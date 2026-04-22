#!/usr/bin/env python3
"""
使用GitHub API创建仓库的脚本
需要设置GITHUB_TOKEN环境变量
"""

import os
import sys
import json
import requests

def create_github_repo():
    """创建GitHub仓库"""

    # 检查token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("错误: 未找到GITHUB_TOKEN环境变量")
        print("请设置: export GITHUB_TOKEN=your_token_here")
        sys.exit(1)

    # 仓库信息
    username = "brucewu905"
    repo_name = "bazi-trading-agents"
    url = f"https://api.github.com/repos/{username}/{repo_name}"

    # 检查仓库是否已存在
    print(f"检查仓库是否存在: {repo_name}")
    response = requests.get(url, headers={"Authorization": f"token {token}"})

    if response.status_code == 200:
        print(f"✓ 仓库已存在: {url}")
        return url

    # 创建仓库
    print(f"创建仓库: {repo_name}")
    create_url = "https://api.github.com/user/repos"
    data = {
        "name": repo_name,
        "description": "Bazi Trading Agents - 八字分析多智能体框架，结合传统命理智慧与现代心理学",
        "private": False,
        "auto_init": False
    }

    response = requests.post(
        create_url,
        headers={
            "Authorization": f"token {token}",
            "Content-Type": "application/json"
        },
        data=json.dumps(data)
    )

    if response.status_code == 201:
        repo_data = response.json()
        print(f"✓ 仓库创建成功!")
        print(f"  URL: {repo_data['html_url']}")
        print(f"  Clone URL: {repo_data['clone_url']}")
        return repo_data['clone_url']
    else:
        print(f"✗ 创建失败: {response.status_code}")
        print(response.text)
        sys.exit(1)

if __name__ == "__main__":
    try:
        repo_url = create_github_repo()
        print(f"\n仓库URL: {repo_url}")
        print("\n现在可以运行:")
        print("  git remote add origin https://github.com/brucewu905/bazi-trading-agents.git")
        print("  git push -u origin main")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
