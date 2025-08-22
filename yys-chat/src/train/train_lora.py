import argparse
from pathlib import Path
import json
import sys
import time
import psutil
import logging
from datetime import datetime

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    get_linear_schedule_with_warmup,
)
from peft import LoraConfig, TaskType, get_peft_model
from trl import SFTTrainer

# 修正导入路径，兼容直接 python 执行
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from utils.roles import add_or_update_role  # noqa: E402

# 配置日志
def setup_logging(output_dir: Path):
    """设置详细的日志记录"""
    log_file = output_dir / "training.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def log_system_info(logger):
    """记录系统信息"""
    logger.info("=" * 60)
    logger.info("训练开始 - 系统信息")
    logger.info("=" * 60)
    
    # Python 和 PyTorch 版本
    logger.info(f"Python 版本: {sys.version}")
    logger.info(f"PyTorch 版本: {torch.__version__}")
    logger.info(f"CUDA 可用: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        logger.info(f"CUDA 版本: {torch.version.cuda}")
        logger.info(f"GPU 数量: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            logger.info(f"GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
    
    # 系统内存
    memory = psutil.virtual_memory()
    logger.info(f"系统内存: {memory.total / 1024**3:.1f} GB")
    logger.info(f"可用内存: {memory.available / 1024**3:.1f} GB")
    logger.info("=" * 60)

def log_model_info(model, tokenizer, logger):
    """记录模型信息"""
    logger.info("模型信息:")
    logger.info(f"  基础模型: {type(model).__name__}")
    logger.info(f"  词表大小: {tokenizer.vocab_size}")
    logger.info(f"  最大长度: {tokenizer.model_max_length}")
    
    # 计算模型参数
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"  总参数: {total_params:,}")
    logger.info(f"  可训练参数: {trainable_params:,}")
    logger.info(f"  参数压缩比: {trainable_params/total_params*100:.2f}%")
    
    # LoRA 配置信息
    if hasattr(model, 'peft_config'):
        for name, config in model.peft_config.items():
            logger.info(f"  LoRA 配置 {name}:")
            logger.info(f"    r: {config.r}")
            logger.info(f"    alpha: {config.lora_alpha}")
            logger.info(f"    dropout: {config.lora_dropout}")
            logger.info(f"    target_modules: {config.target_modules}")

def build_lora_config():
    return LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],
    )

def load_tokenizer(base_model: str, logger):
    logger.info(f"正在加载分词器: {base_model}")
    tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        logger.info("设置 pad_token = eos_token")
    tokenizer.padding_side = "right"
    logger.info("分词器加载完成")
    return tokenizer

def format_dataset(dataset_path: str, logger):
    logger.info(f"正在加载数据集: {dataset_path}")
    
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
    logger.info(f"原始数据集大小: {len(ds)} 个样本")
    
    ds = ds.map(to_text)
    logger.info("数据集格式化完成")
    
    # 统计文本长度
    text_lengths = [len(item["text"]) for item in ds]
    avg_length = sum(text_lengths) / len(text_lengths)
    max_length = max(text_lengths)
    min_length = min(text_lengths)
    logger.info(f"文本长度统计:")
    logger.info(f"  平均长度: {avg_length:.1f} 字符")
    logger.info(f"  最大长度: {max_length} 字符")
    logger.info(f"  最小长度: {min_length} 字符")
    
    return ds

def pick_precision_flags(logger):
    if not torch.cuda.is_available():
        logger.info("CUDA 不可用，使用 CPU 训练")
        return {"fp16": False, "bf16": False}
    
    major, _ = torch.cuda.get_device_capability(0)
    if major >= 8:  # Ampere 及以上支持 bf16
        logger.info("使用 bfloat16 精度 (Ampere+ GPU)")
        return {"fp16": False, "bf16": True}
    
    logger.info("使用 float16 精度")
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
    
    # 设置日志
    logger = setup_logging(output_dir)
    
    # 记录训练参数
    logger.info("训练参数:")
    for key, value in vars(args).items():
        logger.info(f"  {key}: {value}")
    
    # 记录系统信息
    log_system_info(logger)
    
    start_time = time.time()
    
    torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    logger.info(f"使用数据类型: {torch_dtype}")

    load_kwargs = {}
    if args.quant == "4bit":
        load_kwargs.update(dict(load_in_4bit=True, device_map="auto"))
        logger.info("使用 4bit 量化 (QLoRA)")
    elif args.quant == "8bit":
        load_kwargs.update(dict(load_in_8bit=True, device_map="auto"))
        logger.info("使用 8bit 量化")
    else:
        load_kwargs.update(dict(device_map="auto"))
        logger.info("不使用量化")

    # 加载分词器
    tokenizer = load_tokenizer(args.base_model, logger)
    
    # 加载模型
    logger.info(f"正在加载基础模型: {args.base_model}")
    model = AutoModelForCausalLM.from_pretrained(args.base_model, torch_dtype=torch_dtype, **load_kwargs)
    logger.info("基础模型加载完成")

    # 应用 LoRA 配置
    logger.info("正在应用 LoRA 配置...")
    lora_config = build_lora_config()
    model = get_peft_model(model, lora_config)
    logger.info("LoRA 配置应用完成")
    
    # 记录模型信息
    log_model_info(model, tokenizer, logger)

    # 加载和格式化数据集
    train_dataset = format_dataset(args.dataset, logger)

    # 选择精度设置
    prec = pick_precision_flags(logger)

    # 计算训练步数
    total_steps = len(train_dataset) // args.batch_size * args.epochs
    warmup_steps = int(total_steps * 0.1)  # 10% 的步数用于 warmup
    
    logger.info(f"训练配置:")
    logger.info(f"  总步数: {total_steps}")
    logger.info(f"  Warmup 步数: {warmup_steps}")
    logger.info(f"  每 epoch 步数: {total_steps // args.epochs}")

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        learning_rate=args.lr,
        fp16=prec["fp16"],
        bf16=prec["bf16"],
        logging_steps=1,  # 每步都记录
        save_strategy="epoch",
        evaluation_strategy="no",
        gradient_accumulation_steps=1,
        report_to=[],
        remove_unused_columns=False,
        dataloader_pin_memory=False,
        dataloader_num_workers=0,
        warmup_steps=warmup_steps,
        lr_scheduler_type="linear",
        logging_dir=str(output_dir / "logs"),
        run_name=f"yys-{args.role}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    )

    # 创建训练器
    logger.info("正在创建训练器...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        dataset_text_field="text",
        max_seq_length=args.cutoff_len,
        args=training_args,
    )
    logger.info("训练器创建完成")

    # 开始训练
    logger.info("=" * 60)
    logger.info("开始训练!")
    logger.info("=" * 60)
    
    try:
        trainer.train()
        logger.info("训练完成!")
    except Exception as e:
        logger.error(f"训练过程中出现错误: {e}")
        raise
    
    # 保存模型
    logger.info("正在保存模型...")
    trainer.model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    logger.info("模型保存完成")

    # 记录角色信息
    add_or_update_role(args.role, args.base_model, str(output_dir))
    logger.info(f"角色 '{args.role}' 已注册")

    # 保存训练元数据
    meta_data = {
        "role": args.role,
        "base_model": args.base_model,
        "quant": args.quant,
        "training_args": vars(training_args),
        "dataset_info": {
            "path": args.dataset,
            "size": len(train_dataset),
            "cutoff_len": args.cutoff_len
        },
        "training_time": time.time() - start_time,
        "completed_at": datetime.now().isoformat()
    }
    
    meta_file = output_dir / "meta.json"
    meta_file.write_text(json.dumps(meta_data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"训练元数据已保存到: {meta_file}")

    # 最终统计
    total_time = time.time() - start_time
    logger.info("=" * 60)
    logger.info("训练完成总结")
    logger.info("=" * 60)
    logger.info(f"总训练时间: {total_time/3600:.2f} 小时 ({total_time/60:.1f} 分钟)")
    logger.info(f"输出目录: {output_dir}")
    logger.info(f"角色名称: {args.role}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
