import argparse
from typing import List, Tuple
from pathlib import Path
import sys

import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from utils.roles import list_roles, get_role  # noqa: E402


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


def chat(model_tuple, history: List[Tuple[str, str]], message: str, add_emoji: bool):
    tokenizer, model = model_tuple
    if message.strip() == "":
        return history, ""

    # 将历史构造成 prompt
    texts = []
    for user, assistant in history:
        texts.append(f"用户: {user}")
        texts.append(f"助手: {assistant}")
    texts.append(f"用户: {message}")
    prompt = "\n".join(texts) + "\n助手:"

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=128,
            temperature=0.8,
            top_p=0.9,
            do_sample=True,
            eos_token_id=tokenizer.eos_token_id,
        )
    resp = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    resp = resp.strip()
    if add_emoji:
        resp = resp + " ✨"

    history = history + [(message, resp)]
    return history, ""


def build_ui():
    all_roles = [r["name"] for r in list_roles()]

    with gr.Blocks(title="yys-chat 角色对话") as demo:
        gr.Markdown("## yys-chat 角色对话 😊 选择一个角色开始聊天")
        with gr.Row():
            role_dd = gr.Dropdown(choices=all_roles, label="角色", value=all_roles[0] if all_roles else None)
            emoji_ck = gr.Checkbox(label="添加表情", value=True)
        chatbot = gr.Chatbot(height=460)
        msg = gr.Textbox(label="输入消息")
        clear = gr.Button("清空")

        state_model = gr.State(value=None)

        def on_role_change(role_name):
            if not role_name:
                return None
            return load_model(role_name)

        role_dd.change(on_role_change, inputs=role_dd, outputs=state_model)

        def on_submit(history, text, add_emoji, model_tuple):
            if model_tuple is None and len(list_roles()) > 0:
                # 默认加载第一个
                model_tuple = load_model(list_roles()[0]["name"])
            return chat(model_tuple, history, text, add_emoji)

        msg.submit(on_submit, inputs=[chatbot, msg, emoji_ck, state_model], outputs=[chatbot, msg])
        clear.click(lambda: ([], ""), None, [chatbot, msg])

    return demo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--share", type=str, default="false")
    args = parser.parse_args()

    demo = build_ui()
    demo.queue().launch(server_port=args.port, share=(args.share.lower() == "true"))


if __name__ == "__main__":
    main()
