#!/bin/bash

# GitHub仓库创建和推送脚本
# 使用方法：./setup_github.sh

echo "=========================================="
echo "Bazi Trading Agents - GitHub仓库设置"
echo "=========================================="
echo ""

REPO_NAME="bazi-trading-agents"
USERNAME="brucewu905"
REPO_URL="https://github.com/${USERNAME}/${REPO_NAME}.git"

echo "仓库信息："
echo "  仓库名称: $REPO_NAME"
echo "  用户名: $USERNAME"
echo "  仓库URL: $REPO_URL"
echo ""

echo "步骤1: 在GitHub上创建仓库"
echo "----------------------------------------"
echo "请访问以下链接手动创建仓库："
echo "https://github.com/new"
echo ""
echo "仓库设置："
echo "  Repository name: $REPO_NAME"
echo "  Description: Bazi Trading Agents - 八字分析多智能体框架，结合传统命理智慧与现代心理学"
echo "  Public: ✓"
echo "  Initialize with: ✗ (不要勾选任何选项)"
echo ""
echo "创建完成后，按回车继续..."
read

echo ""
echo "步骤2: 添加远程仓库"
echo "----------------------------------------"
git remote add origin $REPO_URL 2>/dev/null || git remote set-url origin $REPO_URL
echo "✓ 远程仓库已设置: $REPO_URL"

echo ""
echo "步骤3: 推送到GitHub"
echo "----------------------------------------"
git push -u origin main

echo ""
echo "=========================================="
echo "完成！"
echo "=========================================="
echo ""
echo "仓库地址: $REPO_URL"
echo ""
