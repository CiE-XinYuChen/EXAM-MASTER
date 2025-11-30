"""
修复填空题答案格式
将简单字符串格式转换为 blanks 数组格式
"""
import json
import sys


def fix_fill_answer(answer_str):
    """
    将填空题答案字符串转换为 blanks 格式
    例如: "上方；>" -> {"blanks": [{"answer": "上方", "alternatives": []}, {"answer": ">", "alternatives": []}]}
    """
    if not answer_str:
        return {"blanks": []}

    # 使用多种分隔符分割答案
    # 常见分隔符: ；、; 、,、/
    import re
    # 先尝试用分号分割
    parts = re.split(r'[；;]', answer_str)

    blanks = []
    for part in parts:
        part = part.strip()
        if part:
            blanks.append({
                "answer": part,
                "alternatives": []
            })

    return {"blanks": blanks}


def fix_json_file(input_path, output_path=None):
    """修复 JSON 文件中的填空题答案格式"""
    if output_path is None:
        output_path = input_path

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data.get('questions', [])
    fixed_count = 0

    for q in questions:
        if q.get('type') == 'fill':
            # 检查是否需要修复
            answer = q.get('answer')
            correct_answer = q.get('correct_answer')

            if answer and (not correct_answer or 'blanks' not in correct_answer):
                # 需要修复
                q['correct_answer'] = fix_fill_answer(answer)
                fixed_count += 1
                print(f"修复题目 #{q.get('number')}: {answer[:30]}... -> {len(q['correct_answer']['blanks'])} 个空")

    print(f"\n共修复 {fixed_count} 道填空题")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已保存到: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fix_fill_answer_format.py <json_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    fix_json_file(input_file, output_file)
