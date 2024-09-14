INFILE="/cpfs01/shared/public/gaobofei.gbf/hard_math/Omni-MATH/GPT_eval/examples/meta_llama_3-1_70b_instruct_gpteval.jsonl"

python get_result.py \
    -i $INFILE \

python3 ./detailed_evaluation/domain_specific_evaluation.py \
    --input_file $INFILE \

python3 ./detailed_evaluation/difficulty_specific_evaluation.py \
    --input_file $INFILE \