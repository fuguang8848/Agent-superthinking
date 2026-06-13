# V6 Multi-Agent 圆桌辩论端到端场景

> 版本: 0.1.0
> 状态: 草案
> 日期: 2026-06-05

本文档定义了 V6 Multi-Agent 圆桌辩论系统的 5 个核心端到端测试场景，每个场景包含完整的输入、期望输出和验证点。

---

## 场景 A: 决策类问题

### 场景描述
用户提出需要权衡利弊的决策问题。

**输入示例:**
```
问题: "我目前在大厂工作 3 年，收到一家创业公司的 CTO offer，薪资相当但股权不确定，我该跳槽吗？"
```

**期望输出结构:**
1. 主持人初始化 → 选择 3-5 位专家（商业创新、风险评估、哲学视角等）
2. 第一轮并行发言 → 各专家独立陈述初始观点
3. 辩论循环（2-3 轮）→ 专家交叉反驳，论点菜单更新
4. 收敛判断 → 达到共识或最大轮次
5. 最终陈述 + 会议结论

**验证点:**
| 验证项 | 期望值 | 检查方法 |
|--------|--------|----------|
| 专家数量 | 3-5 人 | 检查 `session.experts` 长度 |
| 收敛轮次 | ≤3 轮 | 检查 `convergence.round` ≤ 3 |
| 共识点数量 | ≥1 | 检查 `conclusion.共识点` 非空 |
| 建议可操作性 | 是 | 检查 `建议` 包含具体行动项 |
| 分歧点记录 | 是 | 检查 `结论.分歧点` 非空 |

**测试用例:**
```python
def test_scenario_a_decision_making():
    """场景A: 决策类问题"""
    result = run_debate("我该跳槽吗？", max_rounds=5)
    
    assert len(result.experts) >= 3
    assert result.convergence_round <= 3
    assert len(result.conclusion["共识点"]) >= 1
    assert len(result.conclusion["建议"]) >= 1
    assert len(result.conclusion["分歧点"]) >= 0
```

---

## 场景 B: 理解类问题

### 场景描述
用户请求解释或理解一个抽象概念。

**输入示例:**
```
问题: "如何理解'熵增'这个概念？它在生活中有什么应用？"
```

**期望输出结构:**
1. 主持人选择跨学科专家组合（物理学、系统论、哲学、管理学）
2. 第一轮 → 各专家从自身领域解释熵增
3. 辩论循环 → 寻找跨学科的共同点
4. 结论 → 融合多学科视角的完整解释

**验证点:**
| 验证项 | 期望值 | 检查方法 |
|--------|--------|----------|
| 跨学科视角 | ≥3 个不同领域 | 检查 `专家.perspective` 多样性 |
| 共识点明确 | 是 | 检查 `共识点` 包含跨学科共性 |
| 视角融合 | 是 | 检查 `结论` 整合多个学科 |
| 术语解释完整 | 是 | 检查 `关键概念` 定义清晰 |

**测试用例:**
```python
def test_scenario_b_conceptual_understanding():
    """场景B: 理解类问题"""
    result = run_debate("如何理解熵增？", max_rounds=5)
    
    # 检查跨学科视角
    domains = set(e.domain for e in result.experts)
    assert len(domains) >= 3
    
    # 检查共识点
    assert len(result.conclusion["共识点"]) >= 1
    
    # 检查多学科融合
    conclusion_text = " ".join(result.conclusion.values())
    assert "物理学" in conclusion_text or "热力学" in conclusion_text
```

---

## 场景 C: 创意类问题

### 场景描述
用户请求创意建议或产品定位。

**输入示例:**
```
问题: "我想做一个面向老年人的健身 App，请帮我做产品定位。"
```

**期望输出结构:**
1. 主持人选择创意类专家（设计思维、商业创新、用户研究）
2. 第一轮 → 各专家提出创意方向
3. 辩论循环 → 评估各创意可行性
4. 自由补充 → 鼓励专家提出新角度（≥20%）

**验证点:**
| 验证项 | 期望值 | 检查方法 |
|--------|--------|----------|
| 自由补充占比 | ≥20% | `自由补充发言数 / 总发言数` ≥ 0.2 |
| 最终陈述差异化 | 是 | 检查各专家最终观点不完全相同 |
| 创意多样性 | 是 | 检查建议包含多个方向 |
| 视角互补 | 是 | 检查专家来自不同领域 |

**测试用例:**
```python
def test_scenario_c_creative_problem():
    """场景C: 创意类问题"""
    result = run_debate("老年人健身 App 定位", max_rounds=5)
    
    # 检查自由补充占比
    total_statements = sum(len(r.statements) for r in result.rounds)
    free_additions = sum(
        1 for r in result.rounds
        for s in r.statements if s.is_free_addition
    )
    assert free_additions / total_statements >= 0.2
    
    # 检查最终陈述差异化
    final_views = [r.final_statement for r in result.experts]
    assert len(set(final_views)) >= 2  # 至少2个不同的观点
```

---

## 场景 D: 争议问题

### 场景描述
用户提出存在根本价值冲突的问题。

**输入示例:**
```
问题: "在 AI 时代，技术能力和人文素养哪个更重要？"
```

**期望输出结构:**
1. 主持人识别这是一个价值冲突问题
2. 选择对立立场的专家（技术乐观派、人文主义者）
3. 辩论循环 → 深入挖掘分歧根源
4. 必要时向用户咨询 → "您的价值观更偏向哪边？"

**验证点:**
| 验证项 | 期望值 | 检查方法 |
|--------|--------|----------|
| 分歧点识别 | 是 | 检查 `结论.分歧点` 包含核心争议 |
| 用户咨询触发 | 适当 | 检查 `events` 包含 `user_consultation` |
| 未解决矛盾记录 | 是 | 检查 `未解决的根本矛盾` 非空 |
| 对立观点呈现 | 是 | 检查至少有 2 个对立立场 |

**测试用例:**
```python
def test_scenario_d_controversial_issue():
    """场景D: 争议问题"""
    result = run_debate("技术 vs 人文", max_rounds=5)
    
    # 检查分歧点被识别
    assert len(result.conclusion["分歧点"]) >= 1
    
    # 检查根本矛盾被记录
    assert len(result.conclusion["未解决的根本矛盾"]) >= 1
    
    # 检查用户咨询（如果分歧很深）
    if result.disagreement_depth > 0.7:
        assert any(e.type == "user_consultation" for e in result.events)
```

---

## 场景 E: 空领域问题

### 场景描述
用户问题涉及极端小众或全新的领域。

**输入示例:**
```
问题: "我想在火星上建一个自循环生态系统，有什么需要考虑的？"
```

**期望输出结构:**
1. 主持人检测到专家库中相关专家不足
2. 自动降级策略 → 优雅切换到 v5 单轮模式
3. 使用通用分析专家 + 外部咨询补充
4. 明确告知用户局限性

**验证点:**
| 验证项 | 期望值 | 检查方法 |
|--------|--------|----------|
| 降级触发 | 是 | 检查 `mode` 变为 "v5_fallback" |
| 优雅降级 | 是 | 检查无异常抛出，有友好提示 |
| 用户通知 | 是 | 检查输出包含 "领域受限" 说明 |
| 仍有输出 | 是 | 即使降级也产生结论 |

**测试用例:**
```python
def test_scenario_e_edge_case():
    """场景E: 空领域问题"""
    result = run_debate("火星生态系统", max_rounds=5)
    
    # 检查降级模式
    assert result.mode == "v5_fallback" or result.mode == "hybrid"
    
    # 检查仍有输出
    assert result.conclusion is not None
    
    # 检查用户通知
    assert "领域受限" in result.summary or "专家有限" in result.summary
```

---

## 通用验证函数

```python
def run_debate(question: str, max_rounds: int = 5, 
               mock_experts: bool = False) -> DebateResult:
    """
    运行辩论会话
    
    Args:
        question: 用户问题
        max_rounds: 最大辩论轮次
        mock_experts: 是否使用 mock 专家
        
    Returns:
        DebateResult: 包含完整辩论结果
    """
    # TODO: 实现实际逻辑
    pass


@dataclass
class DebateResult:
    """辩论结果数据结构"""
    session_id: str
    question: str
    experts: List[Expert]
    rounds: List[DebateRound]
    convergence_round: int
    mode: str  # "v6_normal", "v5_fallback", "hybrid"
    conclusion: Dict[str, List[str]]
    events: List[Event]
    summary: str
```

---

## 验收标准

所有 5 个场景必须通过以下通用检查:

1. ✅ 辩论流程完整（初始化 → 并行发言 → 辩论循环 → 收敛 → 结论）
2. ✅ 无崩溃或未处理异常
3. ✅ 结论结构完整（共识点、分歧点、建议）
4. ✅ UTF-8 编码输出
5. ✅ 日志记录完整

---

_文档版本: 0.1.0 | 最后更新: 2026-06-05_
