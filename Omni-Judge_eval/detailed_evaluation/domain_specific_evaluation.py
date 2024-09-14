import json
import pdb
import argparse
from prettytable import PrettyTable
from collections import defaultdict

def update_domain(target_entry):
    cnt = 0
    data_1 = []
    with open('/mnt/workspace/hard_math/OmniPic_Bench/OmniPic_Bench_v1_final.jsonl') as f:
        for line in f.readlines():
            data_1.append(json.loads(line))

    # 创建一个字典以便快速查找第一份数据
    first_dict = {item['problem']: item['domain'] for item in data_1}

    # 更新第二份数据中的 domain
    for item in target_entry:
        problem = item['problem']
        if problem in first_dict:
            item['domain'] = first_dict[problem]
        else:
            continue
    return target_entry

def parse_report(report):
    parts = report.split("## ")
    data = {}
    
    for part in parts[1:]:  # 从第一个部分开始
        lines = part.strip().split("\n")
        title = lines[0].strip()  # 第一行是标题
        content = "\n".join(lines[1:]).strip()  # 剩余的内容合并
        
        if title == "Justification":
            # Justification 可能有多行，直接存储所有内容
            data[title] = content
        else:
            # 只取第一行的内容
            data[title] = lines[1].strip() if len(lines) > 1 else ''
    
    return data

def main(args):
    data = []
    with open(args.input_file) as f:
        for line in f.readlines():
            data.append(json.loads(line))
    
    # 处理 JSON 数据
    target_entry = []
    for entry in data:
        omni_eval = entry['omni_judge']
        info = parse_report(omni_eval)
        if info == {}:
            continue
        try:
            correctness = info['Equivalence Judgement']
            if correctness == 'TRUE':
                target_entry.append({'source': entry['source'], 'domain': entry['domain'], 'difficulty': entry['difficulty'], 'problem': entry['problem'], 'answer': entry['answer'], 'model_generation': entry['model_generation'], 'correctness': True})
            else:
                target_entry.append({'source': entry['source'], 'domain': entry['domain'], 'difficulty': entry['difficulty'], 'problem': entry['problem'], 'answer': entry['answer'], 'model_generation': entry['model_generation'], 'correctness': False})
        except:
            continue
    
    target_entry = update_domain(target_entry)

    domain_acc_dict = {}
    for line in target_entry:
        for domain_chain in line['domain']:
            if domain_chain in domain_acc_dict:
                a, t = domain_acc_dict[domain_chain]
                if line['correctness'] == True:
                    domain_acc_dict[domain_chain] = (a+1, t+1)
                else:
                    domain_acc_dict[domain_chain] = (a, t+1)
            else:
                if line['correctness'] == True:
                    domain_acc_dict[domain_chain] = (1, 1)
                else:
                    domain_acc_dict[domain_chain] = (0, 1)

    domain_summary = {}

    # 解析源数据
    for key, (correct, total) in domain_acc_dict.items():
        parts = key.split(" -> ")
        
        # 递归更新准确率
        current = domain_summary
        for part in parts:
            if part not in current.keys():
                current[part] = {'correct': correct, 'total': total}
            else:
                current[part]['correct'] += correct
                current[part]['total'] += total
            
            current = current[part]
    
    # 准备PrettyTable
    table = PrettyTable()
    table.field_names = ["Domain", "Accuracy (Positive / Total)"]

    # 计算主领域的准确率
    main_correct = domain_summary['Mathematics']['correct']
    main_total = domain_summary['Mathematics']['total']

    # 计算主领域的准确率并加入表格
    if main_total > 0:
        main_accuracy = (main_correct / main_total) * 100
    else:
        main_accuracy = 0

    # 子领域信息
    for sub_domain, values in domain_summary['Mathematics'].items():
        if sub_domain in ['correct', 'total']:
            continue  # 跳过主领域的正确率和总数
        
        sub_correct = values['correct']
        sub_total = values['total']
        
        if sub_total > 0:
            sub_accuracy = (sub_correct / sub_total) * 100
        else:
            sub_accuracy = 0
        
        # 子领域信息
        sub_accuracy_info = f"{sub_accuracy:.2f}% ({sub_correct}/{sub_total})"
        
        # 添加到表格的子领域的准确率信息
        table.add_row([sub_domain, sub_accuracy_info])

    # 显示表格
    print(table)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str)  # input path
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(args)