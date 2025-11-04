#!/usr/bin/env python3
"""
测试远程API的脚本
Test script for remote API at exam.shaynechen.tech
"""

import requests
import json

# API配置
BASE_URL = "https://exam.shaynechen.tech/api/v1"
# 请替换为你的token
TOKEN = "YOUR_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_favorites_list(bank_id):
    """测试收藏列表API"""
    print("\n=== 测试收藏列表 ===")
    url = f"{BASE_URL}/favorites"
    params = {"bank_id": bank_id, "limit": 100}

    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total favorites: {data.get('total', 0)}")
            print(f"Favorites returned: {len(data.get('favorites', []))}")

            # 打印前3个收藏的题目信息
            for i, fav in enumerate(data.get('favorites', [])[:3], 1):
                print(f"\nFavorite {i}:")
                print(f"  - ID: {fav.get('id')}")
                print(f"  - Question ID: {fav.get('question_id')}")
                print(f"  - Question Number: {fav.get('question_number')}")
                print(f"  - Question Stem: {fav.get('question_stem', '')[:50]}...")
        else:
            print(f"Error: {response.text}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def test_wrong_questions_list(bank_id):
    """测试错题列表API"""
    print("\n=== 测试错题列表 ===")
    url = f"{BASE_URL}/wrong-questions"
    params = {"bank_id": bank_id, "limit": 100}

    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total wrong questions: {data.get('total', 0)}")
            print(f"Uncorrected count: {data.get('uncorrected_count', 0)}")
            print(f"Wrong questions returned: {len(data.get('wrong_questions', []))}")

            # 打印前3个错题的信息
            for i, wq in enumerate(data.get('wrong_questions', [])[:3], 1):
                print(f"\nWrong Question {i}:")
                print(f"  - ID: {wq.get('id')}")
                print(f"  - Question ID: {wq.get('question_id')}")
                print(f"  - Question Number: {wq.get('question_number')}")
                print(f"  - Error Count: {wq.get('error_count')}")
                print(f"  - Question Stem: {wq.get('question_stem', '')[:50]}...")
        else:
            print(f"Error: {response.text}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def test_create_practice_session(bank_id, mode="favorite_only"):
    """测试创建练习会话"""
    print(f"\n=== 测试创建练习会话 (mode={mode}) ===")
    url = f"{BASE_URL}/practice/sessions"

    payload = {
        "bank_id": bank_id,
        "mode": mode
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"Session created successfully!")
            print(f"  - Session ID: {data.get('id')}")
            print(f"  - Total Questions: {data.get('total_questions')}")
            print(f"  - Mode: {data.get('mode')}")
            print(f"  - Status: {data.get('status')}")
            return data
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def test_bank_statistics(bank_id):
    """测试题库统计API"""
    print("\n=== 测试题库统计 ===")
    url = f"{BASE_URL}/statistics/bank/{bank_id}"

    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Statistics loaded successfully!")
            print(f"  - Total Questions: {data.get('total_questions')}")
            print(f"  - Practiced Questions: {data.get('practiced_questions')}")
            print(f"  - Accuracy Rate: {data.get('accuracy_rate'):.2f}%")
        else:
            print(f"Error: {response.text}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def main():
    print("远程API调试工具")
    print("="*50)

    # 请替换为你的实际bank_id
    bank_id = input("请输入 bank_id (或按Enter使用默认): ").strip()
    if not bank_id:
        bank_id = "YOUR_BANK_ID"  # 替换为默认的bank_id

    token = input("请输入 token (或按Enter使用脚本中的TOKEN): ").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    print(f"\n使用 bank_id: {bank_id}")
    print(f"API URL: {BASE_URL}")

    # 运行测试
    test_favorites_list(bank_id)
    test_wrong_questions_list(bank_id)
    test_bank_statistics(bank_id)
    test_create_practice_session(bank_id, mode="favorite_only")
    test_create_practice_session(bank_id, mode="wrong_only")

    print("\n" + "="*50)
    print("测试完成")

if __name__ == "__main__":
    main()
