INFILE="./examples/meta_llama_3-1_70b_instruct_gpteval.jsonl"

python3 get_result.py \
    -i $INFILE \

python3 ./detailed_evaluation/domain_specific_evaluation.py \
    --input_file $INFILE \

python3 ./detailed_evaluation/difficulty_specific_evaluation.py \
    --input_file $INFILE \