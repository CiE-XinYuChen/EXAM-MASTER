#!/usr/bin/env python3
# txt2csv.py
"""
将 “题干 + 选项 + \\ans:答案” 的题库 TXT 转成
题号,题干,A,B,C,D,E,答案,难度,题型 的 CSV。

用法：
    python txt2csv.py  input.txt  [output.csv]

若不指定输出文件，默认生成 output.csv
"""

import argparse
import csv
import re
from pathlib import Path


def parse_file(text: str):
    """
    把整份文本拆成若干“题目块”（遇到 \ans: 即分块）
    返回由行列表组成的 list。
    """
    block, blocks = [], []
    for line in text.splitlines():
        line = line.rstrip("\n")
        block.append(line)
        if r"\ans:" in line:        # 题目结束
            blocks.append(block)
            block = []
    # 若最后一题后面没有换行，也要记得收集
    if block:
        blocks.append(block)
    return blocks


def parse_block(block, index):
    """
    把单个“题目块”拆成字段。
    返回 dict，字段与 CSV 列对应。
    """
    row = {
        "题号": index,
        "题干": "",
        "A": "", "B": "", "C": "", "D": "", "E": "",
        "答案": "",
        "难度": "无",
        "题型": "",
    }

    # 第一行一定是题干
    row["题干"] = block[0].strip()

    # 正则匹配形如 “A 文本”
    opt_pat = re.compile(r"^\s*([A-E])\s+(.*)$")

    for line in block[1:]:
        if r"\ans:" in line:
            # 可能形如 “D 选项文本\ans:ABC” —— D 与答案在同一行
            before, after = line.split(r"\ans:", 1)
            before = before.strip()
            if before:  # 把最后一个选项补上
                m = opt_pat.match(before)
                if m:
                    row[m.group(1)] = m.group(2).strip()
            row["答案"] = after.strip()
        else:
            m = opt_pat.match(line)
            if m:
                row[m.group(1)] = m.group(2).strip()

    # 判断题型
    row["题型"] = "单选题" if len(row["答案"]) == 1 else "多选题"
    return row


def txt_to_csv(inp: Path, out: Path):
    blocks = parse_file(inp.read_text(encoding="utf-8"))
    rows = [parse_block(b, i + 1) for i, b in enumerate(blocks)]

    with out.open("w", newline="", encoding="utf-8-sig") as f:  # 带 BOM，方便 Excel
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["题号", "题干", "A", "B", "C", "D", "E",
                         "答案", "难度", "题型"])
        for r in rows:
            writer.writerow([r[k] for k in
                             ("题号", "题干", "A", "B", "C", "D", "E",
                              "答案", "难度", "题型")])
    print(f"✅ 已生成 {out}")


def main():
    ap = argparse.ArgumentParser(description="TXT 题库 ➜ CSV")
    ap.add_argument("input", help="源 TXT 文件")
    ap.add_argument("output", nargs="?", default="output.csv",
                    help="目标 CSV 文件（默认 output.csv）")
    args = ap.parse_args()

    txt_to_csv(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
