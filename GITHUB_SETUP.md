# GitHub仓库设置指南

## 方法1: 手动创建（推荐）

### 步骤1: 在GitHub上创建仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - Repository name: `bazi-trading-agents`
   - Description: `Bazi Trading Agents - 八字分析多智能体框架，结合传统命理智慧与现代心理学`
   - Public: ✓ 勾选
   - **重要**: 不要勾选 "Initialize this repository with a README"
3. 点击 "Create repository"

### 步骤2: 推送代码到GitHub

```bash
cd ~/projects/bazi-trading-agents

# 添加远程仓库
git remote add origin https://github.com/brucewu905/bazi-trading-agents.git

# 推送代码
git push -u origin main
```

### 步骤3: 验证

访问 https://github.com/brucewu905/bazi-trading-agents 查看仓库

---

## 方法2: 使用脚本（需要GitHub Token）

### 步骤1: 获取GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 点击 "Generate token"
5. 复制token（只显示一次）

### 步骤2: 设置环境变量

```bash
export GITHUB_TOKEN=your_token_here
```

### 步骤3: 运行脚本

```bash
cd ~/projects/bazi-trading-agents
python3 create_github_repo.py
```

### 步骤4: 推送代码

```bash
git remote add origin https://github.com/brucewu905/bazi-trading-agents.git
git push -u origin main
```

---

## 方法3: 使用GitHub CLI（需要安装gh）

### 安装GitHub CLI

```bash
# macOS
brew install gh

# Linux
# 参考https://github.com/cli/cli#installation
```

### 登录

```bash
gh auth login
```

### 创建仓库并推送

```bash
cd ~/projects/bazi-trading-agents
gh repo create bazi-trading-agents --public --description "Bazi Trading Agents - 八字分析多智能体框架，结合传统命理智慧与现代心理学" --source=. --remote=origin --push
```

---

## 推荐方法

**推荐使用方法1（手动创建）**，因为：
- 不需要额外的token或工具
- 最简单直接
- 适合一次性操作

---

## 完成后

仓库创建完成后，可以：
1. 访问 https://github.com/brucewu905/bazi-trading-agents
2. 查看所有文件和提交历史
3. 分享仓库链接给他人
4. 继续开发和提交新代码
