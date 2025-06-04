#!/usr/bin/env python3
"""
题库格式化和导入工具

这个脚本可以：
1. 将不同格式的CSV题库统一格式化
2. 去重和数据清洗
3. 导入到数据库中

支持的输入格式：
- 格式1: 目录,题型,题干,正确答案,答案解析,难易度,知识点,选项数,A,B,C,D
- 格式2: "题号","题干","A","B","C","D","","正确答案","类别","题型"

"""

import csv
import json
import sqlite3
import os
import sys
from typing import Dict, List, Any, Optional


class QuestionProcessor:
    def __init__(self):
        self.processed_questions = []
        self.duplicate_count = 0
        self.error_count = 0
        self.seen_stems = set()  # 用于去重
        
    def detect_format(self, first_row: Dict[str, str]) -> str:
        """检测CSV文件格式"""
        columns = set(first_row.keys())
        
        # 处理BOM标记的情况
        clean_columns = set()
        for col in columns:
            clean_col = col.replace('\ufeff', '').strip()
            clean_columns.add(clean_col)
        
        if '题干' in clean_columns and '目录' in clean_columns:
            return "format1"  # 目录,题型,题干,正确答案,答案解析,难易度,知识点,选项数,A,B,C,D
        elif '题号' in clean_columns and len(clean_columns) >= 10:
            return "format2"  # "题号","题干","A","B","C","D","","正确答案","类别","题型"
        else:
            return "unknown"
    
    def clean_column_name(self, column_name: str) -> str:
        """清理列名，去除BOM标记和多余空白"""
        return column_name.replace('\ufeff', '').strip()
    
    def get_column_value(self, row: Dict[str, str], column_name: str) -> str:
        """获取列值，处理BOM标记的列名"""
        # 先尝试直接获取
        if column_name in row:
            return row[column_name]
        
        # 如果直接获取失败，尝试找到带BOM的列名
        for key, value in row.items():
            if self.clean_column_name(key) == column_name:
                return value
        
        return ""
    
    def clean_text(self, text: str) -> str:
        """清理文本，去除多余的空白字符和特殊字符"""
        if not text:
            return ""
        return text.strip().replace('\n', ' ').replace('\r', '')
    
    def process_format1(self, row: Dict[str, str], question_id: int) -> Optional[Dict[str, Any]]:
        """处理格式1: 目录,题型,题干,正确答案,答案解析,难易度,知识点,选项数,A,B,C,D"""
        try:
            stem = self.clean_text(self.get_column_value(row, '题干'))
            if not stem or stem in self.seen_stems:
                if stem in self.seen_stems:
                    self.duplicate_count += 1
                return None
            
            self.seen_stems.add(stem)
            
            # 构建选项
            options = {}
            for opt in ['A', 'B', 'C', 'D', 'E']:
                option_text = self.clean_text(self.get_column_value(row, opt))
                if option_text:
                    options[opt] = option_text
            
            # 处理答案
            answer = self.clean_text(self.get_column_value(row, '正确答案'))
            
            # 处理类别 - 改进后的处理逻辑
            category = self.clean_text(self.get_column_value(row, '目录'))
            if not category:
                # 尝试BOM版本的列名
                for key in row.keys():
                    if '目录' in key:
                        category = self.clean_text(row[key])
                        break
            
            if category:
                # 处理路径格式的类别
                if category.startswith('/'):
                    category = category[1:]  # 去除开头的斜杠
                # 如果有多级路径，取最后一级作为类别
                if '/' in category:
                    category = category.split('/')[-1]
            else:
                category = '未分类'
            
            print(f"第{question_id}题 - 类别: {repr(category)}")  # 调试信息
            
            return {
                'id': str(question_id),
                'stem': stem,
                'answer': answer,
                'difficulty': self.clean_text(self.get_column_value(row, '难易度')) or '无',
                'qtype': self.clean_text(self.get_column_value(row, '题型')),
                'category': category,
                'options': options
            }
            
        except Exception as e:
            print(f"处理第{question_id}题时出错: {e}")
            self.error_count += 1
            return None
    
    def process_format2(self, row: Dict[str, str], question_id: int) -> Optional[Dict[str, Any]]:
        """处理格式2: "题号","题干","A","B","C","D","","正确答案","类别","题型" """
        try:
            stem = self.clean_text(row.get('题干', ''))
            if not stem or stem in self.seen_stems:
                if stem in self.seen_stems:
                    self.duplicate_count += 1
                return None
            
            self.seen_stems.add(stem)
            
            # 构建选项
            options = {}
            for opt in ['A', 'B', 'C', 'D', 'E']:
                option_text = self.clean_text(row.get(opt, ''))
                if option_text:
                    options[opt] = option_text
            
            # 处理答案
            answer = self.clean_text(row.get('正确答案', ''))
            
            return {
                'id': str(question_id),
                'stem': stem,
                'answer': answer,
                'difficulty': self.clean_text(row.get('难度', '无')),
                'qtype': self.clean_text(row.get('题型', '')),
                'category': self.clean_text(row.get('类别', '未分类')),
                'options': options
            }
            
        except Exception as e:
            print(f"处理第{question_id}题时出错: {e}")
            self.error_count += 1
            return None
    
    def process_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """处理CSV文件"""
        print(f"正在处理文件: {file_path}")
        
        # 尝试不同的编码
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    # 先读取第一行判断格式
                    first_line = f.readline().strip()
                    f.seek(0)
                    
                    reader = csv.DictReader(f)
                    
                    # 获取第一行数据判断格式
                    first_row = next(reader, None)
                    if not first_row:
                        print(f"文件 {file_path} 为空")
                        return []
                    
                    format_type = self.detect_format(first_row)
                    print(f"检测到格式类型: {format_type}")
                    
                    if format_type == "unknown":
                        print(f"未知的CSV格式，列名: {list(first_row.keys())}")
                        return []
                    
                    # 重新读取文件处理所有行
                    f.seek(0)
                    reader = csv.DictReader(f)
                    
                    question_id = len(self.processed_questions) + 1
                    
                    for row in reader:
                        if format_type == "format1":
                            question = self.process_format1(row, question_id)
                        else:  # format2
                            question = self.process_format2(row, question_id)
                        
                        if question:
                            self.processed_questions.append(question)
                            question_id += 1
                
                print(f"成功读取文件 {file_path}，编码: {encoding}")
                break
                
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"读取文件 {file_path} 时出错 (编码 {encoding}): {e}")
                continue
        else:
            print(f"无法读取文件 {file_path}，尝试了所有编码")
        
        return self.processed_questions

    def save_formatted_csv(self, output_path: str):
        """保存格式化后的CSV文件 - 标准格式: 题号,题干,A,B,C,D,E,答案,难度,题型"""
        if not self.processed_questions:
            print("没有处理的题目数据")
            return
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            # 标准格式：题号,题干,A,B,C,D,E,答案,难度,题型
            fieldnames = ['题号', '题干', 'A', 'B', 'C', 'D', 'E', '答案', '难度', '题型']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for question in self.processed_questions:
                row = {
                    '题号': question['id'],
                    '题干': question['stem'],
                    '答案': question['answer'],
                    '难度': question['difficulty'],
                    '题型': question['qtype']
                }
                
                # 添加选项 A,B,C,D,E
                for opt in ['A', 'B', 'C', 'D', 'E']:
                    row[opt] = question['options'].get(opt, '')
                
                writer.writerow(row)
        
        print(f"格式化的CSV文件已保存到: {output_path}")
        print(f"使用标准格式: 题号,题干,A,B,C,D,E,答案,难度,题型")

    def import_to_database(self, db_path: str = 'exam_master.db'):
        """导入到数据库"""
        if not self.processed_questions:
            print("没有处理的题目数据")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            # 清空现有题目（可选）
            print("清空现有题目数据...")
            c.execute('DELETE FROM questions')
            
            # 插入新题目
            print("正在插入新题目...")
            for question in self.processed_questions:
                c.execute(
                    """INSERT INTO questions (id, stem, answer, difficulty, qtype, category, options) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        question['id'],
                        question['stem'],
                        question['answer'],
                        question['difficulty'],
                        question['qtype'],
                        question['category'],
                        json.dumps(question['options'], ensure_ascii=False)
                    )
                )
            
            conn.commit()
            conn.close()
            
            print(f"成功导入 {len(self.processed_questions)} 道题目到数据库")
            
        except Exception as e:
            print(f"数据库导入失败: {e}")

    def print_statistics(self):
        """打印统计信息"""
        print("\n=== 处理统计 ===")
        print(f"总共处理题目: {len(self.processed_questions)}")
        print(f"去重题目数量: {self.duplicate_count}")
        print(f"错误题目数量: {self.error_count}")
        print(f"有效题目数量: {len(self.processed_questions)}")
        
        if self.processed_questions:
            # 按类别统计
            categories = {}
            qtypes = {}
            difficulties = {}
            
            for q in self.processed_questions:
                categories[q['category']] = categories.get(q['category'], 0) + 1
                qtypes[q['qtype']] = qtypes.get(q['qtype'], 0) + 1
                difficulties[q['difficulty']] = difficulties.get(q['difficulty'], 0) + 1
            
            print(f"\n按类别分布:")
            for category, count in sorted(categories.items()):
                print(f"  {category}: {count}")
            
            print(f"\n按题型分布:")
            for qtype, count in sorted(qtypes.items()):
                print(f"  {qtype}: {count}")
            
            print(f"\n按难度分布:")
            for difficulty, count in sorted(difficulties.items()):
                print(f"  {difficulty}: {count}")


def main():
    """主函数"""
    print("=== 题库格式化和导入工具 ===")
    
    processor = QuestionProcessor()
    
    # 处理当前目录下的CSV文件
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not csv_files:
        print("当前目录没有找到CSV文件")
        return
    
    print(f"找到以下CSV文件: {csv_files}")
    
    # 处理每个CSV文件
    for csv_file in csv_files:
        if csv_file == 'formatted_questions.csv':  # 跳过输出文件
            continue
        processor.process_csv_file(csv_file)
    
    # 显示统计信息
    processor.print_statistics()
    
    if not processor.processed_questions:
        print("没有有效的题目数据")
        return
    
    # 保存格式化的CSV
    processor.save_formatted_csv('formatted_questions.csv')
    
    # 询问是否导入数据库
    choice = input("\n是否要导入到数据库? (y/n): ").lower().strip()
    if choice in ['y', 'yes', '是']:
        processor.import_to_database()
        print("导入完成！")
    else:
        print("已跳过数据库导入")
    
    print("\n处理完成！")


if __name__ == "__main__":
    main()
