# 快速设置GitHub仓库

## 3步完成

### 1. 创建仓库（30秒）

访问这个链接，仓库信息会自动填充：
https://github.com/new?name=bazi-trading-agents&description=Bazi%20Trading%20Agents%20-%20%E5%85%AB%E5%AD%97%E5%88%86%E6%9E%90%E5%A4%9A%E6%99%BA%E8%83%BD%E4%BD%93%E6%A1%86%E6%9E%B6%EF%BC%8C%E7%BB%93%E5%90%88%E4%BC%A0%E7%BB%9F%E5%91%BD%E7%90%86%E6%99%BA%E6%85%A7%E4%B8%8E%E7%8E%B0%E4%BB%A3%E5%BF%83%E7%90%86%E5%AD%A6&visibility=public

**重要**: 不要勾选任何初始化选项！

点击 "Create repository"

### 2. 推送代码（10秒）

```bash
cd ~/projects/bazi-trading-agents
git remote add origin https://github.com/brucewu905/bazi-trading-agents.git
git push -u origin main
```

### 3. 完成！

访问: https://github.com/brucewu905/bazi-trading-agents

---

## 如果遇到问题

### 问题: remote already exists

```bash
git remote set-url origin https://github.com/brucewu905/bazi-trading-agents.git
git push -u origin main
```

### 问题: 认证失败

```bash
# 使用SSH（推荐）
git remote set-url origin git@github.com:brucewu905/bazi-trading-agents.git
git push -u origin main
```

---

## 完成后可以做什么

- 查看代码: https://github.com/brucewu905/bazi-trading-agents
- 分享链接: https://github.com/brucewu905/bazi-trading-agents
- 继续开发: `git add . && git commit -m "message" && git push`
