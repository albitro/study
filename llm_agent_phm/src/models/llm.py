from dataclasses import dataclass
from typing import Any

import torch


@dataclass
class LLMConfig:
    model_id: str = "Qwen/Qwen2.5-7B-Instruct"
    quantization: str = "int4"
    device_map: str = "auto"
    max_new_tokens: int = 512
    temperature: float = 0.2
    top_p: float = 0.9
    do_sample: bool = True


def _bnb_config(quantization: str):
    from transformers import BitsAndBytesConfig

    if quantization == "int4":
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
    if quantization == "int8":
        return BitsAndBytesConfig(load_in_8bit=True)
    return None


def load_hf_model(cfg: LLMConfig | None = None) -> tuple[Any, Any]:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    cfg = cfg or LLMConfig()
    bnb = _bnb_config(cfg.quantization)

    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id, trust_remote_code=True)
    kwargs: dict[str, Any] = {"trust_remote_code": True, "device_map": cfg.device_map}
    if bnb is not None:
        kwargs["quantization_config"] = bnb
    else:
        kwargs["torch_dtype"] = torch.float16
    model = AutoModelForCausalLM.from_pretrained(cfg.model_id, **kwargs)
    return model, tokenizer


def make_chat_pipeline(cfg: LLMConfig | None = None):
    from transformers import pipeline

    cfg = cfg or LLMConfig()
    model, tok = load_hf_model(cfg)
    return pipeline(
        "text-generation",
        model=model,
        tokenizer=tok,
        max_new_tokens=cfg.max_new_tokens,
        temperature=cfg.temperature,
        top_p=cfg.top_p,
        do_sample=cfg.do_sample,
        return_full_text=False,
    )


def make_chat_model(cfg: LLMConfig | None = None):
    from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

    pipe = make_chat_pipeline(cfg)
    hf_pipe = HuggingFacePipeline(pipeline=pipe)
    return ChatHuggingFace(llm=hf_pipe, model_id=(cfg or LLMConfig()).model_id)


def chat(
    messages: list[dict],
    model,
    tokenizer,
    max_new_tokens: int = 512,
    temperature: float = 0.2,
) -> str:
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = out[0][inputs.input_ids.shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
