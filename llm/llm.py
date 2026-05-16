import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

from config import CACHE_DIR
from cache_store import _MODEL_CACHE

def load_llm(model_choice, model_map, quantization):
    key = f"{model_choice}_{quantization}"

    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]
    
    model_name = model_map.get(model_choice, model_map["mistral"])
    
    # Optimization: Use bfloat16 if hardware supports it
    compute_dtype = torch.float16
    # compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

    if quantization:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            quantization_config=quant_config,
            low_cpu_mem_usage=True,
            cache_dir=CACHE_DIR
        )

    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            dtype=torch.float16,
            cache_dir=CACHE_DIR
        )

    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=CACHE_DIR)
    
    # Avoid tokenizer complaints
    tokenizer.padding_side = "left"

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model.config.pad_token_id = tokenizer.pad_token_id
    model.generation_config.pad_token_id = tokenizer.pad_token_id
    model.generation_config.eos_token_id = tokenizer.eos_token_id

    llm = {
        "model": model,
        "tokenizer": tokenizer
    }

    _MODEL_CACHE[key] = llm
    
    return llm