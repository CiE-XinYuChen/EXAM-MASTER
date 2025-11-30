"""
修复数据库中无效的题目类型
将 'question' 改为 'essay'
将 'true_false' 改为 'judge'
"""
import sqlite3
import os

# 获取数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "qbank.db")

def fix_question_types():
    print(f"数据库路径: {DB_PATH}")

    if not os.path.exists(DB_PATH):
        print(f"错误: 数据库文件不存在: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 查看有多少无效记录
    cursor.execute("SELECT COUNT(*) FROM questions_v2 WHERE type = 'question'")
    question_count = cursor.fetchone()[0]
    print(f"发现 {question_count} 条 type='question' 的记录")

    cursor.execute("SELECT COUNT(*) FROM questions_v2 WHERE type = 'true_false'")
    true_false_count = cursor.fetchone()[0]
    print(f"发现 {true_false_count} 条 type='true_false' 的记录")

    # 修复 'question' -> 'essay'
    if question_count > 0:
        cursor.execute("UPDATE questions_v2 SET type = 'essay' WHERE type = 'question'")
        print(f"已将 {question_count} 条记录的 type 从 'question' 改为 'essay'")

    # 修复 'true_false' -> 'judge'
    if true_false_count > 0:
        cursor.execute("UPDATE questions_v2 SET type = 'judge' WHERE type = 'true_false'")
        print(f"已将 {true_false_count} 条记录的 type 从 'true_false' 改为 'judge'")

    conn.commit()
    conn.close()

    print("修复完成!")

if __name__ == "__main__":
    fix_question_types()
