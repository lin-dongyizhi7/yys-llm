import argparse
import json
from pathlib import Path
from typing import List, Dict
import random
from rich import print


def read_jsonl(path: Path) -> List[Dict]:
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def validate_dialog(item: Dict) -> bool:
    if "role" not in item or "dialog" not in item:
        return False
    if not isinstance(item["dialog"], list) or len(item["dialog"]) < 2:
        return False
    for turn in item["dialog"]:
        if turn.get("from") not in {"user", "assistant"}:
            return False
        if not isinstance(turn.get("text"), str) or len(turn["text"]) == 0:
            return False
    # 必须以 user 开始，assistant 结束
    if item["dialog"][0].get("from") != "user" or item["dialog"][-1].get("from") != "assistant":
        return False
    return True


def split_train_val(items: List[Dict], val_ratio: float) -> (List[Dict], List[Dict]):
    random.shuffle(items)
    n_val = max(1, int(len(items) * val_ratio)) if len(items) > 10 else 1
    return items[n_val:], items[:n_val]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--val_ratio", type=float, default=0.02)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    items = read_jsonl(input_path)
    items = [x for x in items if validate_dialog(x) and x.get("role") == args.role]

    if len(items) == 0:
        raise ValueError("没有有效样本，请检查 role 与数据格式")

    train, val = split_train_val(items, args.val_ratio)

    # 写入训练文件（仍使用 jsonl）
    def write_jsonl(path: Path, data: List[Dict]):
        with path.open("w", encoding="utf-8") as f:
            for x in data:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")

    write_jsonl(output_path, train)
    val_out = output_path.with_suffix("")
    val_out = val_out.parent / (val_out.name + "_val.jsonl")
    write_jsonl(val_out, val)

    print(f"[green]OK[/green] 训练:{len(train)} 验证:{len(val)} -> {output_path} / {val_out}")


if __name__ == "__main__":
    main()
