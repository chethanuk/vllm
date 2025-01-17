import pytest

from transformers import AutoTokenizer

from vllm.transformers_utils.tokenizer import detokenize_incrementally

TRUTH = [
    "Hello here, this is a simple test",
    "vLLM is a high-throughput and memory-efficient inference and serving engine for LLMs. It is designed to be used in production environments, where inference and serving",
    "我很感谢你的热情"
]
TOKENIZERS = [
    "facebook/opt-125m",
    "gpt2",
    "bigcode/tiny_starcoder_py",
    "EleutherAI/gpt-j-6b",
    "EleutherAI/pythia-70m",
    "bigscience/bloom-560m",
    "mosaicml/mpt-7b",
    "tiiuae/falcon-7b",
    "meta-llama/Llama-2-7b-hf",
    "codellama/CodeLlama-7b-hf",
]


def _run_incremental_decode(tokenizer, all_input_ids):
    decoded_text = ""
    offset = 0
    token_offset = 0
    prev_tokens = None
    for i in range(len(all_input_ids)):
        new_tokens, text, offset, token_offset = detokenize_incrementally(
            tokenizer,
            all_input_ids[:i + 1],
            prev_tokens,
            offset,
            token_offset,
            skip_special_tokens=False)
        decoded_text += text
        if prev_tokens is None:
            prev_tokens = new_tokens
        else:
            prev_tokens += new_tokens
    return decoded_text


@pytest.mark.parametrize("truth", TRUTH)
@pytest.mark.parametrize("tokenizer_id", TOKENIZERS)
def test_decode_streaming(tokenizer_id, truth):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_id)
    all_input_ids = tokenizer(truth, add_special_tokens=False)["input_ids"]

    decoded_text = _run_incremental_decode(tokenizer, all_input_ids)

    assert decoded_text == truth
