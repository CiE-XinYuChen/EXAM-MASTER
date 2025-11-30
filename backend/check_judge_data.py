"""
检查判断题数据格式
"""
import sqlite3
import json
import os
import glob


def find_databases():
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


def check_database(db_path):
    print(f"\n检查数据库: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions_v2'")
        if not cursor.fetchone():
            print(f"  跳过 - 没有 questions_v2 表")
            conn.close()
            return

        # 查找判断题，显示 meta_data 内容
        cursor.execute("""
            SELECT id, stem, meta_data
            FROM questions_v2
            WHERE type = 'judge'
            LIMIT 5
        """)
        rows = cursor.fetchall()

        print(f"  找到判断题，显示前5条:")
        for row in rows:
            question_id, stem, meta_data_str = row
            print(f"\n  ID: {question_id[:8]}...")
            print(f"  题干: {stem[:50]}...")
            print(f"  meta_data 原始值: {meta_data_str}")

            if meta_data_str:
                try:
                    meta_data = json.loads(meta_data_str)
                    print(f"  meta_data 解析后: {meta_data}")
                    if "answer" in meta_data:
                        answer = meta_data["answer"]
                        print(f"  answer 值: {answer}, 类型: {type(answer).__name__}")
                except:
                    print(f"  解析失败")

        conn.close()

    except Exception as e:
        print(f"  错误: {e}")


def main():
    print("=" * 60)
    print("判断题数据检查")
    print("=" * 60)

    databases = find_databases()

    for db_path in databases:
        if "question_bank" in db_path:
            check_database(db_path)


if __name__ == "__main__":
    main()
