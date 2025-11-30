"""
修复判断题答案格式
将 "正确"/"错误" 字符串转换为 {"answer": true/false} 格式
"""
import json
import sys


def fix_judge_answer(answer_str):
    """
    将判断题答案字符串转换为正确格式
    例如: "正确" -> {"answer": true}
          "错误" -> {"answer": false}
    """
    if not answer_str:
        return {"answer": False}

    answer_str = answer_str.strip().lower()

    # 判断是正确还是错误
    if answer_str in ['正确', '对', 'true', 't', 'yes', 'y', '√', '是']:
        return {"answer": True}
    else:
        return {"answer": False}


def fix_json_file(input_path, output_path=None):
    """修复 JSON 文件中的判断题答案格式"""
    if output_path is None:
        output_path = input_path

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data.get('questions', [])
    fixed_count = 0

    for q in questions:
        if q.get('type') == 'judge':
            # 检查是否需要修复
            answer = q.get('answer')
            correct_answer = q.get('correct_answer')

            if answer and (not correct_answer or 'answer' not in correct_answer):
                # 需要修复
                q['correct_answer'] = fix_judge_answer(answer)
                fixed_count += 1
                print(f"修复题目 #{q.get('number')}: {answer} -> {q['correct_answer']['answer']}")

    print(f"\n共修复 {fixed_count} 道判断题")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已保存到: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fix_judge_answer_format.py <json_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    fix_json_file(input_file, output_file)
