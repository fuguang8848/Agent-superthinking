# 最终综合 Prompt

## 任务

综合所有辩论轮次的论点，形成最终结论。

## 辩论概况

- **原始问题**：{user_question}
- **辩论轮次**：{total_rounds} 轮
- **参与专家**：{expert_names}
- **收敛状态**：{convergence_status}

## 完整论点历史

### 第 1 轮（INITIAL）

{statements_round_1}

### 第 2 轮（REBUTTAL）

{statements_round_2}

### ...（中间轮次省略）

{中间轮次论点摘要}

### 最终轮（FINAL）

{statements_final}

## 最终论点菜单

```markdown
{all_arguments}
```

## 综合分析格式

### 1. 共识结论

> 基于多轮辩论，以下观点获得专家广泛认同：

```markdown
## 核心共识

{consensus_point_1}

**支撑依据**：
- {evidence_1}
- {evidence_2}

---

{consensus_point_2}

**支撑依据**：
- {evidence_1}
- {evidence_2}
```

### 2. 主要分歧

> 以下问题专家存在显著分歧：

```markdown
## 分歧领域

### 分歧 1：{divergence_title}

**观点A**：[@专家名] {claim_a}
- 理由：{reason_a}

**观点B**：[@专家名] {claim_b}
- 理由：{reason_b}

**分歧根源**：{root_cause}

**建议进一步研究**：{suggestion}
```

### 3. 根本矛盾

> 以下矛盾无法通过现有信息解决：

```markdown
## 根本矛盾

1. **{contradiction_1}**
   - 矛盾双方：{party_a} vs {party_b}
   - 矛盾性质：{nature}

2. **{contradiction_2}**
   - 矛盾双方：{party_a} vs {party_b}
   - 矛盾性质：{nature}
```

### 4. 行动建议

> 基于辩论结论，建议：

```markdown
## 行动建议

### 短期（1-3个月）
1. {action_1}
2. {action_2}

### 中期（3-12个月）
1. {action_1}
2. {action_2}

### 长期（1年以上）
1. {action_1}
2. {action_2}
```

### 5. 开放问题

> 需要进一步思考或研究的问题：

```markdown
## 开放问题

1. {question_1}
2. {question_2}
3. {question_3}
```

### 6. 置信度评估

> 对最终结论的置信度：

```markdown
| 结论 | 置信度 | 专家认同度 |
|------|--------|------------|
| {conclusion_1} | {conf}/1.0 | {agreement}% |
| {conclusion_2} | {conf}/1.0 | {agreement}% |
```

## 输出格式

```json
{
  "consensus_points": ["{conclusion_1}", "{conclusion_2}"],
  "divergence_points": ["{divergence_1}", "{divergence_2}"],
  "root_contradictions": ["{contradiction_1}", "{contradiction_2}"],
  "suggestions": ["{action_1}", "{action_2}"],
  "open_questions": ["{question_1}", "{question_2}"],
  "overall_confidence": {overall_confidence},
  "debate_quality": "{quality_assessment}"
}
```

## 主持人总结语

{moderator_final_remark}
