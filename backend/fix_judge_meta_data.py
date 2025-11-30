"""
修复数据库中判断题的 meta_data 格式
1. 将 correct_answer 字段改为 answer
2. 将字符串 "true"/"false" 转换为布尔值 true/false
"""
import sqlite3
import json
import os
import glob


def find_databases():
    """查找所有可能的数据库文件"""
    search_dirs = [
        os.path.dirname(__file__),
        os.path.join(os.path.dirname(__file__), "databases"),
        ".",
        "./databases",
    ]

    found_dbs = []
    for dir_path in search_dirs:
        if os.path.exists(dir_path):
            for db_file in glob.glob(os.path.join(dir_path, "*.db")):
                if db_file not in found_dbs:
                    found_dbs.append(db_file)

    return found_dbs


def parse_bool_answer(value):
    """将各种格式的答案转换为布尔值"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ["true", "正确", "对", "是", "yes", "t", "√"]
    return bool(value)


def fix_database(db_path):
    """修复单个数据库中的判断题答案"""
    print(f"\n检查数据库: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查是否存在 questions_v2 表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions_v2'")
        if not cursor.fetchone():
            print(f"  跳过 - 没有 questions_v2 表")
            conn.close()
            return 0

        # 查找所有判断题
        cursor.execute("SELECT id, meta_data FROM questions_v2 WHERE type = 'judge'")
        rows = cursor.fetchall()
        print(f"  找到 {len(rows)} 道判断题")

        fixed_count = 0
        for row in rows:
            question_id, meta_data_str = row

            if not meta_data_str:
                continue

            try:
                meta_data = json.loads(meta_data_str)
            except json.JSONDecodeError:
                print(f"  警告: 题目 {question_id} 的 meta_data 不是有效JSON")
                continue

            need_fix = False
            old_value = None

            # 检查 correct_answer 字段（需要改为 answer）
            if "correct_answer" in meta_data:
                old_value = meta_data["correct_answer"]
                new_value = parse_bool_answer(old_value)
                # 删除旧字段，添加新字段
                del meta_data["correct_answer"]
                meta_data["answer"] = new_value
                need_fix = True

            # 检查 answer 字段是否需要转换类型
            elif "answer" in meta_data:
                old_value = meta_data["answer"]
                if not isinstance(old_value, bool):
                    new_value = parse_bool_answer(old_value)
                    meta_data["answer"] = new_value
                    need_fix = True

            if need_fix:
                # 更新数据库
                new_meta_data_str = json.dumps(meta_data, ensure_ascii=False)
                cursor.execute(
                    "UPDATE questions_v2 SET meta_data = ? WHERE id = ?",
                    (new_meta_data_str, question_id)
                )

                print(f"  修复: {question_id[:8]}... '{old_value}' -> {meta_data['answer']}")
                fixed_count += 1

        conn.commit()
        conn.close()

        if fixed_count > 0:
            print(f"  共修复 {fixed_count} 道判断题")
        else:
            print(f"  无需修复")

        return fixed_count

    except Exception as e:
        print(f"  错误: {e}")
        return 0


def main():
    print("=" * 50)
    print("判断题 meta_data 修复工具")
    print("correct_answer -> answer, 字符串 -> 布尔值")
    print("=" * 50)

    databases = find_databases()

    if not databases:
        print("错误: 找不到任何数据库文件")
        return

    print(f"\n找到 {len(databases)} 个数据库文件:")
    for db in databases:
        print(f"  - {db}")

    total_fixed = 0
    for db_path in databases:
        total_fixed += fix_database(db_path)

    print("\n" + "=" * 50)
    print(f"共修复 {total_fixed} 道判断题")
    print("=" * 50)


if __name__ == "__main__":
    main()
