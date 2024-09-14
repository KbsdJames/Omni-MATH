import json
import pdb
import argparse

def main(args):
    data = []
    with open(args.input_file) as f:
        for line in f.readlines():
            data.append(json.loads(line))

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

    difficulty_1_3 = []
    difficulty_3_5 = []
    difficulty_5_7 = []
    difficulty_7_10 = []


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

    for line in target_entry:
        if line['difficulty'] >= 1 and line['difficulty'] <= 3:
            difficulty_1_3.append(line)
        elif line['difficulty'] > 3 and line['difficulty'] <= 5:
            difficulty_3_5.append(line)
        elif line['difficulty'] > 5 and line['difficulty'] <= 8:
            difficulty_5_7.append(line)
        elif line['difficulty'] > 8 and line['difficulty'] <= 10:
            difficulty_7_10.append(line)


    cnt = 0
    acc = 0
    for line in difficulty_1_3:
        if line['correctness'] == True:
            acc += 1
        cnt += 1
    if cnt != 0:
        print('difficulty_1_3: {}'.format(acc / cnt))

    cnt = 0
    acc = 0
    for line in difficulty_3_5:
        if line['correctness'] == True:
            acc += 1
        cnt += 1

    if cnt != 0:
        print('difficulty_3_5: {}'.format(acc / cnt))

    cnt = 0
    acc = 0
    for line in difficulty_5_7:
        if line['correctness'] == True:
            acc += 1
        cnt += 1

    print('difficulty_5_7: {}'.format(acc / cnt))

    cnt = 0
    acc = 0
    for line in difficulty_7_10:
        if 'prove' in line['problem'].lower() or 'proof' in line['problem'].lower():
            continue
        if line['correctness'] == True:
            acc += 1
        cnt += 1

    if cnt != 0:
        print('difficulty_7_10: {}'.format(acc / cnt))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str)  # input path
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(args)