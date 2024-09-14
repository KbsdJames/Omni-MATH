import json
import pdb

sample = []
with open('./meta_llama_3-1_70b_instruct_gpteval.jsonl') as f:
    for line in f.readlines():
        sample.append(json.loads(line))

sample_in = []
for line in sample:
    original_json = json.loads(line['original_json'])
    sample_in.append({'domain': original_json['domain'], 'difficulty': original_json['difficulty'], \
        'problem': original_json['problem'], 'solution': original_json['solution'], 'answer': original_json['answer'], \
        'source': original_json['source'], 'model_generation': original_json['model_generation']})


with open('./meta_llama_3-1_70b_infile.jsonl', 'w') as f:
    for line in sample_in:
        f.write(json.dumps(line) + '\n')

