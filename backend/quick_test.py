#!/usr/bin/env python3
"""
快速测试API功能
Quick API Test Script
"""

import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    """测试API基本功能"""

    print("=" * 60)
    print("快速API测试")
    print("=" * 60)

    # 1. 测试登录
    print("\n1. 测试登录...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": "admin", "password": "admin123"},
            timeout=5
        )

        if response.status_code == 200:
            token = response.json().get("access_token")
            print("   ✓ 登录成功")
        else:
            print(f"   ✗ 登录失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
        print("   提示: 请确保API服务器正在运行 (python run.py)")
        return False

    headers = {"Authorization": f"Bearer {token}"}

    # 2. 测试获取题库列表
    print("\n2. 测试获取题库列表...")
    try:
        response = requests.get(f"{BASE_URL}/qbank/banks", headers=headers, timeout=5)

        if response.status_code == 200:
            banks = response.json()
            print(f"   ✓ 成功获取 {len(banks)} 个题库")
            if banks:
                bank_id = banks[0].get('id')
                print(f"   题库: {banks[0].get('name')} (ID: {bank_id})")
            else:
                print("   提示: 没有题库数据")
                bank_id = None
        else:
            print(f"   ✗ 获取题库失败: {response.status_code}")
            bank_id = None
    except Exception as e:
        print(f"   ✗ 请求失败: {e}")
        bank_id = None

    # 3. 测试获取题目列表（使用大limit值）
    if bank_id:
        print("\n3. 测试获取题目列表 (limit=864)...")
        try:
            response = requests.get(
                f"{BASE_URL}/qbank/questions/",
                params={"bank_id": bank_id, "skip": 0, "limit": 864},
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                questions = response.json()
                print(f"   ✓ 成功获取 {len(questions)} 个题目")
            elif response.status_code == 422:
                print(f"   ✗ 参数验证错误: {response.json()}")
            else:
                print(f"   ✗ 获取题目失败: {response.status_code}")
        except Exception as e:
            print(f"   ✗ 请求失败: {e}")

    # 4. 测试创建练习会话
    if bank_id:
        print("\n4. 测试创建练习会话...")
        try:
            response = requests.post(
                f"{BASE_URL}/practice/sessions",
                headers={**headers, "Content-Type": "application/json"},
                json={
                    "bank_id": bank_id,
                    "mode": "sequential",
                    "question_types": None,
                    "difficulty": None
                },
                timeout=5
            )

            if response.status_code == 200:
                session = response.json()
                session_id = session.get('id')
                print(f"   ✓ 成功创建练习会话")
                print(f"   会话ID: {session_id}")
                print(f"   题目总数: {session.get('total_questions')}")
            elif response.status_code == 403:
                print(f"   ✗ 权限不足: {response.json().get('detail')}")
            else:
                print(f"   ✗ 创建会话失败: {response.status_code}")
                print(f"   响应: {response.text}")
        except Exception as e:
            print(f"   ✗ 请求失败: {e}")

    print("\n" + "=" * 60)
    print("✓ 测试完成")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
