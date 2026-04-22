# Bazi Trading Agents - 快速开始指南

## 5分钟快速上手

### 1. 安装依赖

```bash
cd ~/projects/bazi-trading-agents
pip install -r requirements.txt
```

### 2. 验证安装

```bash
python3 test_imports.py
```

如果看到 "All imports and basic tests passed!" 说明安装成功。

### 3. 配置LLM提供商

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置你的LLM提供商：

#### 使用SiliconFlow（推荐，国内访问快）
```env
LLM_PROVIDER=siliconflow
LLM_MODEL=deepseek-ai/DeepSeek-V3
LLM_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_API_KEY=your_api_key_here
```

#### 使用OpenAI
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
OPENAI_API_KEY=your_api_key_here
```

#### 使用Anthropic
```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229
ANTHROPIC_API_KEY=your_api_key_here
```

### 4. 运行测试分析

```bash
python3 test_bazi_analysis.py
```

这将使用你的八字（1990年9月5日8:00，男）进行测试分析。

### 5. 查看结果

分析结果会：
1. 在终端输出
2. 保存到 `results/test_analysis_output.txt`
3. 保存详细状态到 `results/bazi_analysis_*.json`

## 代码示例

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

### 自定义配置

```python
from bazi_graph import BaziAnalysisGraph

# 自定义配置
config = {
    "memory_dir": "./my_memory",
    "results_dir": "./my_results",
    "max_debate_rounds": 5,  # 增加辩论轮数
}

graph = BaziAnalysisGraph(
    config=config,
    llm_provider="siliconflow",
    llm_model="deepseek-ai/DeepSeek-V3",
    base_url="https://api.siliconflow.cn/v1",
    debug=False  # 关闭调试模式
)

# 运行分析
birth_info = "1995年3月15日14:30，女，农历"
final_state, final_analysis = graph.analyze(birth_info)
```

### 访问详细状态

```python
from bazi_graph import BaziAnalysisGraph

graph = BaziAnalysisGraph(
    llm_provider="siliconflow",
    llm_model="deepseek-ai/DeepSeek-V3",
    base_url="https://api.siliconflow.cn/v1"
)

final_state, final_analysis = graph.analyze("1990年9月5日8:00，男，农历")

# 访问各个分析报告
print("命盘报告:", final_state["chart_report"])
print("日主分析:", final_state["day_master_report"])
print("十神分析:", final_state["ten_gods_report"])
print("格局分析:", final_state["pattern_report"])
print("用神分析:", final_state["useful_god_report"])
print("大运分析:", final_state["luck_cycle_report"])

# 访问辩论历史
print("传统命理师观点:", final_state["bazi_debate_state"]["traditional_history"])
print("心理学分析师观点:", final_state["bazi_debate_state"]["psychology_history"])
```

## 常见问题

### Q: 如何获取API密钥？

**SiliconFlow**: 访问 https://siliconflow.cn/ 注册账号

**OpenAI**: 访问 https://platform.openai.com/ 注册账号

**Anthropic**: 访问 https://console.anthropic.com/ 注册账号

### Q: 分析需要多长时间？

取决于：
- LLM提供商的响应速度
- 网络连接
- 辩论轮数（默认3轮）

通常需要2-5分钟。

### Q: 如何提高分析质量？

1. 增加辩论轮数：`config["max_debate_rounds"] = 5`
2. 使用更强大的模型：如 `gpt-4` 或 `claude-3-opus`
3. 提供更详细的出生信息（包括出生地点）

### Q: 记忆系统有什么用？

记忆系统让智能体可以从历史分析中学习，提高后续分析的质量。记忆存储在 `memory/` 目录下。

### Q: 如何清理记忆？

```python
from utils import BaziAnalysisMemory

config = {"memory_dir": "./memory"}
memory = BaziAnalysisMemory("traditional_memory", config)
memory.clear_old_memories(days=30)  # 清理30天前的记忆
```

## 下一步

- 阅读 [README.md](README.md) 了解更多细节
- 阅读 [PROJECT.md](PROJECT.md) 了解项目架构
- 查看 [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md) 了解已完成的工作

## 获取帮助

如果遇到问题：
1. 检查 `.env` 文件配置是否正确
2. 确认API密钥有效
3. 检查网络连接
4. 查看错误日志

祝使用愉快！
