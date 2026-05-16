# 添加新视角

本目录包含所有可用的思考视角。每个视角都是一个独立的分析模块，按照标准接口实现。

## 接口定义

详见 [`_interface.py`](./_interface.py)

## 创建新视角

### 1. 创建视角文件

在 `perspectives/` 目录下创建新文件，例如 `my_perspective.py`：

```python
from dataclasses import dataclass
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


@dataclass
class MyPerspectiveOutput(PerspectiveOutput):
    """自定义输出类型（可选）"""
    pass


class MyPerspective:
    """我的分析视角"""

    id = "my_perspective"  # 唯一标识符
    name = "我的视角"        # 显示名称
    description = "这个视角从某个特定角度分析问题"  # 简短描述
    trigger_keywords = ["关键词1", "关键词2"]  # 触发关键词

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """
        分析输入问题

        Args:
            input: 用户的问题或陈述
            context: 额外上下文信息

        Returns:
            PerspectiveOutput: 分析结果
        """
        # 你的分析逻辑
        analysis = self._analyze(input, context)

        return MyPerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis=analysis,
            key_points=["关键点1", "关键点2", "关键点3"],
            confidence=0.85,
            tags=["tag1", "tag2"],
            warnings=["这个视角可能的局限性"],
            metadata={"extra": "额外数据"},
        )

    def _analyze(self, input: str, context: dict) -> str:
        """实际的分析逻辑"""
        # 实现你的分析
        return f"分析结果：{input}"
```

### 2. 注册视角

**方式一：自动发现**
将视角文件放入 `perspectives/` 目录，registry 会自动扫描并加载。

**方式二：手动注册**
```python
from super_thinking import get_registry

registry = get_registry()
registry.register(MyPerspective())
```

**方式三：配置启用**
在 `config.yaml` 中添加视角 ID：
```yaml
enabled_perspectives:
  - my_perspective
```

### 3. 定义触发关键词

触发关键词用于 `auto` 路由模式。当用户问题包含这些关键词时，对应视角会被激活。

```python
trigger_keywords = ["AI", "人工智能", "机器学习", "深度学习"]
```

## 视角模板

```python
"""
[视角名称] - [简短描述]

详细的视角说明，包括：
- 这个视角的关注点
- 分析方法论
- 适用的场景
"""

from dataclasses import dataclass
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class TemplatePerspective:
    id = "template"
    name = "模板视角"
    description = "创建新视角的模板"
    trigger_keywords = ["template", "模板"]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        return PerspectiveOutput(
            perspective_id=self.id,
            perspective_name=self.name,
            analysis="",
            key_points=[],
            confidence=0.5,
            tags=[],
            warnings=[],
            metadata={},
        )
```

## 最佳实践

1. **设置合理的置信度** - 0.0-1.0，反映这个视角对该问题的把握程度
2. **提供关键点** - 3-5个简明的关键发现
3. **添加风险警示** - 说明视角的局限性或潜在偏见
4. **使用标签** - 帮助后续分析归类
5. **处理异常** - 在 `think()` 中做好错误处理

## 内置视角

| ID | 文件 | 描述 |
|----|------|------|
| mao_perspective | mao_perspective.py | 毛泽东思想视角 |
| magi_debate | magi_debate.py | 辩论/正反方视角 |
| meta_thinking | meta_thinking.py | 元认知/反思视角 |
