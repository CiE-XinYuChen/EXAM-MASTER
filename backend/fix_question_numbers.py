"""
修复题库中重复或缺失的题号
为每个题库的题目重新分配连续的题号
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.question_models_v2 import QuestionV2
from sqlalchemy import func

def fix_question_numbers():
    """修复所有题库的题号"""

    # 创建数据库连接
    engine = create_engine(str(settings.QBANK_DATABASE_URL))
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("开始修复题号...")

        # 1. 检查当前重复的题号
        print("\n检查重复题号:")
        duplicates = session.execute(text("""
            SELECT bank_id, question_number, COUNT(*) as count
            FROM questions_v2
            WHERE question_number IS NOT NULL AND question_number > 0
            GROUP BY bank_id, question_number
            HAVING COUNT(*) > 1
        """)).fetchall()

        if duplicates:
            print(f"发现 {len(duplicates)} 个重复题号:")
            for dup in duplicates:
                print(f"  题库ID: {dup[0]}, 题号: {dup[1]}, 重复次数: {dup[2]}")
        else:
            print("未发现重复题号")

        # 2. 检查缺失题号的题目
        null_count = session.query(QuestionV2).filter(
            (QuestionV2.question_number == None) | (QuestionV2.question_number == 0)
        ).count()
        print(f"\n发现 {null_count} 个缺失题号的题目")

        # 3. 获取所有题库
        banks = session.execute(text("""
            SELECT DISTINCT bank_id FROM questions_v2
            WHERE bank_id IS NOT NULL
            ORDER BY bank_id
        """)).fetchall()

        print(f"\n共有 {len(banks)} 个题库需要处理")

        # 4. 为每个题库重新分配题号
        for (bank_id,) in banks:
            # 获取该题库的所有题目，按照优先级排序：
            # 1. 已有有效题号的题目按原题号排序
            # 2. 没有题号的题目按创建时间和ID排序
            questions = session.query(QuestionV2).filter(
                QuestionV2.bank_id == bank_id
            ).order_by(
                # 有效题号的优先，然后按题号排序
                func.coalesce(
                    func.nullif(QuestionV2.question_number, 0),
                    999999
                ),
                QuestionV2.created_at,
                QuestionV2.id
            ).all()

            # 重新分配连续题号
            for index, question in enumerate(questions, start=1):
                old_number = question.question_number
                question.question_number = index
                if old_number != index:
                    print(f"  题库 {bank_id}: 题目 {question.id[:8]}... 题号 {old_number} -> {index}")

        # 5. 提交更改
        session.commit()
        print("\n✓ 题号修复完成！")

        # 6. 验证结果
        print("\n验证修复结果:")
        banks_stats = session.execute(text("""
            SELECT
                bank_id,
                COUNT(*) as total_questions,
                MIN(question_number) as min_number,
                MAX(question_number) as max_number,
                COUNT(DISTINCT question_number) as unique_numbers
            FROM questions_v2
            GROUP BY bank_id
            ORDER BY bank_id
        """)).fetchall()

        for stat in banks_stats:
            bank_id, total, min_num, max_num, unique = stat
            status = "✓" if total == unique and min_num == 1 and max_num == total else "✗"
            print(f"{status} 题库 {bank_id}: {total}题, 题号范围 {min_num}-{max_num}, 唯一题号 {unique}")

    except Exception as e:
        session.rollback()
        print(f"\n✗ 修复失败: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fix_question_numbers()
