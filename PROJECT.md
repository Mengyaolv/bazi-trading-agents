# Bazi Trading Agents - 项目文档

## 项目概述

基于TradingAgents架构的八字（四柱）分析多智能体框架，结合传统命理学与现代心理学。

## 创建时间

2026-04-22

## 项目目标

1. 创建一个多智能体八字分析系统
2. 结合传统命理智慧与现代心理学
3. 提供可扩展的架构，便于添加新的分析维度
4. 实现智能体之间的辩论机制，提升分析质量

## 技术架构

### 智能体架构

9个专业智能体，分为3个阶段：

#### 分析阶段（6个智能体）

1. 命盘计算师 - 四柱排盘 + 大运计算
2. 日主分析师 - 日主强弱分析
3. 十神分析师 - 十神分布与组合效应
4. 格局分析师 - 格局判断与高低评估
5. 用神分析师 - 四法取用（扶抑/调候/通关/病药）
6. 大运分析师 - 大运趋势与人生阶段

#### 辩论阶段（2个智能体）

7. 传统命理师 - 传统命理视角
8. 心理学分析师 - 现代心理学视角

#### 综合阶段（1个智能体）

9. 综合分析师 - 最终综合分析

### 技术栈

- **LangChain**: LLM编排框架
- **LangGraph**: 多智能体图编排
- **OpenAI/Anthropic API**: LLM提供商
- **SiliconFlow**: 国内LLM提供商

## 文件结构

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
├── .env.example
├── .gitignore
├── README.md
└── PROJECT.md
```

## 使用方法

### 安装依赖

```bash
cd ~/projects/bazi-trading-agents
pip install -r requirements.txt
```

### 运行测试

```bash
python test_bazi_analysis.py
```

### 代码示例

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

## 配置选项

### LLM提供商

- **SiliconFlow**: `llm_provider="siliconflow"`
- **OpenAI**: `llm_provider="openai"`
- **Anthropic**: `llm_provider="anthropic"`

### 配置参数

```python
config = {
    "memory_dir": "./memory",
    "results_dir": "./results",
    "max_debate_rounds": 3,
}
```

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

## 灵感来源

- [TradingAgents](https://github.com/TauricResearch/TradingAgents) - 多智能体金融交易框架
- 传统命理学经典：《渊海子平》《三命通会》《滴天髓》《子平真诠》《穷通宝鉴》《神峰通考》
- 现代心理学：Carl Jung、Big Five、MBTI、Erikson、积极心理学

## 后续计划

### Phase 1: 基础功能（已完成）

- [X] 创建9个专业智能体
- [X] 实现多智能体图编排
- [X] 实现记忆系统
- [X] 创建测试脚本

### Phase 2: 优化改进

- [X] 优化prompt，提升分析质量
- [ ] 添加更多LLM提供商支持
- [X] 实现更智能的记忆检索
- [X] 添加分析质量评估

### Phase 3: 功能扩展

- [X] 添加Web界面
- [X] 添加批量分析功能
- [X] 添加可视化功能
- [X] 添加导出功能（PDF、Word等）

### Phase 4: 部署上线

- [ ] 部署到服务器
- [ ] 添加API接口
- [ ] 添加用户认证
- [ ] 添加付费功能

## 相关项目

- ~/projects/bazi-analysis-system/ - 八字分析系统（SKILL.md）
- ~/projects/bazi-personality-test/ - 八字人格测试
- ~/TradingAgents/ - TradingAgents框架

## 作者

Wu Zhongpei (吴忠佩)

## 版本

0.1.0 - 初始版本（2026-04-22）
