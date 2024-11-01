from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
import argparse
import json

def get_batch_responses(
    questions,
    reference_answers,
    student_solutions,
    tokenizer,
    model ,
    terminators,
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

    sampling_params = SamplingParams(
        n=1,
        stop=terminators,
        max_tokens=max_new_tokens,
        temperature=0,
    )

    responses = []
    batch_outputs = model.generate(
        contexts,
        sampling_params=sampling_params,
    )
    for output in batch_outputs:
        response = output.outputs[0].text
        responses.append(
            "## Student Final Answer\n" + response.strip()
        )

    return responses


def main(args):
    model = LLM(
        model=args.model_path, 
        tensor_parallel_size=args.tensor_parallel_size,
        trust_remote_code=True,
        enable_prefix_caching=True
    )

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path,
        trust_remote_code=True,
        use_fast=True
    )

    # set terminators for decoding
    terminators = [
        tokenizer.eos_token,
        "<|eot_id|>",
    ]

    inputs = []
    with open(args.in_file) as f:
        for line in f.readlines():
            inputs.append(json.loads(line))

    questions = [d['problem'] for d in inputs]
    reference_answers = [d['answer'] for d in inputs]
    student_solutions = [d['model_generation'] for d in inputs]
    omni_judge_result = get_batch_responses(
        questions, 
        reference_answers, 
        student_solutions, 
        tokenizer, 
        model, 
        terminators
    )
    
    with open(args.out_file, 'w') as f:
        for (q, r, s, o, d) in zip(questions, reference_answers, student_solutions, omni_judge_result, inputs):
            f.write(json.dumps({'domain': d['domain'], 'difficulty':d['difficulty'], 'source':d['source'],\
                 'problem': q, 'answer': r, 'model_generation':s, 'omni_judge': o}) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Omni-Judge")
    parser.add_argument("-i", "--in-file", type=str)
    parser.add_argument("-m", "--model-path", type=str)
    parser.add_argument("-o", "--out-file", type=str)
    parser.add_argument("--tensor_parallel_size", type=int, default=1)

    args = parser.parse_args()
    main(args)