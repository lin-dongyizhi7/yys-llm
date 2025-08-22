import argparse
from pathlib import Path
import json
import sys

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
)
from peft import LoraConfig, TaskType, get_peft_model
from trl import SFTTrainer

# 修正导入路径，兼容直接 python 执行
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from utils.roles import add_or_update_role  # noqa: E402


def build_lora_config():
    return LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],
    )


def load_tokenizer(base_model: str):
    tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    return tokenizer


def format_dataset(dataset_path: str):
    # dataset 是 jsonl，每行包含 role 和 dialog
    def to_text(example):
        dialog = example["dialog"]
        # 将多轮拼接为 SFT 文本，加入少量表情增强风格 😀
        lines = []
        for turn in dialog:
            speaker = "用户" if turn["from"] == "user" else "助手"
            text = turn["text"].strip()
            if turn["from"] == "assistant":
                text = text + " 😊"
            lines.append(f"{speaker}: {text}")
        return {"text": "\n".join(lines)}

    ds = load_dataset("json", data_files=dataset_path, split="train")
    ds = ds.map(to_text)
    return ds


def pick_precision_flags() -> dict:
    if not torch.cuda.is_available():
        return {"fp16": False, "bf16": False}
    major, _ = torch.cuda.get_device_capability(0)
    if major >= 8:  # Ampere 及以上支持 bf16
        return {"fp16": False, "bf16": True}
    return {"fp16": True, "bf16": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--cutoff_len", type=int, default=2048)
    parser.add_argument("--quant", choices=["none", "4bit", "8bit"], default="4bit")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    load_kwargs = {}
    if args.quant == "4bit":
        load_kwargs.update(dict(load_in_4bit=True, device_map="auto"))
    elif args.quant == "8bit":
        load_kwargs.update(dict(load_in_8bit=True, device_map="auto"))
    else:
        load_kwargs.update(dict(device_map="auto"))

    tokenizer = load_tokenizer(args.base_model)
    model = AutoModelForCausalLM.from_pretrained(args.base_model, torch_dtype=torch_dtype, **load_kwargs)

    lora_config = build_lora_config()
    model = get_peft_model(model, lora_config)

    train_dataset = format_dataset(args.dataset)

    prec = pick_precision_flags()

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        learning_rate=args.lr,
        fp16=prec["fp16"],
        bf16=prec["bf16"],
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="no",
        gradient_accumulation_steps=1,
        report_to=[],
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        dataset_text_field="text",
        max_seq_length=args.cutoff_len,
        args=training_args,
    )

    trainer.train()
    trainer.model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    add_or_update_role(args.role, args.base_model, str(output_dir))

    (output_dir / "meta.json").write_text(json.dumps({
        "role": args.role,
        "base_model": args.base_model,
        "quant": args.quant
    }, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
