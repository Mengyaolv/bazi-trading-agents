# Bazi Trading Agents - 八字分析多智能体框架

一个基于TradingAgents架构的八字（四柱）分析多智能体框架，结合传统命理学与现代心理学。

## 特性

- **多智能体架构**: 9个专业智能体协同工作
- **传统+现代**: 传统命理智慧与现代心理学翻译
- **辩论机制**: 传统命理师与心理学分析师的深度对话
- **记忆系统**: 智能体可以从历史分析中学习
- **可扩展**: 易于添加新的分析维度

## 智能体架构

### 分析阶段
1. **命盘计算师** (Chart Calculator) - 四柱排盘 + 大运计算
2. **日主分析师** (Day Master Analyst) - 日主强弱分析
3. **十神分析师** (Ten Gods Analyst) - 十神分布与组合效应
4. **格局分析师** (Pattern Analyst) - 格局判断与高低评估
5. **用神分析师** (Useful God Analyst) - 四法取用（扶抑/调候/通关/病药）
6. **大运分析师** (Luck Cycle Analyst) - 大运趋势与人生阶段

### 辩论阶段
7. **传统命理师** (Traditional Analyst) - 传统命理视角
8. **心理学分析师** (Psychology Analyst) - 现代心理学视角

### 综合阶段
9. **综合分析师** (Comprehensive Analyst) - 最终综合分析

## 安装

```bash
cd ~/projects/bazi-trading-agents

# 安装依赖
pip install -r requirements.txt

# 或使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```python
from bazi_graph import BaziAnalysisGraph

# 初始化分析图
graph = BaziAnalysisGraph(
    llm_provider="siliconflow",
    llm_model="deepseek-ai/DeepSeek-V3",
    base_url="https://api.siliconflow.cn/v1",
    debug=True
)

# 运行分析
birth_info = "1990年9月5日8:00，男，农历"
final_state, final_analysis = graph.analyze(birth_info)

# 输出结果
print(final_analysis)
```

### 运行测试

```bash
cd ~/projects/bazi-trading-agents
python test_bazi_analysis.py
```

## 配置选项

### LLM提供商支持

- **SiliconFlow**: `llm_provider="siliconflow"`
- **OpenAI**: `llm_provider="openai"`
- **Anthropic**: `llm_provider="anthropic"`

### 配置参数

```python
config = {
    "memory_dir": "./memory",           # 记忆存储目录
    "results_dir": "./results",         # 结果存储目录
    "max_debate_rounds": 3,             # 最大辩论轮数
}

graph = BaziAnalysisGraph(
    config=config,
    llm_provider="siliconflow",
    llm_model="deepseek-ai/DeepSeek-V3",
    base_url="https://api.siliconflow.cn/v1"
)
```

## 输出格式

分析结果包含以下部分：

1. **出生信息** - 原始输入信息
2. **核心人格** - 日主+主导十神，MBTI/大五人格翻译
3. **优势与成长路径** - 基于用神的成长建议
4. **阴影面与整合** - 基于忌神的阴影整合
5. **当前人生阶段** - 基于大运的当前状态
6. **传统命理智慧** - 传统命理视角
7. **现代心理学翻译** - 心理学框架解读
8. **成长建议** - 具体可操作的建议
9. **伦理说明** - 参考工具声明

## 伦理边界

### 能说的
- 人格特质和行为倾向
- 优势和成长方向
- 人生阶段的可能主题
- "倾向"和"可能性"（不是"注定"）

### 不能说的
- 具体的死亡、灾祸预测
- 绝对化的判断（"你一定会..."）
- 婚姻/感情的对错判断
- 替用户做人生重大决定

### 表达原则
1. 始终用"倾向"而非"注定"
2. 强调人的主观能动性
3. 八字是参考，不是命运判决书
4. 心理学翻译只是帮助理解的工具
5. 遇到严重心理问题，建议寻求专业心理咨询

## 项目结构

```
bazi-trading-agents/
├── bazi_agents/              # 智能体实现
│   ├── __init__.py
│   ├── chart_calculator.py
│   ├── day_master_analyst.py
│   ├── ten_gods_analyst.py
│   ├── pattern_analyst.py
│   ├── useful_god_analyst.py
│   ├── luck_cycle_analyst.py
│   ├── traditional_analyst.py
│   ├── psychology_analyst.py
│   └── comprehensive_analyst.py
├── bazi_graph/               # 图编排
│   ├── __init__.py
│   └── bazi_analysis_graph.py
├── utils/                    # 工具类
│   ├── __init__.py
│   ├── bazi_states.py
│   └── memory.py
├── memory/                   # 记忆存储
├── results/                  # 分析结果
├── __init__.py
├── requirements.txt
├── test_bazi_analysis.py
└── README.md
```

## 技术栈

- **LangChain**: LLM编排框架
- **LangGraph**: 多智能体图编排
- **OpenAI/Anthropic API**: LLM提供商
- **SiliconFlow**: 国内LLM提供商

## 灵感来源

本框架灵感来自：
- [TradingAgents](https://github.com/TauricResearch/TradingAgents) - 多智能体金融交易框架
- 传统命理学经典：《渊海子平》《三命通会》《滴天髓》《子平真诠》《穷通宝鉴》《神峰通考》
- 现代心理学：Carl Jung、Big Five、MBTI、Erikson、积极心理学

## 许可证

MIT License

## 作者

Wu Zhongpei (吴忠佩)

## 版本

0.1.0 - 初始版本
