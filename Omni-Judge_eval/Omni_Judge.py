import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import argparse
import json
import pdb
from tqdm import tqdm

def get_batch_responses(
    questions,
    reference_answers,
    student_solutions,
    tokenizer,
    model ,
    terminators,
    batch_size = 4,
    max_new_tokens = 300,
):
    contexts = []
    for question, reference_answer, student_solution in zip(
        questions,
        reference_answers,
        student_solutions,
    ):
        # pre-process
        formatted_context = tokenizer.get_context(
            question,
            reference_answer,
            student_solution,
        )
        contexts.append(formatted_context)

    total_pred = []
    total_input_ids = []
    tokenizer.padding_side = "left"

    batch = []
    for index in tqdm(range(len(contexts))):
        batch.append(contexts[index])
        if len(batch) == batch_size or index == len(contexts) - 1:
            # tokenize
            model_inputs = tokenizer(batch, padding=True, return_tensors="pt")
            batch_input_ids = model_inputs["input_ids"].to(model.device)
            batch_attention_mask = model_inputs["attention_mask"].to(model.device)

            with torch.no_grad():
                batch_pred = model.generate(
                    batch_input_ids,
                    attention_mask = batch_attention_mask,
                    do_sample = False,
                    num_return_sequences = 1,
                    max_new_tokens = max_new_tokens,
                ).cpu().tolist()
            
            total_pred.extend(batch_pred)
            total_input_ids.extend(batch_input_ids.cpu().tolist())
            batch = []

    responses = []
    for pred, input_ids in zip(total_pred, total_input_ids):
        # post-process
        assert pred[:len(input_ids)] == input_ids
        pred = pred[len(input_ids):]
        for terminator in terminators:
            if terminator in pred:
                pred = pred[:pred.index(terminator)]
        response = tokenizer.decode(pred, skip_special_tokens=True)
        responses.append(
            "## Student Final Answer\n" + response.strip()
        )

    return responses


def main(args):
    # load the model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path, 
        device_map="auto", 
        torch_dtype=torch.bfloat16, 
    )
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path,
        trust_remote_code=True,
        use_fast=True
    )

    # set terminators for decoding
    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    inputs = []
    with open(args.in_file) as f:
        for line in f.readlines():
            inputs.append(json.loads(line))

    questions = [d['problem'] for d in inputs]
    reference_answers = [d['answer'] for d in inputs]
    student_solutions = [d['model_generation'] for d in inputs]
    omni_judge_result = get_batch_responses(questions, reference_answers, student_solutions, tokenizer, model, terminators)
    
    with open(args.out_file, 'w') as f:
        for (q, r, s, o, d) in zip(questions, reference_answers, student_solutions, omni_judge_result, inputs):
            f.write(json.dumps({'domain': d['domain'], 'difficulty':d['difficulty'], 'source':d['source'],\
                 'problem': q, 'answer': r, 'model_generation':s, 'omni_judge': o}) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Omni-Judge")
    parser.add_argument("-i", "--in-file", type=str)
    parser.add_argument("-m", "--model-path", type=str)
    parser.add_argument("-o", "--out-file", type=str)

    args = parser.parse_args()
    main(args)