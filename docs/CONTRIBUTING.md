# 超思考贡献指南

> 版本：v6.0.0
> 状态：草案
> 日期：2026-06-05

---

## 欢迎贡献！

感谢你愿意为超思考项目做出贡献。本指南将帮助你了解如何贡献代码、文档和专家定义。

---

## 目录

1. [贡献类型](#贡献类型)
2. [开发环境](#开发环境)
3. [添加新专家](#添加新专家)
4. [添加新方法论](#添加新方法论)
5. [CLI 开发](#cli-开发)
6. [文档贡献](#文档贡献)
7. [代码规范](#代码规范)
8. [提交规范](#提交规范)
9. [审核流程](#审核流程)

---

## 贡献类型

我们欢迎以下类型的贡献：

| 类型 | 说明 | 难度 |
|------|------|------|
| **新专家** | 添加新的人物型专家 | 中 |
| **新方法论** | 添加新的方法论框架 | 中-高 |
| **CLI 功能** | 改进命令行工具 | 高 |
| **文档** | 改进文档、教程、示例 | 低 |
| **Bug 修复** | 修复已知问题 | 不等 |
| **测试** | 添加单元测试和集成测试 | 中 |

---

## 开发环境

### 克隆项目

```bash
git clone https://github.com/your-fork/super-thinking.git
cd super-thinking
```

### 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_router.py

# 带覆盖率
pytest --cov=src --cov-report=html
```

### 代码格式化

```bash
# 格式化代码
ruff format .

# 检查代码风格
ruff check .
```

---

## 添加新专家

### 专家结构

每个专家需要创建以下文件：

```
experts/people/<domain>/
├── <name>-perspective/
│   ├── SKILL.md          # OpenClaw Skill 格式
│   └── schema.json       # JSON Schema（跨框架支持）
└── INDEX.md              # 领域索引
```

### 示例：添加"庄子"专家

#### 1. 创建目录结构

```bash
mkdir -p experts/people/philosophy/zhuangzi-perspective
```

#### 2. 编写 SKILL.md

```markdown
# 庄子视角 (zhuangzi-perspective)

> 庄周梦蝶，不知周之梦为胡蝶与，胡蝶之梦为周与？

## 专家信息

| 属性 | 值 |
|------|-----|
| 名称 | 庄子 |
| 时代 | 战国（公元前369-前286） |
| 领域 | 哲学 |
| 学派 | 道家 |

## 思维方式

### 核心特质

- **相对主义**：一切都是相对的，没有绝对标准
- **齐物论**：万物平等，无贵贱之分
- **逍遥游**：追求精神自由，不为外物所累
- **无用之用**：看似无用的事物可能有最大价值

### 思考模式

```
1. 质疑前提 → 这个问题的前提是否成立？
2. 扩大视角 → 从更大的尺度看会怎样？
3. 相对化 → 这真的重要吗？从相对角度看呢？
4. 归自然 → 顺应自然本性，而非强行改变
```

### 关键词

```
齐物、逍遥、无为、相对、道法自然、无用之用
蝶梦、天籁、物化、天钧、坐忘
```

## 适用场景

### 适合的问题

- 人生意义与价值判断
- 竞争与成败的思考
- 社会规范与个人自由的冲突
- 成功与失败的辩证

### 不适合的问题

- 需要精确数据的分析
- 具体的操作建议

## 发言风格

### 语气特点

- 诗意、富有哲理
- 常用比喻和寓言
- 善于讲故事

### 常用句式

```
"子非鱼，安知鱼之乐？"
"天地与我并生，而万物与我为一。"
"夫大道不称，大辩不言..."
```

## 方法论整合

### 可调用的方法论

- 复杂性科学（理解系统性）
- 现象学（悬置判断）

## 局限与偏见

### 可能存在的盲点

- 过于超脱现实，缺乏可操作性
- 可能回避具体的价值判断
- 相对主义可能导致无法做决策

### 使用注意事项

- 需要结合实践性强的专家一起使用

---

_版本：1.0.0_
_更新：2026-06-05_
```

#### 3. 编写 schema.json

```json
{
  "name": "zhuangzi-perspective",
  "type": "people",
  "domain": "philosophy",
  "displayName": "庄子",
  "keywords": ["齐物", "逍遥", "无为", "相对主义", "道家"],
  "models": [
    {
      "name": "齐物论",
      "summary": "万物平等的哲学基础",
      "prompt": "从齐物论的角度分析..."
    },
    {
      "name": "逍遥游", 
      "summary": "追求精神自由的理想",
      "prompt": "从逍遥游的角度分析..."
    }
  ],
  "heuristics": [
    "质疑前提：这个问题的前提是什么？",
    "扩大视角：从更大的尺度看会怎样？",
    "相对化：站在对立方思考",
    "归自然：顺应本性而非强行改变"
  ],
  "dna": {
    "thinking_pattern": "相对主义",
    "expression_style": "诗意比喻",
    "core_belief": "道法自然"
  },
  "limits": [
    "缺乏可操作性",
    "回避具体价值判断"
  ],
  "source": {
    "text": "《庄子·内篇》",
    "reference": "内七篇：逍遥游、齐物论、养生主、人间世、德充符、大宗师、应帝王"
  },
  "version": "1.0.0"
}
```

#### 4. 更新领域索引

在 `experts/people/philosophy/INDEX.md` 中添加：

```markdown
## 庄子 (zhuangzi)

| 属性 | 值 |
|------|-----|
| ID | zhuangzi |
| 时代 | 战国 |
| 核心思想 | 齐物论、逍遥游 |
| 关键词 | 无为、相对、道法自然 |

[详细文档](./zhuangzi-perspective/SKILL.md)
```

### 专家质量标准

添加的专家必须满足以下标准：

| 标准 | 要求 |
|------|------|
| **准确性** | 专家描述必须符合历史事实 |
| **独特性** | 与现有专家有可区分的视角 |
| **完整性** | 包含 SKILL.md 和 schema.json |
| **可用性** | 在实际辩论中有独特价值 |
| **文档化** | 有清晰的适用场景和局限性说明 |

---

## 添加新方法论

### 方法论结构

```
experts/methods/
├── <name>-perspective/
│   ├── SKILL.md          # 方法论文档
│   └── schema.json       # JSON Schema
└── INDEX.md              # 方法论索引
```

### 示例：添加"博弈论"方法论

#### 1. 创建文件

```bash
mkdir -p experts/methods/gametheory-perspective
```

#### 2. 编写 SKILL.md

```markdown
# 博弈论视角 (gametheory-perspective)

> 博弈论研究决策者在相互影响的情况下的最优策略选择。

## 方法论信息

| 属性 | 值 |
|------|-----|
| 名称 | 博弈论 |
| 类型 | 方法论型 |
| 起源 | 数学、经济学 |
| 核心 | 策略互动、最优决策 |

## 核心概念

### 基础模型

- **囚徒困境**：个人最优不等于集体最优
- **纳什均衡**：各方都无法单方面改善的局面
- **零和博弈**：一方的收益等于另一方的损失
- **重复博弈**：长期关系改变策略选择

### 分析框架

```
1. 识别参与者：谁在做决策？
2. 确定收益：各方的收益函数是什么？
3. 分析策略：有哪些可能的策略组合？
4. 寻找均衡：是否存在稳定的策略组合？
5. 评估结果：均衡是否是最优的？
```

### 适用场景

- 商业竞争分析
- 国际关系研究
- 资源分配问题
- 激励机制设计

### 使用限制

- 假设理性人
- 需要明确收益函数
- 复杂情况计算困难

---

_版本：1.0.0_
```

#### 3. 编写 schema.json

```json
{
  "name": "gametheory-perspective",
  "type": "method",
  "domain": "economics",
  "displayName": "博弈论",
  "keywords": ["策略", "均衡", "理性", "收益"],
  "models": [
    {
      "name": "囚徒困境",
      "summary": "个人理性与集体理性的冲突",
      "prompt": "从囚徒困境角度分析..."
    },
    {
      "name": "纳什均衡",
      "summary": "稳定策略组合",
      "prompt": "寻找纳什均衡点..."
    }
  ],
  "heuristics": [
    "识别所有参与者及其利益",
    "构建收益矩阵",
    "寻找占优策略",
    "分析纳什均衡",
    "考虑重复博弈的可能性"
  ],
  "limits": [
    "假设完全理性",
    "需要精确的收益函数",
    "多参与者时计算复杂"
  ],
  "version": "1.0.0"
}
```

---

## CLI 开发

### 项目结构

```
src/super_thinking/
├── cli/
│   ├── __init__.py
│   ├── main.py          # 入口点
│   ├── commands/
│   │   ├── analyze.py   # analyze 命令
│   │   ├── list.py     # list 命令
│   │   └── info.py     # info 命令
│   └── utils/
│       ├── config.py    # 配置管理
│       └── output.py    # 输出格式化
├── core/
│   ├── router.py        # 路由逻辑
│   ├── registry.py      # 专家注册
│   └── debate.py        # 辩论引擎
└── experts/
    └── ...
```

### 添加新命令

```python
# cli/commands/mycommand.py
from .base import BaseCommand

class MyCommand(BaseCommand):
    name = "mycommand"
    help = "我的新命令"
    
    def add_arguments(self, parser):
        parser.add_argument("--option", help="选项")
    
    def handle(self, args):
        # 你的逻辑
        return 0
```

### 注册命令

```python
# cli/commands/__init__.py
from .analyze import AnalyzeCommand
from .list import ListCommand
from .info import InfoCommand
from .mycommand import MyCommand  # 添加这行

COMMANDS = [
    AnalyzeCommand,
    ListCommand,
    InfoCommand,
    MyCommand,  # 注册新命令
]
```

---

## 文档贡献

### 文档结构

```
docs/
├── CLI_DESIGN.md       # CLI 设计文档
├── USER_GUIDE.md       # 用户指南
├── CONTRIBUTING.md    # 本文件
└── ...
```

### 文档规范

| 类型 | 文件名 | 内容 |
|------|--------|------|
| 设计文档 | `*-DESIGN.md` | 技术设计、架构决策 |
| 用户指南 | `*-GUIDE.md` | 使用说明、教程 |
| 参考文档 | `*.md` | API 文档、配置说明 |

### 写作风格

- 使用中文
- 简洁明了
- 提供代码示例
- 包含故障排除

---

## 代码规范

### Python 代码风格

- 遵循 PEP 8
- 使用 type hints
- 文档字符串使用 Google 风格

```python
def analyze(question: str, experts: list[str]) -> DebateResult:
    """分析问题并启动辩论。
    
    Args:
        question: 用户问题
        experts: 参与的专家列表
    
    Returns:
        DebateResult: 辩论结果
    
    Raises:
        ValueError: 当专家列表为空时
    """
    if not experts:
        raise ValueError("专家列表不能为空")
    # ...
```

### 文件组织

- 每个模块一个文件
- 相关模块放在同一包
- 使用 `__init__.py` 导出公共接口

---

## 提交规范

### 提交类型

| 类型 | 说明 |
|------|------|
| `feat:` | 新功能 |
| `fix:` | Bug 修复 |
| `docs:` | 文档更新 |
| `test:` | 测试相关 |
| `refactor:` | 重构 |
| `chore:` | 构建/工具 |

### 提交格式

```
<类型>(<范围>): <简短描述>

[可选的详细描述]

[可选的关闭issue]
```

### 示例

```
feat(experts): 添加庄子专家

- 添加 SKILL.md 和 schema.json
- 更新领域索引
- 添加测试用例

Closes #123
```

---

## 审核流程

### Pull Request 流程

1. **Fork 仓库** - 创建你的派生仓库
2. **创建分支** - 使用有意义的分支名
   ```bash
   git checkout -b feat/add-zhuangzi-expert
   ```
3. **编写代码** - 遵循本指南的规范
4. **添加测试** - 确保有测试覆盖
5. **提交代码** - 遵循提交规范
6. **推送分支** - 推送到你的派生仓库
7. **创建 PR** - 创建 Pull Request
8. **等待审核** - 响应审核意见

### 审核标准

| 项目 | 要求 |
|------|------|
| 代码质量 | 通过 ruff 检查 |
| 测试覆盖 | 关键逻辑有测试 |
| 文档 | 新功能有文档 |
| 示例 | 新专家有示例 |

### 审核周期

- 一般在 3-5 个工作日内回复
- 如果超过一周没有回复，可以 ping

---

## 常见问题

### Q: 我不确定我的贡献是否合适

**A**: 可以在 GitHub Issues 中开一个讨论，描述你的想法，我们会给出建议。

### Q: 我发现了一个 bug，应该怎么办？

**A**: 
1. 先搜索是否已有相关 issue
2. 如果没有，创建一个新 issue
3. 如果你想修复，可以同时提交 PR

### Q: 我不擅长代码，可以贡献什么？

**A**: 
- 文档改进
- 示例添加
- Bug 报告
- 专家资料整理

---

## 联系我们

- GitHub Issues: https://github.com/super-thinking/super-thinking/issues
- 邮箱: support@super-thinking.example.com

---

感谢你的贡献！ 🎉

---

_贡献指南版本：v6.0.0 · 2026-06-05_
