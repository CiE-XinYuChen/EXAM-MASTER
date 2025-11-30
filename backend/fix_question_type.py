"""
修复数据库中无效的题目类型
将 'question' 改为 'essay'
将 'true_false' 改为 'judge'
"""
import sqlite3
import os
import glob

def find_databases():
    """查找所有可能的数据库文件"""
    # 可能的目录
    search_dirs = [
        os.path.dirname(__file__),
        os.path.join(os.path.dirname(__file__), "databases"),
        os.path.join(os.path.dirname(__file__), "data"),
        "/root/demo/EXAM-MASTER/backend",
        "/root/demo/EXAM-MASTER/backend/databases",
        "/root/demo/EXAM-MASTER/backend/data",
        ".",
        "./databases",
        "./data",
    ]

    found_dbs = []
    for dir_path in search_dirs:
        if os.path.exists(dir_path):
            for db_file in glob.glob(os.path.join(dir_path, "*.db")):
                if db_file not in found_dbs:
                    found_dbs.append(db_file)

    return found_dbs

def fix_database(db_path):
    """修复单个数据库"""
    print(f"\n检查数据库: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查是否存在 questions_v2 表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions_v2'")
        if not cursor.fetchone():
            print(f"  跳过 - 没有 questions_v2 表")
            conn.close()
            return False

        # 查看有多少无效记录
        cursor.execute("SELECT COUNT(*) FROM questions_v2 WHERE type = 'question'")
        question_count = cursor.fetchone()[0]
        print(f"  发现 {question_count} 条 type='question' 的记录")

        cursor.execute("SELECT COUNT(*) FROM questions_v2 WHERE type = 'true_false'")
        true_false_count = cursor.fetchone()[0]
        print(f"  发现 {true_false_count} 条 type='true_false' 的记录")

        if question_count == 0 and true_false_count == 0:
            print(f"  无需修复")
            conn.close()
            return False

        # 修复 'question' -> 'essay'
        if question_count > 0:
            cursor.execute("UPDATE questions_v2 SET type = 'essay' WHERE type = 'question'")
            print(f"  已将 {question_count} 条记录的 type 从 'question' 改为 'essay'")

        # 修复 'true_false' -> 'judge'
        if true_false_count > 0:
            cursor.execute("UPDATE questions_v2 SET type = 'judge' WHERE type = 'true_false'")
            print(f"  已将 {true_false_count} 条记录的 type 从 'true_false' 改为 'judge'")

        conn.commit()
        conn.close()
        print(f"  修复完成!")
        return True

    except Exception as e:
        print(f"  错误: {e}")
        return False

def main():
    print("=" * 50)
    print("题目类型修复工具")
    print("=" * 50)

    databases = find_databases()

    if not databases:
        print("错误: 找不到任何数据库文件")
        return

    print(f"\n找到 {len(databases)} 个数据库文件:")
    for db in databases:
        print(f"  - {db}")

    fixed_count = 0
    for db_path in databases:
        if fix_database(db_path):
            fixed_count += 1

    print("\n" + "=" * 50)
    print(f"共修复了 {fixed_count} 个数据库")
    print("=" * 50)

if __name__ == "__main__":
    main()
