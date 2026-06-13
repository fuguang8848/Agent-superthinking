# v5 核心模块摘要

> 版本：v5 分析
> 日期：2026-06-05
> 作者：后端工程师

---

## 1. 核心模块概览



---

## 2. Router（路由模块）

**文件路径：** 

### 2.1 职责
Router 决定哪些视角（perspective）应该被激活，基于用户的输入。

### 2.2 关键类

#### RoutingResult（dataclass）
-  - 待激活的 perspective ID 列表
-  - 路由模式：auto/force_all/selective
-  - 路由决策的解释
-  - 每个 perspective 的匹配分数

#### Router（主类）
-  - 主入口方法

### 2.3 路由模式

| 模式 | 说明 | 激活逻辑 |
|------|------|----------|
| auto | 自动匹配 | 基于 trigger_keywords 关键词匹配，score = 命中数/总数 |
| force_all | 强制全部 | 激活所有已启用的 perspective |
| selective | 选择性 | 仅激活 selective_ids 指定的 perspective |

### 2.4 关键函数

| 函数名 | 功能 |
|--------|------|
| _route_auto() | 关键词匹配路由，按 trigger_keywords 计算匹配分数 |
| _route_force_all() | 返回所有已启用 perspective |
| _route_selective() | 验证并返回指定 ID 的 perspective |

### 2.5 激活判断依据
- auto 模式：至少命中 1 个关键词（score > 0）即激活
- 无匹配时：自动回退到激活所有已启用的 perspective

---

## 3. Registry（注册表模块）

**文件路径：** 

### 3.1 职责
动态发现、注册、管理视角模块，提供 enable/disable 功能。

### 3.2 核心数据结构
-  - perspective_id → 实例
-  - 已启用的 perspective ID 集合

### 3.3 关键函数

| 函数名 | 功能 |
|--------|------|
| discover() | 自动扫描 perspectives/ 目录，加载有效模块 |
| _validate_perspective() | 验证 perspective 是否实现必需接口 |
| register(perspective) | 手动注册 perspective 实例 |
| enable(perspective_id) | 启用 perspective |
| disable(perspective_id) | 禁用 perspective |
| list_all() | 返回所有注册的 perspective |
| list_enabled() | 返回所有已启用的 perspective |
| get(perspective_id) | 获取指定 perspective |

### 3.4 配置持久化
- 配置存储在 config.yaml
- 字段：enabled_perspectives: [...]
- 使用 yaml.safe_load() 和 yaml.dump() 读写

---

## 4. Jury（陪审团模块）

**文件路径：** 

### 4.1 职责
编排多个视角的并行执行，处理超时控制和异常隔离。

### 4.2 关键类

#### JuryResult（dataclass）
-  - perspective_id → 输出
-  - perspective_id → 错误信息
-  - 路由决策
-  - 总数
-  - 成功数
-  - 失败数

#### Jury（主类）


### 4.3 关键函数

| 函数名 | 功能 |
|--------|------|
| think(input, context, mode, selective_ids) | 主入口：执行所有激活的 perspective |
| _execute_perspective() | 执行单个 perspective（异常包装） |
| convene(perspective_ids, input, context) | 指定 perspective IDs 并执行 |

### 4.4 并行执行机制
使用 ThreadPoolExecutor(max_workers=self.max_workers) 并行执行
- 单个 perspective 失败不影响其他 perspective
- 使用 concurrent.futures.TimeoutError 处理超时
- 所有异常被捕获并记录到 errors 字典

---

## 5. LLMRouter（LLM 路由模块）

**文件路径：** 

### 5.1 职责
使用 LLM 智能选择视角，替代简单的关键词匹配。

### 5.2 关键类

#### LLMRouter（继承自 Router）
- ROUTING_PROMPT: str - LLM 路由提示词模板
- CATEGORY_SUMMARY: str - 专家分类摘要

### 5.3 关键函数

| 函数名 | 功能 |
|--------|------|
| route(input, mode, selective_ids) | 路由入口，新增 llm 模式 |
| _route_llm(input_text) | 调用 LLM 选择视角 |
| _build_experts_context() | 构建专家上下文（分组：内置 vs SKILL） |
| _parse_llm_response() | 解析 LLM 返回的 JSON 数组 |

### 5.4 LLM 路由流程
1. 构建专家上下文（名称 + 描述）
2. 填充 ROUTING_PROMPT 模板
3. 调用 SharedContext.call_llm()
4. 解析 JSON 响应获取 perspective IDs
5. 验证 ID 有效性，回退到 auto 模式如需

---

## 6. ExtendedRegistry（扩展注册表）

**文件路径：** 

### 6.1 职责
在 Registry 基础上，增加对 SKILL.md 视角的发现支持。

### 6.2 关键类

#### ExtendedRegistry（继承自 Registry）
- discover(include_skill_perspectives=True) - 发现 Python + SKILL.md 视角
- _discover_skill_perspectives() - 扫描 experts/ 目录加载 SKILL.md

### 6.3 SKILL.md 结构


---

## 7. Fusion 模块

### 7.1 ConflictDetector（冲突检测）

**文件路径：** 

- CONTRADICTION_KEYWORDS - 反义词对列表
- detect(outputs) - 检测输出间的冲突
- _check_contradictions() - 检查关键词矛盾
- _check_confidence_gaps() - 检查置信度差异（gap >= 0.6）
- _check_divergence() - 检查结论分歧

**冲突类型：** contradiction, confidence_gap, divergence

### 7.2 ConsensusFinder（共识发现）

**文件路径：** 

- THEME_GROUPS - 主题关键词组
- find(outputs) - 查找共识点
- _find_exact_matches() - 精确匹配（指纹前50字符）
- _find_theme_matches() - 主题匹配
- _find_weak_consensus() - 弱共识（基于 tags）

**共识类型：** strong(3+), moderate(2), weak, unique

### 7.3 Formatter（格式化）

**文件路径：** 

- format(outputs, conflicts, consensus) - 格式化最终输出

---

## 8. Perspective 接口

**文件路径：** 

### PerspectiveOutput（dataclass）


### Perspective 协议（@runtime_checkable）
- id: str - 唯一标识符
- name: str - 人类可读名称
- description: str - 描述
- trigger_keywords: list[str] - 触发关键词
- think(input: str, context: dict) -> PerspectiveOutput

---

## 9. 执行流程总结



---

_文档版本：v5 核心模块摘要 v1.0_
