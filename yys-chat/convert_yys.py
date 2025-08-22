'''
Author: 凛冬已至 2985956026@qq.com
Date: 2025-08-22 13:36:15
LastEditors: 凛冬已至 2985956026@qq.com
LastEditTime: 2025-08-22 13:40:28
FilePath: \my-llm\yys-chat\convert_yys.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import json
import codecs
from pathlib import Path

def convert_yys_to_jsonl():
    # 读取源文件
    input_file = Path("data/yys/yr_dev.json")
    output_file = Path("data/yys/dev.jsonl")
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 尝试不同的编码方式读取文件
    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
    data = None
    
    for encoding in encodings:
        try:
            with codecs.open(input_file, 'r', encoding=encoding) as f:
                data = json.load(f)
            print(f"成功使用 {encoding} 编码读取文件")
            break
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            print(f"使用 {encoding} 编码失败: {e}")
            continue
    
    if data is None:
        print("无法读取文件，请检查文件编码")
        return
    
    # 转换为 JSONL 格式
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            # 确保每个项目都有正确的格式
            if 'role' in item and 'dialog' in item:
                # 验证对话格式
                if isinstance(item['dialog'], list) and len(item['dialog']) >= 2:
                    # 检查是否以 user 开始，assistant 结束
                    if (item['dialog'][0].get('from') == 'user' and 
                        item['dialog'][-1].get('from') == 'assistant'):
                        # 写入 JSONL 格式
                        json.dump(item, f, ensure_ascii=False)
                        f.write('\n')
                    else:
                        print(f"跳过格式不正确的对话: {item.get('role', 'Unknown')}")
                else:
                    print(f"跳过对话长度不足的项目: {item.get('role', 'Unknown')}")
            else:
                print(f"跳过格式不正确的项目: {item}")
    
    print(f"转换完成！输出文件: {output_file}")
    print(f"共处理 {len(data)} 个项目")

if __name__ == "__main__":
    convert_yys_to_jsonl()
