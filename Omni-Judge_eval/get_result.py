import json
import pdb
import argparse  # 只是将jsonl转为了list of dict
from collections import defaultdict
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
    with open(args.in_file) as f:
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
                target_entry.append({'source': entry['source'], 'domain': entry['domain'], 'difficulty': entry['difficulty'], 'question': entry['problem'], 'answer': entry['answer'], 'model_generation': entry['model_generation'], 'correctness': True})
            else:
                target_entry.append({'source': entry['source'], 'domain': entry['domain'], 'difficulty': entry['difficulty'], 'question': entry['problem'], 'answer': entry['answer'], 'model_generation': entry['model_generation'], 'correctness': False})
        except:
            continue
    

    # 读取jsonl文件并将数据按difficulty分组
    grouped_data = defaultdict(list)
    for line in target_entry:
        difficulty = line['difficulty']
        correctness = line['correctness']
        grouped_data[difficulty].append(correctness)

    # 计算每个difficulty组的准确率
    accuracy_by_difficulty = {}
    tot_acc = 0
    tot_len = 0
    for difficulty, correctness_list in grouped_data.items():
        total_questions = len(correctness_list)
        tot_len += total_questions
        correct_answers = correctness_list.count(True)
        tot_acc += correct_answers
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        if len(correctness_list) > 10:
            accuracy_by_difficulty[difficulty] = accuracy

    print('Total Accuracy:{}'.format(tot_acc / tot_len))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="llm gen")
    parser.add_argument("-i", "--in-file", type=str)
    parser.add_argument("-o", "--out-file", type=str)
    args = parser.parse_args()
    main(args)