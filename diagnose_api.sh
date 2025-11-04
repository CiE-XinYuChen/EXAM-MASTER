#!/bin/bash

# API诊断脚本 - 检查所有错题本和收藏相关API
# 使用方法: ./diagnose_api.sh <YOUR_TOKEN>

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <YOUR_TOKEN>${NC}"
    echo "Example: $0 eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    exit 1
fi

TOKEN="$1"
BANK_ID="9ccfb869-9d3c-4a4c-a114-3c21148c9e53"
API_URL="https://exam.shaynechen.tech/api/v1"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}API 诊断报告${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# 1. 检查错题本API
echo -e "${YELLOW}[1/5] 检查错题本列表API${NC}"
echo "-------------------------------------------"
wrong_questions_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X GET "$API_URL/wrong-questions?bank_id=$BANK_ID&limit=3" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

http_code=$(echo "$wrong_questions_response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$wrong_questions_response" | sed '/HTTP_CODE/d')

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✅ HTTP 200 OK${NC}"

    # 检查字段
    question_number=$(echo "$body" | jq -r '.wrong_questions[0].question_number // "null"')
    question_options=$(echo "$body" | jq -r '.wrong_questions[0].question_options // "null"')

    if [ "$question_number" != "null" ] && [ "$question_number" != "" ]; then
        echo -e "${GREEN}  ✅ question_number 字段存在: $question_number${NC}"
    else
        echo -e "${RED}  ❌ question_number 字段缺失或为null${NC}"
    fi

    if [ "$question_options" != "null" ] && [ "$question_options" != "" ]; then
        options_count=$(echo "$body" | jq -r '.wrong_questions[0].question_options | length // 0')
        echo -e "${GREEN}  ✅ question_options 字段存在: $options_count 个选项${NC}"
    else
        echo -e "${RED}  ❌ question_options 字段缺失或为null${NC}"
    fi
else
    echo -e "${RED}❌ HTTP $http_code${NC}"
    echo "$body" | jq '.'
fi
echo ""

# 2. 检查批量收藏状态API
echo -e "${YELLOW}[2/5] 检查批量收藏状态API${NC}"
echo "-------------------------------------------"

# 先获取一些题目ID
question_ids=$(echo "$body" | jq -r '[.wrong_questions[].question_id] | .[0:3]')

batch_check_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$API_URL/favorites/check/batch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"question_ids\": $question_ids}")

http_code=$(echo "$batch_check_response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$batch_check_response" | sed '/HTTP_CODE/d')

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✅ HTTP 200 OK${NC}"
    echo "$body" | jq '.'
elif [ "$http_code" == "422" ]; then
    echo -e "${RED}❌ HTTP 422 Unprocessable Entity${NC}"
    echo -e "${RED}  可能原因:${NC}"
    echo -e "${RED}  1. 请求格式不正确${NC}"
    echo -e "${RED}  2. question_ids 为空或格式错误${NC}"
    echo -e "${RED}  3. 后端Schema定义有问题${NC}"
    echo ""
    echo "请求数据:"
    echo "{\"question_ids\": $question_ids}" | jq '.'
    echo ""
    echo "响应:"
    echo "$body" | jq '.'
else
    echo -e "${RED}❌ HTTP $http_code${NC}"
    echo "$body" | jq '.'
fi
echo ""

# 3. 检查错题练习会话创建
echo -e "${YELLOW}[3/5] 检查错题练习会话创建${NC}"
echo "-------------------------------------------"
practice_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$API_URL/practice/sessions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"bank_id\": \"$BANK_ID\", \"mode\": \"wrong_only\"}")

http_code=$(echo "$practice_response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$practice_response" | sed '/HTTP_CODE/d')

if [ "$http_code" == "200" ] || [ "$http_code" == "201" ]; then
    echo -e "${GREEN}✅ HTTP $http_code${NC}"
    total=$(echo "$body" | jq -r '.total_questions // 0')
    echo -e "${GREEN}  总题数: $total${NC}"
else
    echo -e "${RED}❌ HTTP $http_code${NC}"
    echo "$body" | jq '.'
fi
echo ""

# 4. 检查收藏练习会话创建
echo -e "${YELLOW}[4/5] 检查收藏练习会话创建${NC}"
echo "-------------------------------------------"
favorite_practice_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$API_URL/practice/sessions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"bank_id\": \"$BANK_ID\", \"mode\": \"favorite_only\"}")

http_code=$(echo "$favorite_practice_response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$favorite_practice_response" | sed '/HTTP_CODE/d')

if [ "$http_code" == "200" ] || [ "$http_code" == "201" ]; then
    echo -e "${GREEN}✅ HTTP $http_code${NC}"
    total=$(echo "$body" | jq -r '.total_questions // 0')
    if [ "$total" -gt 0 ]; then
        echo -e "${GREEN}  总题数: $total${NC}"
    else
        echo -e "${YELLOW}  ⚠️  总题数为0，可能没有收藏题目${NC}"
    fi
else
    echo -e "${RED}❌ HTTP $http_code${NC}"
    echo "$body" | jq '.'
fi
echo ""

# 5. 检查收藏列表
echo -e "${YELLOW}[5/5] 检查收藏列表API${NC}"
echo "-------------------------------------------"
favorites_response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X GET "$API_URL/favorites?bank_id=$BANK_ID&limit=3" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

http_code=$(echo "$favorites_response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$favorites_response" | sed '/HTTP_CODE/d')

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✅ HTTP 200 OK${NC}"

    total=$(echo "$body" | jq -r '.total // 0')
    question_number=$(echo "$body" | jq -r '.favorites[0].question_number // "null"')

    echo -e "${GREEN}  总收藏数: $total${NC}"

    if [ "$question_number" != "null" ] && [ "$question_number" != "" ]; then
        echo -e "${GREEN}  ✅ question_number 字段存在: $question_number${NC}"
    else
        echo -e "${RED}  ❌ question_number 字段缺失或为null${NC}"
    fi
else
    echo -e "${RED}❌ HTTP $http_code${NC}"
    echo "$body" | jq '.'
fi
echo ""

# 总结
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}诊断总结${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${YELLOW}需要检查的项目:${NC}"
echo "1. 如果 question_number 为 null → 需要部署后端更新"
echo "2. 如果 question_options 为 null → 需要部署后端更新"
echo "3. 如果批量检查收藏返回422 → 检查远程服务器后端版本"
echo "4. 如果错题练习题数不正确 → 需要部署练习模式修复"
echo "5. 如果收藏练习题数为0 → 检查数据库中的bank_id匹配"
echo ""
echo -e "${BLUE}建议操作:${NC}"
echo "1. 提交本地代码到 git"
echo "2. SSH到远程服务器: ssh user@exam.shaynechen.tech"
echo "3. 拉取最新代码: git pull origin dev_2.0"
echo "4. 重启后端服务: sudo systemctl restart exam-backend"
echo "5. 重新运行此诊断脚本验证"
