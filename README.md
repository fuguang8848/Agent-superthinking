# Agent-Superthinking

> 多维度思考框架：输入问题 → 路由层判断 → 用户选择轨别 → 并行分析 → 冲突检测 → 综合报告。

**面向 AI 框架设计**：模块化、可扩展、按需加载，适合集成到各类 AI Agent 系统。

**[English](./README_EN.md) | [简体中文](./README.md)**

## 核心架构

```
用户问题
    ↓
┌──────────────────────────────────────┐
│  路由层（Router）                    │
│  - 读取 INDEX_PEOPLE.md（人物索引）  │
│  - 读取 INDEX_METHODS.md（方法论索引）│
│  - 判断涉及哪些专家团                 │
└──────────────────────────────────────┘
    ↓
┌──────────────────────────────────────┐
│  用户选择轨别：                       │
│  [1] 人物型（历史人物视角）          │
│  [2] 方法论型（学术框架视角）        │
│  [3] 双轨组合（最全面）              │
│  [4] 自定义                          │
└──────────────────────────────────────┘
    ↓
被选中的专家/框架并行分析
    ↓
┌──────────────────────────────────────┐
│  融合层（Fusion）                    │
│  - ConflictDetector 冲突检测         │
│  - ConsensusFinder 共识提炼          │
│  - Formatter 结构化综合报告           │
│  (fusion/conflict.py + consensus.py   │
│   + formatter.py, 5 files)            │
└──────────────────────────────────────┘
```


## 核心组件 (V 6/19 19:19 L1 verify)

| 组件 | 文件 | 类 | 说明 |
|---|---|---|---|
| **Router** | `core/router.py` | `class Router` | 路由层 (读取 INDEX_PEOPLE.md + INDEX_METHODS.md) |
| **Jury** | `core/jury.py:29` | `class JuryResult` | 评审结果 |
| **Expert** | `v6/expert_statement.py` | `class ExpertStatement` | 专家陈述 |
| **ConflictDetector** | `fusion/conflict.py` | `class ConflictDetector` | 多视角冲突检测 |
| **ConsensusFinder** | `fusion/consensus.py` | `class ConsensusFinder` | 共识提炼 |
| **Formatter** | `fusion/formatter.py` | `class Formatter` | 综合报告格式化 |

## 双轨专家系统

### 人物型（People）

蒸馏自真实历史人物，捕捉其思维方式。适合：价值观判断、决策启发、人性洞察。

**人物统计：140 expert files / 12 领域** (V 6/19 19:19 L1 verify, 实际 schema.json 数)

| 领域 | 人数 | 代表人物 |
|------|------|---------|
| 哲学 | 12 | 苏格拉底、柏拉图、尼采、庄子、康德、马克思... |  |
| 科学 | 6 | 爱因斯坦、玻尔、图灵、居里夫人、麦克斯韦、薛定谔 |
| 心理/社会 | 6 | 弗洛伊德、荣格、福柯、米德、埃里克森、罗杰斯 |
| 经济/历史 | 6 | 凯恩斯、哈耶克、亚当·斯密、稻盛和夫、基辛格、李光耀 |
| 文学 | 13 | 莎士比亚、托尔斯泰、鲁迅、卡夫卡、博尔赫斯... |
| 军事/策略 | 2 | 孙子、克劳塞维茨 |
| 数学/逻辑 | 3 | 欧几里得、高斯、哥德尔 |
| 宗教/伦理 | 2 | 佛陀、王阳明 |
| 战略决策 | 4 | 马斯克、芒格、纳瓦尔、乔布斯 |
| 风险/认知 | 7 | 塔勒布、费曼、达尔文、元思考、MSA... |

### 方法论型（Methods）

整合自成熟学术框架/学派，无单一人物代表。适合：分析工具、量化方法、系统建模。

**方法论统计：19 个**

| 类别 | 框架 | 核心贡献 |
|------|------|---------|
| 复杂系统 | 复杂性科学、网络科学 | 涌现、自组织、非线性 |
| 信息计算 | 信息论、量子信息、计算理论 | 熵、叠加、算法复杂度 |
| 决策博弈 | 博弈论、系统论 | 纳什均衡、反馈循环 |
| 认知学习 | 认知科学、贝叶斯统计、演化学 | 双过程、贝叶斯推断、选择 |
| 分析推理 | 批判性思维、统计学 | 逻辑谬误、正则化 |
| 设计人本 | 设计思维、叙事学、修辞学、诗学、文学批评 | 共情、英雄旅程、说服 |
| 优化控制 | 运筹学、控制论 | 线性规划、反馈控制 |
| 语言意义 | 语言学、现象学 | 语法、悬置 |
| 哲学方法 | 分析哲学、政治哲学 | 语言分析、社会契约 |
| 社会政治 | 政治哲学、法学、伦理学 | 正义、权利、义务 |
| 传播管理 | 传播学、管理学 | 议程设置、SWOT |
| 社会科学 | 人类学、社会学、美学 | 民族志、制度、美感 |

---

## 跨框架兼容性

### 三种格式支持

| 格式 | 文件 | 用途 |
|------|------|------|
| **SKILL.md** | `experts/*/SKILL.md` | OpenClaw Skill 直接使用 |
| **schema.json** | `experts/*/schema.json` | 任何框架 JSON 解析即用 |
| **INDEX** | `INDEX_PEOPLE.md`, `INDEX_METHODS.md` | 路由层索引 |

### JSON Schema（通用格式）

每个专家同时生成 `schema.json`，任何 AI 框架都能解析：

```json
{
  "name": "socrates-perspective",
  "type": "people",
  "domain": "philosophy",
  "displayName": "苏格拉底",
  "keywords": ["苏格拉底", "辩证法", "自知无知"],
  "models": [...],
  "heuristics": [...],
  "dna": {...},
  "limits": [...],
  "source": {...},
  "version": "1.0.0"
}
```

详细 Schema 定义见 [SCHEMA.md](./SCHEMA.md)

### 框架适配示例

#### OpenClaw（原生支持）
```markdown
> 帮我分析：AI会不会取代人类？
```

#### LangChain
```python
from langchain.tools import Tool
import json

# 加载任意专家
with open("experts/gametheory-perspective/schema.json") as f:
    expert = json.load(f)

tool = Tool(
    name=expert["displayName"],
    func=lambda x: analyze_with_expert(x, expert),
    description=f"Use {expert['displayName']} perspective"
)
```

#### LlamaIndex
```python
from llama_index.tools import FunctionTool
import json

with open("experts/bayesian-perspective/schema.json") as f:
    schema = json.load(f)

tool = FunctionTool.from_defaults(
    fn=analyze_bayesian,
    name=schema["name"],
    description=f"Bayesian reasoning tool"
)
```

#### Claude Code
```bash
# 读取专家 JSON
cat experts/socrates-perspective/schema.json | jq '.models[]'
```

#### 自定义 Agent
```python
import json

def load_expert(name: str):
    with open(f"experts/{name}/schema.json") as f:
        return json.load(f)

socrates = load_expert("socrates-perspective")
for model in socrates["models"]:
    print(f"{model['name']}: {model['summary']}")
```

---

## AI 框架集成

### 方式一：OpenClaw Skill（推荐）

```markdown
> 帮我分析：AI会不会取代人类？

[路由器展示路由结果]
→ 用户选择轨别和粒度
→ 系统自动加载对应专家 SKILL.md
→ 并行分析 → 融合报告
```

触发词：`思考`、`分析`、`深度分析`、`多视角`

### 方式二：Python 包

```bash
pip install agent-superthinking
```

```python
from super_thinking import Router, Fusion, Registry

# 初始化
router = Router()
registry = Registry()
fusion = Fusion()

# 1. 路由
question = "AI会不会取代人类？"
routes = router.route(question)  # 返回涉及哪些专家团

# 2. 用户选择后，加载专家
selected = ["philosophy", "gametheory", "complexity"]
experts = registry.load(selected)  # 按需加载，不全量

# 3. 并行分析（各框架自行分析）
results = [expert.analyze(question) for expert in experts]

# 4. 融合报告
report = fusion.fuse(results)
print(report)
```

### 方式三：JSON Schema（任意框架）

```python
import json
from pathlib import Path

# 遍历所有专家
for schema_path in Path("experts").rglob("schema.json"):
    expert = json.loads(schema_path.read_text())
    print(f"{expert['displayName']}: {len(expert['models'])} models")
```

---

## 目录结构

```
Agent-superthinking/
├── SKILL.md                    # OpenClaw Skill 入口
├── INDEX_PEOPLE.md            # 人物索引（路由层读取）
├── INDEX_METHODS.md            # 方法论索引（路由层读取）
├── SCHEMA.md                  # JSON Schema 定义
├── README.md                  # 本文件
├── LICENSE                    # MIT
├── pyproject.toml             # Python 包配置
├── scripts/
│   └── sketch_to_json.py     # SKILL.md → JSON 转换脚本
├── src/super_thinking/        # Python 包源码
│   ├── __init__.py
│   ├── core/
│   │   ├── router.py         # 路由层
│   │   ├── registry.py        # 专家注册
│   │   └── jury.py            # 评审层
│   ├── fusion/
│   │   ├── conflict.py        # 冲突检测
│   │   ├── consensus.py       # 共识提炼
│   │   └── formatter.py       # 报告格式化
│   └── experts/               # 内置专家实现
│       └── ...
├── experts/
│   ├── people/                # 人物型专家（52位）
│   │   ├── philosophy/        # 12位
│   │   ├── science/           # 6位
│   │   ├── psychology/        # 6位
│   │   ├── economics/         # 6位
│   │   ├── literature/        # 13位
│   │   ├── military/          # 2位
│   │   ├── math/             # 3位
│   │   └── religion/           # 2位
│   │   └── <name>-perspective/
│   │       ├── SKILL.md       # OpenClaw Skill
│   │       └── schema.json    # JSON Schema（跨框架）
│   └── methods/               # 方法论型框架（19个）
│       └── <name>-perspective/
│           ├── SKILL.md       # OpenClaw Skill
│           └── schema.json    # JSON Schema（跨框架）
└── tests/
```

---

## 贡献指南

### 新增人物专家

1. 使用 nuwa-skill 蒸馏流程：
   ```bash
   # 安装女娲
   npm install -g @huashu/nuwa-skill
   
   # 蒸馏新人物
   nuwa distill <人物名>
   ```

2. 将生成的 SKILL.md 放入 `experts/people/<领域>/`
3. 运行转换脚本生成 JSON：
   ```bash
   python scripts/sketch_to_json.py
   ```
4. 更新 `INDEX_PEOPLE.md`

### 新增方法论框架

1. 在 `experts/methods/<name>-perspective/` 下创建 `SKILL.md`
2. 格式：见 [SCHEMA.md](./SCHEMA.md)
3. 运行转换脚本生成 JSON：
   ```bash
   python scripts/sketch_to_json.py
   ```
4. 更新 `INDEX_METHODS.md`

---

## 版本历史

| 版本 | 更新内容 |
|------|---------|
| v2.0 | 双轨系统上线：52人物 + 19方法论 + JSON Schema 跨框架支持 |
| v1.0 | 初始版本：18视角 |

---

## License

MIT

---

Agent-Superthinking_
