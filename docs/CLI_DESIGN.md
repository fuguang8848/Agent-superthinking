# 超思考 CLI 设计文档

> 版本：v6.0.0
> 状态：草案
> 日期：2026-06-05

---

## 一、设计目标

### 1.1 核心原则

| 原则 | 说明 |
|------|------|
| **简洁性** | 用户一行命令即可启动深度分析 |
| **灵活性** | 支持单专家、多专家、自定义组合 |
| **渐进式** | 新手用默认配置，专家可精细调优 |
| **可扩展** | 支持插件式新增专家和方法论 |

### 1.2 用户体验愿景

```
# 新手体验（一行命令启动）
$ think "AI会不会取代人类？"

# 专家体验（精确控制）
$ think analyze --experts=socrates,confucius --methods=bayesian,gametheory --rounds=3 "AI会不会取代人类？"
```

---

## 二、CLI 命令结构

### 2.1 主命令

```bash
think [subcommand] [options] [question]
```

| 子命令 | 说明 | 示例 |
|--------|------|------|
| `analyze` | 启动多专家圆桌辩论（默认） | `think analyze "问题"` |
| `list` | 列出可用专家和方法论 | `think list experts` |
| `info` | 查看专家/方法论详情 | `think info socrates` |
| `init` | 初始化项目配置 | `think init` |
| `config` | 管理配置文件 | `think config set default_rounds 5` |

### 2.2 全局选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--experts` | 指定参与的专家列表 | 自动路由 |
| `--methods` | 指定使用的方法论工具 | 空 |
| `--rounds` | 最大辩论轮次 | 5 |
| `--format` | 输出格式 (`text`/`json`/`markdown`) | `text` |
| `--model` | 指定 LLM 模型 | `auto` |
| `--verbose` | 显示详细日志 | false |
| `--help` | 显示帮助 | - |

---

## 三、核心子命令详解

### 3.1 `think analyze`

启动多专家圆桌辩论。

#### 基本用法

```bash
# 自动路由（系统根据问题自动选择专家）
$ think analyze "AI会不会取代人类？"

# 指定专家
$ think analyze --experts=socrates,confucius,einstein "AI会不会取代人类？"

# 指定专家和方法论
$ think analyze --experts=socrates,confucius --methods=bayesian,gametheory "AI会不会取代人类？"

# 自定义轮次
$ think analyze --experts=socrates --rounds=3 "什么是善？"
```

#### 输出示例

```
═══════════════════════════════════════════════════════════════
  超思考 v6 · 多专家圆桌辩论
═══════════════════════════════════════════════════════════════

问题：AI会不会取代人类？

参与者：苏格拉底、孔子、爱因斯坦、孙子
方法论：博弈论、贝叶斯统计

───────────────────────────────────────────────────────────────
第 1 轮 · 并行发言
───────────────────────────────────────────────────────────────

【苏格拉底】
关于AI会不会取代人类，从辩证的角度来看，我认为这个问题本身
需要我们先澄清"取代"的含义。如果指的是完全替代，那么我认为
这是不可能的，因为...

【孔子】
论及此事，吾以为当观其"用"之道。AI者，器也；器可助人，亦可
害人，端在用之者之心...

───────────────────────────────────────────────────────────────
第 2 轮 · 辩论
───────────────────────────────────────────────────────────────

## 论点菜单
1. 苏格拉底认为"取代"需要澄清定义
2. 孔子认为AI是器，关键在用者之心
3. 爱因斯坦认为技术进步不可阻挡

【苏格拉底】
针对爱因斯坦关于"技术进步不可阻挡"的论点，我部分认同，但...
```

#### 返回值

| 代码 | 说明 |
|------|------|
| 0 | 分析完成 |
| 1 | 分析失败（LLM调用错误） |
| 2 | 参数错误 |
| 130 | 用户中断（Ctrl+C） |

### 3.2 `think list`

列出可用资源。

```bash
# 列出所有专家
$ think list experts

# 列出所有方法论
$ think list methods

# 按领域筛选
$ think list experts --domain=philosophy

# 搜索专家
$ think list experts --search=辩证

# JSON 输出
$ think list experts --format=json
```

#### 输出示例

```
═══════════════════════════════════════════════════════════════
  可用专家（52 位）
═══════════════════════════════════════════════════════════════

哲学领域 (12)
  ✓ socrates        苏格拉底      辩证法 · 自知无知
  ✓ plato           柏拉图        理念论 · 洞穴隐喻
  ✓ aristotle       亚里士多德    形而上学 · 三段论
  ...

科学领域 (6)
  ✓ einstein        爱因斯坦      相对论 · 思想实验
  ✓ curie           居里夫人      放射性 · 勤奋
  ...

───────────────────────────────────────────────────────────────
使用 --info <名称> 查看详情
───────────────────────────────────────────────────────────────
```

### 3.3 `think info`

查看专家或方法论详情。

```bash
$ think info socrates

═══════════════════════════════════════════════════════════════
  专家详情：苏格拉底 (socrates)
═══════════════════════════════════════════════════════════════

领域：哲学
类型：人物型
核心方法：辩证法、问答法
关键词：自知无知、美德即知识、未经审视的人生不值得过

简介：
古希腊哲学家，西方哲学的奠基人之一。以问答法著称，
通过不断追问帮助人们澄清概念、发现真理。

适用场景：
• 概念辨析和定义
• 价值观追问
• 苏格拉底式批判性思考

═══════════════════════════════════════════════════════════════
```

### 3.4 `think init`

初始化项目配置。

```bash
$ think init

# 指定配置路径
$ think init --config=./my-think.yaml

# 交互式配置
$ think init --interactive
```

#### 生成配置示例

```yaml
# .think.yaml
version: "1.0"

defaults:
  experts: []  # 空表示自动路由
  methods: []
  rounds: 5
  format: text
  model: auto

experts:
  enabled:
    - socrates
    - confucius
  disabled: []

methods:
  enabled:
    - bayesian
  disabled: []

llm:
  provider: openai  # openai / anthropic / local
  model: gpt-4
  api_key: ${OPENAI_API_KEY}
```

---

## 四、交互模式

### 4.1 问答模式（REPL）

```bash
$ think repl

═══════════════════════════════════════════════════════════════
  超思考 v6 · 交互模式
═══════════════════════════════════════════════════════════════

输入您的问题，或输入以下命令：
  list    - 列出可用专家
  experts - 切换专家配置
  methods - 切换方法论配置
  config  - 查看/修改配置
  exit    - 退出

───────────────────────────────────────────────────────────────
> AI会不会取代人类？

启动多专家圆桌辩论...

...
```

### 4.2 流式输出

```bash
$ think analyze --stream "AI会不会取代人类？"
```

专家发言实时流式输出，每轮到主持人整理论点菜单时暂停显示。

---

## 五、配置文件

### 5.1 配置加载顺序

```
命令行参数 > 环境变量 > 项目配置 (.think.yaml) > 用户配置 (~/.think.yaml) > 默认值
```

### 5.2 环境变量

| 变量 | 说明 |
|------|------|
| `THINK_API_KEY` | LLM API Key |
| `THINK_MODEL` | 默认模型 |
| `THINK_CONFIG` | 配置文件路径 |

### 5.3 配置文件格式

```yaml
# .think.yaml
version: "1.0"

# 默认配置
defaults:
  experts: []
  methods: []
  rounds: 5
  format: text
  model: auto

# 专家配置
experts:
  enabled: []
  disabled: []

# 方法论配置  
methods:
  enabled: []
  disabled: []

# LLM 配置
llm:
  provider: openai
  model: gpt-4
  temperature: 0.7
  max_tokens: 2000

# 输出配置
output:
  color: true
  emoji: true
  verbosity: normal
```

---

## 六、扩展接口

### 6.1 添加自定义专家

```bash
# 注册本地专家
$ think expert add ./my-expert/

# 从 URL 安装
$ think expert install https://example.com/expert.zip
```

### 6.2 添加自定义方法论

```bash
$ think method add ./my-method/
```

### 6.3 插件系统

```yaml
# .think.yaml
plugins:
  - name: custom-experts
    path: ./plugins/custom-experts
    enabled: true
```

---

## 七、错误处理

### 7.1 错误代码

| 代码 | 含义 | 处理建议 |
|------|------|---------|
| E001 | 专家不存在 | 使用 `think list experts` 查看可用专家 |
| E002 | 方法论不存在 | 使用 `think list methods` 查看可用方法论 |
| E003 | 配置解析错误 | 检查 YAML 格式 |
| E004 | LLM API 错误 | 检查 API Key 和网络连接 |
| E005 | 辩论超时 | 减少轮次或使用更多方法论 |
| E006 | 无效参数 | 查看帮助信息 |

### 7.2 错误输出格式

```
[ERROR] E001: 专家不存在
  专家 "xxx" 未找到。
  
  使用 `think list experts` 查看可用专家列表。
  
  提示：专家名称不区分大小写，可使用简称（如 socrates）
```

---

## 八、进度指示器

### 8.1 辩论进度

```
[1/5] 第 1 轮：并行发言 ████████████░░░░░░░░░░░░ 40%
  正在等待专家发言...
  苏格拉底 ✓  孔子 ✓  爱因斯坦 ●  孙子 ○
```

### 8.2 转轮动画

```
[2/5] 第 2 轮：辩论中
  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░ 40%
  苏格拉底 ← 针对 → 爱因斯坦
  孔子 ← 补充 → 全员
```

---

## 九、API 接口（供集成）

### 9.1 Python SDK

```python
from super_thinking import DebateSession

session = DebateSession(
    question="AI会不会取代人类？",
    experts=["socrates", "confucius"],
    methods=["bayesian"],
    rounds=5
)

for event in session.stream():
    if event.type == "round_start":
        print(f"第 {event.round} 轮开始")
    elif event.type == "expert_speak":
        print(f"{event.expert}: {event.content}")
    elif event.type == "round_end":
        print(f"论点菜单: {event.menu}")
    elif event.type == "debate_end":
        print(f"结论: {event.conclusion}")
```

### 9.2 HTTP API（可选）

```bash
# 启动服务器
$ think serve --port=8080

# 发送请求
$ curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"question": "AI会不会取代人类？", "experts": ["socrates"]}'
```

---

## 十、实现计划

### Phase 1: MVP（当前）

- [x] 命令行参数解析
- [ ] `analyze` 子命令核心逻辑
- [ ] `list` 子命令
- [ ] 基础错误处理
- [ ] 配置文件支持

### Phase 2: 增强

- [ ] `info` 子命令
- [ ] REPL 交互模式
- [ ] 流式输出
- [ ] 进度指示器

### Phase 3: 扩展

- [ ] 插件系统
- [ ] HTTP API
- [ ] Python SDK 完善
- [ ] VS Code 插件

---

## 附录 A：命令速查表

| 命令 | 说明 |
|------|------|
| `think "问题"` | 快速分析 |
| `think analyze "问题"` | 标准分析 |
| `think list experts` | 列出专家 |
| `think list methods` | 列出方法论 |
| `think info <名称>` | 查看详情 |
| `think init` | 初始化配置 |
| `think repl` | 交互模式 |
| `think --help` | 显示帮助 |

---

_文档版本：v6.0.0 · 2026-06-05_
