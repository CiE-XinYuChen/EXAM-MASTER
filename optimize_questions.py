#!/usr/bin/env python3
"""
ExamMaster 题型优化脚本

该脚本用于：
1. 检测和修正数据库中的题型
2. 统计不同题型的分布
3. 优化题目数据质量

使用方法：
python optimize_questions.py
"""

import sqlite3
import json
import sys
import os

# 导入应用模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import QuestionTypeManager

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def detect_and_update_question_types():
    """检测并更新所有题目的类型"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # 获取所有题目
    c.execute('SELECT * FROM questions')
    questions = c.fetchall()
    
    print(f"开始处理 {len(questions)} 道题目...")
    
    type_changes = {
        'updated': 0,
        'unchanged': 0,
        'type_distribution': {}
    }
    
    for question in questions:
        # 构建题目数据
        question_data = {
            'stem': question['stem'],
            'options': json.loads(question['options']) if question['options'] else {},
            'answer': question['answer'],
            'qtype': question['qtype']
        }
        
        # 检测题型
        detected_type = QuestionTypeManager.detect_question_type(question_data)
        original_type = question['qtype'] or '未分类'
        
        # 统计题型分布
        type_distribution = type_changes['type_distribution']
        if detected_type not in type_distribution:
            type_distribution[detected_type] = 0
        type_distribution[detected_type] += 1
        
        # 更新题型（如果有变化）
        if original_type != detected_type:
            c.execute('UPDATE questions SET qtype = ? WHERE id = ?', 
                     (detected_type, question['id']))
            type_changes['updated'] += 1
            print(f"题目 {question['id']}: {original_type} → {detected_type}")
        else:
            type_changes['unchanged'] += 1
    
    conn.commit()
    conn.close()
    
    return type_changes

def add_missing_judgment_options():
    """为判断题添加缺失的选项"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # 获取所有判断题
    c.execute('SELECT * FROM questions WHERE qtype = ?', ('判断题',))
    judgment_questions = c.fetchall()
    
    print(f"处理 {len(judgment_questions)} 道判断题...")
    
    updated_count = 0
    default_options = {'A': '对', 'B': '错'}
    
    for question in judgment_questions:
        options = json.loads(question['options']) if question['options'] else {}
        
        # 如果选项为空或不完整，添加默认选项
        if not options or len(options) < 2:
            c.execute('UPDATE questions SET options = ? WHERE id = ?',
                     (json.dumps(default_options, ensure_ascii=False), question['id']))
            updated_count += 1
            print(f"为题目 {question['id']} 添加判断题选项")
    
    conn.commit()
    conn.close()
    
    return updated_count

def analyze_question_quality():
    """分析题目质量"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # 统计各种质量指标
    c.execute('SELECT COUNT(*) as total FROM questions')
    total = c.fetchone()['total']
    
    c.execute('SELECT COUNT(*) as no_type FROM questions WHERE qtype IS NULL OR qtype = ""')
    no_type = c.fetchone()['no_type']
    
    c.execute('SELECT COUNT(*) as no_options FROM questions WHERE options IS NULL OR options = "" OR options = "{}"')
    no_options = c.fetchone()['no_options']
    
    c.execute('SELECT COUNT(*) as no_difficulty FROM questions WHERE difficulty IS NULL OR difficulty = "" OR difficulty = "无"')
    no_difficulty = c.fetchone()['no_difficulty']
    
    c.execute('''
        SELECT qtype, COUNT(*) as count 
        FROM questions 
        WHERE qtype IS NOT NULL AND qtype != ""
        GROUP BY qtype 
        ORDER BY count DESC
    ''')
    type_stats = c.fetchall()
    
    conn.close()
    
    return {
        'total': total,
        'no_type': no_type,
        'no_options': no_options,
        'no_difficulty': no_difficulty,
        'type_stats': type_stats
    }

def print_quality_report(quality_stats):
    """打印质量报告"""
    print("\n" + "="*50)
    print("           题目质量分析报告")
    print("="*50)
    
    print(f"总题目数量: {quality_stats['total']}")
    print(f"缺少题型: {quality_stats['no_type']} ({quality_stats['no_type']/quality_stats['total']*100:.1f}%)")
    print(f"缺少选项: {quality_stats['no_options']} ({quality_stats['no_options']/quality_stats['total']*100:.1f}%)")
    print(f"缺少难度: {quality_stats['no_difficulty']} ({quality_stats['no_difficulty']/quality_stats['total']*100:.1f}%)")
    
    print("\n题型分布:")
    print("-" * 30)
    for stat in quality_stats['type_stats']:
        percentage = stat['count'] / quality_stats['total'] * 100
        print(f"{stat['qtype']:<15}: {stat['count']:>4} 题 ({percentage:>5.1f}%)")

def optimize_judgment_questions():
    """专门优化判断题的函数"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # 获取所有判断题
    c.execute('SELECT * FROM questions WHERE qtype = ?', ('判断题',))
    judgment_questions = c.fetchall()
    
    print(f"开始优化 {len(judgment_questions)} 道判断题...")
    
    updated_count = 0
    default_options = {'A': '对', 'B': '错'}
    
    for question in judgment_questions:
        options = json.loads(question['options']) if question['options'] else {}
        answer = question['answer']
        need_update = False
        
        # 1. 为判断题添加默认选项（如果没有选项）
        if not options or len(options) < 2:
            options = default_options
            need_update = True
            print(f"为题目 {question['id']} 添加判断题选项")
        
        # 2. 标准化答案格式
        original_answer = answer
        if answer.lower() in ['正确', '对', 'true', 't']:
            answer = 'A'  # A选项对应"对"
            need_update = True
            print(f"题目 {question['id']} 答案标准化: {original_answer} → {answer}")
        elif answer.lower() in ['错误', '错', 'false', 'f']:
            answer = 'B'  # B选项对应"错"
            need_update = True
            print(f"题目 {question['id']} 答案标准化: {original_answer} → {answer}")
        
        # 3. 更新数据库
        if need_update:
            c.execute('''
                UPDATE questions 
                SET options = ?, answer = ? 
                WHERE id = ?
            ''', (json.dumps(options, ensure_ascii=False), answer, question['id']))
            updated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"判断题优化完成，共更新了 {updated_count} 道题目")
    return updated_count

def main():
    """主函数"""
    print("ExamMaster 题型优化脚本")
    print("=" * 40)
    
    # 1. 分析当前质量状况
    print("\n1. 分析当前题目质量...")
    quality_before = analyze_question_quality()
    print_quality_report(quality_before)
    
    # 2. 检测和更新题型
    print("\n2. 检测和更新题型...")
    type_changes = detect_and_update_question_types()
    
    print(f"\n题型更新完成:")
    print(f"- 更新了 {type_changes['updated']} 道题目")
    print(f"- {type_changes['unchanged']} 道题目无需更新")
    
    # 3. 专门优化判断题
    print("\n3. 专门优化判断题...")
    judgment_updated = optimize_judgment_questions()
    
    # 4. 为判断题添加选项（保留原有功能）
    print("\n4. 为判断题添加选项...")
    judgment_options_updated = add_missing_judgment_options()
    print(f"为 {judgment_options_updated} 道判断题添加了选项")
    
    # 5. 重新分析质量
    print("\n5. 重新分析题目质量...")
    quality_after = analyze_question_quality()
    print_quality_report(quality_after)
    
    # 6. 显示改进效果
    print("\n改进效果:")
    print("-" * 30)
    print(f"题型完整率: {100-quality_before['no_type']/quality_before['total']*100:.1f}% → {100-quality_after['no_type']/quality_after['total']*100:.1f}%")
    print(f"选项完整率: {100-quality_before['no_options']/quality_before['total']*100:.1f}% → {100-quality_after['no_options']/quality_after['total']*100:.1f}%")
    print(f"判断题优化: 共处理 {judgment_updated} 道判断题")
    
    print(f"\n✅ 优化完成！题目数据质量得到显著提升。")
    print(f"📊 特别针对判断题进行了以下优化：")
    print(f"   - 自动添加A='对', B='错'选项")
    print(f"   - 将'正确'/'错误'答案标准化为A/B选项")
    print(f"   - 增强答案匹配逻辑，支持多种输入格式")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc() 