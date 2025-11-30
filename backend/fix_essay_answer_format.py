"""
修复问答题答案格式
将简单字符串转换为 {"reference_answer": "...", "keywords": [...]} 格式
"""
import json
import sys
import re


def extract_keywords(text):
    """从文本中提取关键词"""
    if not text:
        return []

    # 移除括号内容
    text = re.sub(r'[（(][^)）]*[)）]', '', text)

    # 分割成词组
    parts = re.split(r'[；;、,，/]', text)

    keywords = []
    for part in parts:
        part = part.strip()
        if part and len(part) > 1 and len(part) < 50:
            keywords.append(part)

    return keywords[:5]  # 最多5个关键词


def fix_essay_answer(answer_str):
    """
    将问答题答案字符串转换为正确格式
    """
    if not answer_str:
        return {"reference_answer": "", "keywords": []}

    return {
        "reference_answer": answer_str,
        "keywords": extract_keywords(answer_str)
    }


def fix_json_file(input_path, output_path=None):
    """修复 JSON 文件中的问答题答案格式"""
    if output_path is None:
        output_path = input_path

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data.get('questions', [])
    fixed_count = 0

    for q in questions:
        if q.get('type') == 'essay':
            # 检查是否需要修复
            answer = q.get('answer')
            correct_answer = q.get('correct_answer')

            if answer and (not correct_answer or 'reference_answer' not in correct_answer):
                # 需要修复
                q['correct_answer'] = fix_essay_answer(answer)
                fixed_count += 1
                keywords = q['correct_answer']['keywords']
                print(f"修复题目 #{q.get('number')}: 关键词={keywords[:3]}...")

    print(f"\n共修复 {fixed_count} 道问答题")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已保存到: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fix_essay_answer_format.py <json_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    fix_json_file(input_file, output_file)
