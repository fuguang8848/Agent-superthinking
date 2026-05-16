# Super Thinking - 超级思考技能

**触发词：** `超级思考`、`专家团`、`所有视角分析`、`综合思考`、`多角度分析`

---

## 什么是超级思考？

超级思考是一个**多视角专家团分析系统**。当面对复杂问题时，它会同时激活多个思考视角，并行分析后融合输出。

```
用户问题 → 路由判断 → 并行专家分析 → 冲突检测 → 共识提炼 → 格式化输出
```

---

## 使用方式

### 快速使用（auto模式）

```
超级思考：{你的问题}
```

系统会自动根据问题关键词匹配相关视角。

### 指定模式

| 模式 | 命令 | 说明 |
|------|------|------|
| auto | `超级思考：xxx` | 根据关键词自动匹配视角 |
| force_all | `超级思考[force_all]：xxx` | 激活所有已启用的视角 |
| selective | `超级思考[视角1,视角2]：xxx` | 仅激活指定视角 |

### 示例

```
超级思考：2024年AI创业机会如何？
超级思考[force_all]：是否应该转行做程序员？
超级思考[mao,magi]：新能源汽车行业分析
```

---

## 输出格式

```markdown
## 🧠 超级思考报告

### 核心共识 (3个视角一致)
- **关键结论1** - 支持: 毛泽东视角, 辩论视角, 元视角
- **关键结论2** - 支持: 毛泽东视角, 元视角

### 关键分歧
⚠️ **高严重性冲突: 1**
- 来源: 毛泽东视角 ↔ 辩论视角
- 详情: 在XX问题上存在根本对立

### 各视角独特洞察
### 毛泽东视角
- 详细的分析内容...
- 关键点1
- 关键点2

### 风险警示
- **[毛泽东视角]** 可能的局限性...
```

---

## 内置视角

| ID | 名称 | 触发关键词 |
|----|------|-----------|
| nuwa_meta | 女娲元视角 | 创造, 生成, 设计, 构思, 新视角, 新思维 |
| mao_perspective | 毛泽东视角 | 革命, 斗争, 人民, 群众, 阶级 |
| magi_debate | 辩论视角 | 辩论, 论证, 支持, 反对, 正方, 反方 |
| meta_thinking | 元视角 | 分析, 思考, 逻辑, 框架, 方法 |

### 女娲元视角（特殊）

女娲不是普通视角，而是**视角生成器**。当你需要：

- 现有视角无法覆盖你的问题
- 需要针对特定场景生成新视角
- 想知道应该用哪些视角的组合

使用女娲：

```
超级思考[nuwa_meta]：我想提升创造力，有什么思路
```

女娲会：
1. 诊断你需要的视角类型
2. 检查现有视角覆盖情况
3. 推荐最优视角组合
4. **自动生成并注册新视角**（如需要）

---

## 添加新视角

创建文件 `src/super_thinking/perspectives/your_perspective.py`：

```python
from dataclasses import dataclass
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput

@dataclass
class YourPerspectiveOutput(PerspectiveOutput):
    pass

class YourPerspective:
    id = "your_perspective"
    name = "你的视角"
    description = "描述这个视角的特色"
    trigger_keywords = ["关键词1", "关键词2"]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        # 你的分析逻辑
        return YourPerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="你的分析内容...",
            key_points=["要点1", "要点2"],
            confidence=0.8,
            tags=["标签1"],
            warnings=["局限性或风险"],
        )
```

---

## 技术架构

```
super_thinking/
├── core/           # 核心组件
│   ├── registry.py # 视角动态注册表
│   ├── router.py   # 路由判断
│   └── jury.py     # 专家团调度
├── fusion/         # 融合层
│   ├── conflict.py # 冲突检测
│   ├── consensus.py# 共识提炼
│   └── formatter.py# 输出格式化
└── perspectives/  # 视角实现
    ├── _interface.py  # 标准接口
    └── README.md   # 新增视角指南
```

---

## 配置

编辑 `config.yaml` 修改默认行为：

```yaml
enabled_perspectives:
  - mao_perspective
  - magi_debate
  - meta_thinking

routing:
  default_mode: "auto"
  timeout_per_perspective: 60
  max_workers: 4
```
