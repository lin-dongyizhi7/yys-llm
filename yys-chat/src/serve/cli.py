import argparse
from typing import List, Tuple
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

from ..utils.roles import list_roles, get_role


def load_model(role_name: str):
    role = get_role(role_name)
    base_model = role["base_model"]
    adapter_path = role["adapter_path"]

    tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
    )
    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()
    return tokenizer, model


def generate(model_tuple, history: List[Tuple[str, str]], message: str) -> str:
    tokenizer, model = model_tuple
    texts = []
    for u, a in history:
        texts.append(f"用户: {u}")
        texts.append(f"助手: {a}")
    texts.append(f"用户: {message}")
    prompt = "\n".join(texts) + "\n助手:"

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.8,
            top_p=0.9,
            do_sample=True,
            eos_token_id=tokenizer.eos_token_id,
        )
    resp = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    return resp.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", type=str, default=None)
    args = parser.parse_args()

    roles = [r["name"] for r in list_roles()]
    if not roles:
        print("未发现已训练角色，请先训练一个角色。")
        return

    role = args.role or roles[0]
    tokenizer_model = load_model(role)

    history: List[Tuple[str, str]] = []
    print(f"进入对话，当前角色: {role}，输入 exit 退出。\n")
    while True:
        try:
            user = input("你: ").strip()
        except EOFError:
            break
        if user.lower() in {"exit", "quit"}:
            break
        if not user:
            continue
        answer = generate(tokenizer_model, history, user)
        history.append((user, answer))
        print(f"{role}: {answer}")


if __name__ == "__main__":
    main()
