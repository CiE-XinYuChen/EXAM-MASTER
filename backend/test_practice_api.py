"""
Test script for Practice API endpoints
测试脚本 - 验证练习API功能
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def login():
    """登录获取token"""
    print("\n=== 1. 测试登录 ===")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "admin",
            "password": "admin123"
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✓ 登录成功，获取到token")
        return token
    else:
        print(f"✗ 登录失败: {response.text}")
        return None


def get_question_banks(token):
    """获取题库列表"""
    print("\n=== 2. 测试获取题库列表 ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/qbank/banks", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        banks = response.json()
        print(f"✓ 成功获取题库列表，共 {len(banks)} 个题库")
        if banks:
            print(f"  第一个题库: {banks[0].get('name')} (ID: {banks[0].get('id')})")
            return banks[0].get('id')
        return None
    else:
        print(f"✗ 获取题库失败: {response.text}")
        return None


def create_practice_session(token, bank_id):
    """创建练习会话"""
    print("\n=== 3. 测试创建练习会话 ===")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "bank_id": bank_id,
        "mode": "sequential",
        "question_types": None,
        "difficulty": None
    }
    response = requests.post(
        f"{BASE_URL}/practice/sessions",
        headers=headers,
        json=data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        session = response.json()
        print(f"✓ 成功创建练习会话")
        print(f"  会话ID: {session.get('id')}")
        print(f"  题目总数: {session.get('total_questions')}")
        print(f"  当前进度: {session.get('current_index')}/{session.get('total_questions')}")
        return session.get('id')
    else:
        print(f"✗ 创建练习会话失败: {response.text}")
        return None


def get_current_question(token, session_id):
    """获取当前题目"""
    print("\n=== 4. 测试获取当前题目 ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/practice/sessions/{session_id}/current",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        question = response.json()
        print(f"✓ 成功获取当前题目")
        print(f"  题目ID: {question.get('id')}")
        print(f"  题目类型: {question.get('type')}")
        print(f"  进度: {question.get('current_index')}/{question.get('total_questions')}")
        print(f"  题干: {question.get('stem')[:50]}..." if len(question.get('stem', '')) > 50 else f"  题干: {question.get('stem')}")
        return question.get('id')
    else:
        print(f"✗ 获取题目失败: {response.text}")
        return None


def submit_answer(token, session_id, question_id):
    """提交答案"""
    print("\n=== 5. 测试提交答案 ===")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "question_id": question_id,
        "user_answer": {
            "answer": "A"
        },
        "time_spent": 30
    }
    response = requests.post(
        f"{BASE_URL}/practice/sessions/{session_id}/submit",
        headers=headers,
        json=data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 成功提交答案")
        print(f"  是否正确: {'✓' if result.get('is_correct') else '✗'}")
        print(f"  正确答案: {result.get('correct_answer')}")
        return True
    else:
        print(f"✗ 提交答案失败: {response.text}")
        return False


def get_session_statistics(token, session_id):
    """获取会话统计"""
    print("\n=== 6. 测试获取会话统计 ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/practice/sessions/{session_id}/statistics",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ 成功获取会话统计")
        print(f"  总题数: {stats.get('total_questions')}")
        print(f"  已完成: {stats.get('completed_count')}")
        print(f"  正确数: {stats.get('correct_count')}")
        print(f"  错误数: {stats.get('wrong_count')}")
        print(f"  正确率: {stats.get('accuracy_rate'):.2f}%")
        return True
    else:
        print(f"✗ 获取统计失败: {response.text}")
        return False


def main():
    """主测试流程"""
    print("=" * 60)
    print("开始测试 Practice API")
    print("=" * 60)

    # 1. 登录
    token = login()
    if not token:
        print("\n✗ 测试终止: 无法获取token")
        return

    # 2. 获取题库
    bank_id = get_question_banks(token)
    if not bank_id:
        print("\n✗ 测试终止: 无法获取题库ID")
        return

    # 3. 创建练习会话
    session_id = create_practice_session(token, bank_id)
    if not session_id:
        print("\n✗ 测试终止: 无法创建练习会话")
        return

    # 4. 获取当前题目
    question_id = get_current_question(token, session_id)
    if not question_id:
        print("\n✗ 测试终止: 无法获取题目")
        return

    # 5. 提交答案
    if not submit_answer(token, session_id, question_id):
        print("\n✗ 测试终止: 无法提交答案")
        return

    # 6. 获取统计
    get_session_statistics(token, session_id)

    print("\n" + "=" * 60)
    print("✓ 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
