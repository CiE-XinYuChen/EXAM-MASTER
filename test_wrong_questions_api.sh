#!/bin/bash

# 测试错题本API - 检查question_number和question_options字段
# 使用方法: ./test_wrong_questions_api.sh <YOUR_TOKEN>

if [ -z "$1" ]; then
    echo "Usage: $0 <YOUR_TOKEN>"
    echo "Example: $0 eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    exit 1
fi

TOKEN="$1"
BANK_ID="9ccfb869-9d3c-4a4c-a114-3c21148c9e53"
API_URL="https://exam.shaynechen.tech/api/v1"

echo "============================================"
echo "测试错题本API"
echo "============================================"
echo ""

echo "1. 获取错题列表（前3条）"
echo "-------------------------------------------"
response=$(curl -s -X GET "$API_URL/wrong-questions?bank_id=$BANK_ID&limit=3" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "完整响应:"
echo "$response" | jq '.'
echo ""

echo "检查第一条错题的字段:"
echo "- question_number: $(echo "$response" | jq -r '.wrong_questions[0].question_number // "❌ null/不存在"')"
echo "- question_type: $(echo "$response" | jq -r '.wrong_questions[0].question_type // "❌ null/不存在"')"
echo "- question_options: $(echo "$response" | jq -r '.wrong_questions[0].question_options // "❌ null/不存在" | if type == "array" then "✅ 存在 (\(length)个选项)" else . end')"
echo ""

echo "============================================"
echo "2. 获取单个错题详情"
echo "-------------------------------------------"
wrong_question_id=$(echo "$response" | jq -r '.wrong_questions[0].id // empty')

if [ -n "$wrong_question_id" ]; then
    detail_response=$(curl -s -X GET "$API_URL/wrong-questions/$wrong_question_id" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json")

    echo "检查字段:"
    echo "- question_number: $(echo "$detail_response" | jq -r '.question_number // "❌ null/不存在"')"
    echo "- question_options: $(echo "$detail_response" | jq -r '.question_options // "❌ null/不存在" | if type == "array" then "✅ 存在 (\(length)个选项)" else . end')"
    echo ""

    echo "选项详情（如果存在）:"
    echo "$detail_response" | jq -r '.question_options // [] | if length > 0 then .[] | "  \(.label): \(.content) (正确: \(.is_correct))" else "  无选项" end'
else
    echo "❌ 无法获取错题ID"
fi

echo ""
echo "============================================"
echo "总结"
echo "============================================"

if echo "$response" | jq -e '.wrong_questions[0].question_number' > /dev/null 2>&1; then
    echo "✅ question_number 字段存在"
else
    echo "❌ question_number 字段不存在或为null - 需要部署后端更新"
fi

if echo "$response" | jq -e '.wrong_questions[0].question_options' > /dev/null 2>&1; then
    echo "✅ question_options 字段存在"
else
    echo "❌ question_options 字段不存在或为null - 需要部署后端更新"
fi
