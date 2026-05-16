# Super Thinking - 多视角专家团思考系统

一个模拟专家团协作的多维度思考框架。通过并行调用多个专业视角分析问题，自动检测冲突、提炼共识，并生成结构化的综合报告。

## 特性

- **多视角并行分析** - 多个专业视角同时思考问题
- **智能路由** - 根据问题内容自动匹配相关视角
- **冲突检测** - 自动识别并标记观点间的矛盾
- **共识提炼** - 提取跨视角的一致结论
- **结构化输出** - 生成易于阅读的综合报告

## 安装

```bash
pip install -e .
```

## 快速开始

```python
from super_thinking import think, format_result

# 简单使用
result = think("2024年AI发展趋势如何？", mode="auto")

# 格式化输出
output = format_result(result)
print(output.full_report)
```

## 使用方法

### Python API

```python
from super_thinking.core.jury import Jury
from super_thinking.core.registry import get_registry
from super_thinking.fusion.formatter import Formatter

# 初始化
registry = get_registry()
jury = Jury(registry)
formatter = Formatter()

# 执行分析
result = jury.think(
    input="你的问题",
    context={},  # 可选上下文
    mode="auto",  # auto, force_all, selective
)

# 格式化结果
output = formatter.format(result)
print(output.full_report)
```

### 路由模式

| 模式 | 说明 |
|------|------|
| `auto` | 根据问题关键词自动匹配视角 |
| `force_all` | 激活所有已启用的视角 |
| `selective` | 仅激活指定的视角 |

## 添加新视角

1. 在 `src/super_thinking/perspectives/` 创建新文件
2. 实现 `Perspective` 接口
3. 在 `config.yaml` 中添加到 `enabled_perspectives`

详见 [perspectives/README.md](src/super_thinking/perspectives/README.md)

## 开发

```bash
# 运行测试
pytest tests/ -v

# 代码格式化
black src/
```

## 许可证

MIT
