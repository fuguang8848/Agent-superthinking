# 超思考用户指南

> 版本：v6.0.0
> 状态：草案
> 日期：2026-06-05

---

## 目录

1. [快速开始](#快速开始)
2. [核心概念](#核心概念)
3. [基础用法](#基础用法)
4. [进阶技巧](#进阶技巧)
5. [常见场景](#常见场景)
6. [故障排除](#故障排除)
7. [常见问题](#常见问题)

---

## 快速开始

### 安装

```bash
# 使用 pip 安装
pip install super-thinking

# 或使用 uv（更快）
uv pip install super-thinking
```

### 首次使用

```bash
# 验证安装
$ think --version
super-thinking v6.0.0

# 初始化配置
$ think init
配置文件已创建：~/.think.yaml
```

### 快速分析

```bash
# 一句话启动分析
$ think "AI会不会取代人类？"
```

---

## 核心概念

### 什么是超思考？

超思考是一个**多专家圆桌辩论系统**。当你提出一个问题时，系统会：

1. **路由分析** - 判断你的问题涉及哪些领域
2. **邀请专家** - 选择相关领域的专家参与辩论
3. **圆桌辩论** - 专家们围绕问题展开真实交锋
4. **综合结论** - 融合各方观点，给出平衡的分析

### 专家类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **人物型** | 蒸馏自历史人物的思维方式 | 苏格拉底、孔子、爱因斯坦 |
| **方法论型** | 整合自学术框架和学派 | 博弈论、贝叶斯统计、设计思维 |

### 辩论流程

```
问题输入
    ↓
第 1 轮：各专家独立陈述初始观点
    ↓
第 2 轮：针对上一轮论点展开辩论
    ↓
第 3 轮：深化分歧、寻找共识
    ↓
...
    ↓
收敛或达到最大轮次 → 最终结论
```

---

## 基础用法

### 命令行基本结构

```bash
think [子命令] [选项] "你的问题"
```

### 最简单的用法

```bash
# 直接输入问题（系统自动选择专家）
$ think "什么是幸福？"

# 使用 analyze 子命令（效果相同）
$ think analyze "什么是幸福？"
```

### 指定专家

```bash
# 单个专家
$ think analyze --experts=socrates "什么是幸福？"

# 多个专家
$ think analyze --experts=socrates,confucius,einstein "科技发展的伦理边界在哪里？"

# 查看可用专家
$ think list experts
```

### 使用方法论

方法论是检验工具，可以帮助专家更严谨地分析问题。

```bash
# 添加方法论工具
$ think analyze --experts=socrates --methods=bayesian "AI是否有意识？"

# 查看可用方法论
$ think list methods
```

### 调整辩论轮次

```bash
# 快速分析（2轮）
$ think analyze --experts=socrates --rounds=2 "什么是善？"

# 深度分析（最多10轮）
$ think analyze --experts=socrates,confucius,mencius --rounds=10 "人性本善还是本恶？"
```

### 选择输出格式

```bash
# 文本格式（默认）
$ think analyze --format=text "问题"

# JSON 格式（适合程序处理）
$ think analyze --format=json "问题"

# Markdown 格式（适合文档使用）
$ think analyze --format=markdown "问题"
```

---

## 进阶技巧

### 交互模式

启动交互式对话，可以连续提问：

```bash
$ think repl

═══════════════════════════════════════════════════════════════
  超思考 v6 · 交互模式
═══════════════════════════════════════════════════════════════

> AI会不会取代人类？
启动辩论...

[辩论过程...]

> 第二个问题：996工作制合理吗？
启动辩论...

[辩论过程...]
```

### 流式输出

实时看到专家发言：

```bash
$ think analyze --stream "量子计算的未来"
```

### 配置默认专家

在 `~/.think.yaml` 中设置默认专家：

```yaml
defaults:
  experts:
    - socrates
    - confucius
  methods:
    - bayesian
  rounds: 3
```

以后直接输入问题即可使用这些默认配置。

### 环境变量

```bash
# 设置 API Key
export THINK_API_KEY="sk-xxxx"

# 设置默认模型
export THINK_MODEL="gpt-4"

# 使用配置
$ think analyze "问题"
```

---

## 常见场景

### 场景 1：哲学思辨

```bash
$ think analyze --experts=socrates,confucius,mencius "人性本善还是本恶？"
```

**适用专家**：苏格拉底（辩证）、孔子（仁义）、孟子（性善论）、荀子（性恶论）

### 场景 2：科技决策

```bash
$ think analyze --experts=einstein,curie,turing --methods=gametheory,ethics "是否应该暂停AI训练？"
```

**适用专家**：爱因斯坦（物理直觉）、居里夫人（科学精神）、图灵（计算思维）

**适用方法论**：博弈论（利弊分析）、伦理学（价值判断）

### 场景 3：商业策略

```bash
$ think analyze --experts=sunwu,zhangfei,chengyu --methods=swot,game-theory "公司是否应该进入新市场？"
```

**适用专家**：孙子（军事策略）、张飞（风险决策）、程昱（谋略）

**适用方法论**：SWOT分析、博弈论

### 场景 4：文学分析

```bash
$ think analyze --experts=shakespeare,tolstoy,lu_xun --methods=narratology,rhetoric "分析鲁迅《狂人日记》的文学价值"
```

**适用专家**：莎士比亚（戏剧）、托尔斯泰（史诗）、鲁迅（现实主义）

**适用方法论**：叙事学、修辞学

### 场景 5：伦理困境

```bash
$ think analyze --experts=confucius,kant,mill --methods=ethics,philosophy "自动驾驶撞人应该如何决策？"
```

**适用专家**：孔子（儒家伦理）、康德（义务论）、密尔（功利主义）

**适用方法论**：伦理学、政治哲学

### 场景 6：科学探索

```bash
$ think analyze --experts=einstein,bohr,curie --methods=scientific-method,probability "量子力学应该如何解释？"
```

**适用专家**：爱因斯坦（相对论）、玻尔（哥本哈根诠释）、居里夫人（实验精神）

**适用方法论**：科学方法论、概率论

---

## 故障排除

### 问题：命令未找到

```bash
# 错误
$ think: command not found

# 解决：确保 PATH 包含 Python bin 目录
# 或使用完整路径
$ python -m super_thinking "问题"
```

### 问题：API Key 错误

```bash
# 错误
[ERROR] E004: LLM API 错误 - Invalid API key

# 解决：检查 API Key
export THINK_API_KEY="sk-xxxx"
```

### 问题：专家未找到

```bash
# 错误
[ERROR] E001: 专家不存在

# 解决：查看正确名称
$ think list experts --search=苏格拉底
```

### 问题：分析超时

```bash
# 错误
[ERROR] E005: 辩论超时

# 解决：减少轮次或专家数量
$ think analyze --experts=socrates --rounds=2 "问题"
```

### 问题：输出乱码

```bash
# 解决：设置 UTF-8 编码
export LANG=en_US.UTF-8
$ think analyze "问题"
```

---

## 常见问题

### Q: 超思考和普通 AI 问答有什么区别？

**A**: 普通 AI 问答是由单一 AI 生成答案；超思考是由多个具有不同思维方式的"专家"进行真实的辩论交锋，最后综合各方观点给出更全面、更平衡的分析。

### Q: 如何选择专家？

**A**: 
- **自动选择**：不指定专家时，系统会根据问题自动路由
- **手动选择**：如果你知道问题涉及哪些领域，可以手动指定
- **组合建议**：哲学+科学=深度思辨，商业+军事=策略分析

### Q: 方法论是什么？必须使用吗？

**A**: 方法论是检验工具，如贝叶斯统计、博弈论等。**不是必须**，但使用可以让分析更严谨。可以先不用，熟悉后再逐步添加。

### Q: 辩论多少轮合适？

**A**: 
- **2-3 轮**：快速分析、简单问题
- **5 轮**：标准分析（默认）
- **7-10 轮**：复杂问题、深度探讨

### Q: 可以自定义专家吗？

**A**: 可以！你可以通过创建自定义 SKILL.md 或 schema.json 来添加自己的专家。具体方法见 CONTRIBUTING.md。

### Q: 分析结果保存在哪里？

**A**: 默认情况下结果只输出到终端。如需保存，可以使用输出重定向：

```bash
$ think analyze "问题" > result.md
```

### Q: 支持哪些 LLM？

**A**: 当前支持 OpenAI GPT 系列和 Anthropic Claude 系列。更多模型支持正在开发中。

---

## 下一步

- 📖 查看 [CLI 设计文档](./CLI_DESIGN.md) - 了解完整命令行选项
- 🤝 查看 [贡献指南](./CONTRIBUTING.md) - 如何添加自定义专家
- 💻 查看 [示例](../examples/) - 实际使用案例

---

_文档版本：v6.0.0 · 2026-06-05_
