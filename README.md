# 观己 · Bazi Trading Agents

一个基于 Streamlit 和 LangGraph 的八字文化解读与自我观察工具。用户注册后填写出生信息、选择关注主题，并使用**自己的模型服务商 API Key**生成报告。报告提供传统文化与心理学两个视角，以及可供参考的行动建议。

> 当前仓库提供可运行的代码，**尚未部署公开网站**。GitHub 仓库页面不能直接运行需要 Python 后端和模型 API 的应用。

![观己欢迎页](docs/screenshots/welcome.jpeg)

<details>
<summary>查看更多页面截图</summary>

登录页：

![登录页](docs/screenshots/login.jpeg)

关注主题：

![关注主题](docs/screenshots/topics.jpeg)

</details>

## 目前可以做什么

- **分步填写**：出生日期、时间、地点、历法及补充说明；选择性格、职业、关系、压力等主题，也可提出自定义问题。
- **多智能体分析**：LangGraph 串联命盘、日主、十神、格局、用神、大运、传统视角、心理学视角和综合分析环节。
- **查看报告**：报告概览、传统与心理学双视角、行动建议和反馈。
- **自带 API Key**：支持硅基流动、OpenAI、Anthropic；服务商和模型由应用预设，用户在每次分析时输入自己的 Key。
- **账号与记录隔离**：登录后只显示当前账号的记录。分析记录默认关闭；用户主动勾选后才保存本次出生资料与结果。
- **下载报告**：普通用户可下载简版 Markdown、Word、PDF；管理员另有专业版和 JSON 导出。
- **基础限流**：单账号每小时最多 6 次，单进程每小时最多 60 次，最多同时处理 3 次分析。

## 本地启动

建议使用 Python 虚拟环境。已经创建 `bazi-trading-agents` Conda 环境的用户，在 PowerShell 中运行：

```powershell
cd E:\NSSC\findwork\code\bazi-trading-agents
conda activate bazi-trading-agents
pip install -r requirements.txt
streamlit run web_app.py
```

也可以先克隆本仓库，再进入克隆后的目录运行后三条命令：

```powershell
git clone https://github.com/Mengyaolv/bazi-trading-agents.git
cd bazi-trading-agents
```

终端显示 `Local URL` 后，在浏览器打开该地址，通常是 `http://localhost:8501`。首次使用先注册账号；生成分析前选择服务商并输入该服务商的有效 API Key。停止服务时在终端按 `Ctrl+C`。

网页模式无需把自己的 API Key 写入 `.env`。如需调整运行参数，可参考 [`.env.example`](.env.example)；**不要提交 `.env`、真实 Key、`data/`、`results/` 或 `memory/` 中的私人内容**。

## 使用流程

1. 注册或登录。
2. 填写出生信息，选择关注主题。
3. 确认资料，选择模型服务商并输入自己的 API Key。按需勾选“允许记录本次分析结果”。
4. 查看报告概览、双视角分析及行动建议，并下载报告。

API Key 会通过应用服务器发送给所选模型服务商，用于当前分析；应用不将 Key 写入分析记录。出生资料和相关问题也会发送给模型服务商。若选择保存记录，服务器会保存出生资料与分析结果；账号数据保存在 `data/users.json`。请只在信任的服务实例上填写资料与 Key。

## 项目结构

```text
web_app.py             Streamlit 网页入口
bazi_graph/             LangGraph 分析流程
bazi_agents/            各分析智能体
utils/                  登录、访问限制、导出、记录与质量检查等工具
prompts/                分析提示词
docs/screenshots/       README 页面截图
PUBLIC_DEPLOYMENT.md    公开部署说明
```

## 公开部署说明

当前仓库上传到 GitHub 后，访客只能查看代码。要提供可访问的网站，需要另行部署一个能持续运行 Python 的服务，并用 HTTPS 对外提供访问。部署步骤和数据持久化要求见 [`PUBLIC_DEPLOYMENT.md`](PUBLIC_DEPLOYMENT.md)。`PUBLIC_MODE=1` 用于公开环境；`data/users.json` 需要持久化，只有在允许保留分析记录时才需要持久化 `results/`。

## 使用边界与来源

当前“四柱排盘”环节由大模型生成，**不是经过独立历法程序校验的确定性计算**，可能出现排盘或解读错误。所有内容仅供文化解读与自我观察参考，不构成心理诊断、医疗、法律、投资或重大人生决策建议。

本项目基于 [brucewu905/bazi-trading-agents](https://github.com/brucewu905/bazi-trading-agents) 改造；原框架作者为 Wu Zhongpei。请保留原项目来源，并遵守上游许可与署名要求。
