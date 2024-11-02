export CUDA_VISIBLE_DEVICES=0

OUTFILE=""

python3 omni_judge_vllm.py \
    -i in_file.jsonl \
    -o  $OUTFILE \
    -m ./Omni_Judge_Model



python3 get_result.py \
    -i $OUTFILE \

python3 ./detailed_evaluation/domain_specific_evaluation.py \
    --input_file $OUTFILE \

python3 ./detailed_evaluation/difficulty_specific_evaluation.py \
    --input_file $OUTFILE \