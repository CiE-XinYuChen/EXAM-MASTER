#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import csv
import os

def parse_question_block(lines, start_idx):
    """解析一个题目块，返回题目信息和下一个题目的起始位置"""
    question_info = {
        'question': '',
        'options': {'A': '', 'B': '', 'C': '', 'D': '', 'E': ''},
        'answer': '',
        'question_type': '单选题'  # 默认单选
    }
    
    i = start_idx
    
    # 解析题目（第一行）
    if i < len(lines):
        # 提取题号和题干
        line = lines[i].strip()
        match = re.match(r'^(\d+)\.(.+)', line)
        if match:
            question_info['question'] = match.group(2).strip()
        i += 1
    
    # 解析选项
    while i < len(lines):
        line = lines[i].strip()
        
        # 检查是否是答案行
        if line.startswith('【答案】'):
            answer = line.replace('【答案】', '').strip()
            question_info['answer'] = answer
            
            # 判断题型：如果答案包含多个字母，则为多选题
            if len(answer) > 1:
                question_info['question_type'] = '多选题'
            
            i += 1
            break
        
        # 解析选项
        option_match = re.match(r'^([A-E])\.(.+)', line)
        if option_match:
            option_letter = option_match.group(1)
            option_text = option_match.group(2).strip()
            question_info['options'][option_letter] = option_text
        
        i += 1
    
    return question_info, i

def convert_txt_to_csv(txt_file, csv_file):
    """将txt文件转换为CSV格式"""
    
    # 读取txt文件
    with open(txt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    questions = []
    
    i = 0
    question_num = 1
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 跳过空行
        if not line:
            i += 1
            continue
        
        # 查找题目开始（以数字+点开始）
        if re.match(r'^\d+\.', line):
            question_info, next_i = parse_question_block(lines, i)
            
            if question_info['question'] and question_info['answer']:
                # 构建CSV行
                csv_row = [
                    str(question_num),  # 题号
                    question_info['question'],  # 题干
                    question_info['options']['A'],  # A选项
                    question_info['options']['B'],  # B选项
                    question_info['options']['C'],  # C选项
                    question_info['options']['D'],  # D选项
                    question_info['options']['E'],  # E选项
                    question_info['answer'],  # 答案
                    '无',  # 难度
                    question_info['question_type']  # 题型
                ]
                questions.append(csv_row)
                question_num += 1
            
            i = next_i
        else:
            i += 1
    
    # 写入CSV文件
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(['题号', '题干', 'A', 'B', 'C', 'D', 'E', '答案', '难度', '题型'])
        # 写入题目数据
        writer.writerows(questions)
    
    print(f"转换完成！共转换 {len(questions)} 道题目")
    print(f"输出文件：{csv_file}")

if __name__ == "__main__":
    txt_file = "questions_202505共同体概论.txt"
    csv_file = "questions_202505共同体概论.csv"
    
    if os.path.exists(txt_file):
        convert_txt_to_csv(txt_file, csv_file)
    else:
        print(f"错误：找不到文件 {txt_file}")