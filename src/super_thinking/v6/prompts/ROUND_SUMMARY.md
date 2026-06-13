# 轮次总结 Prompt

## 任务

对第 {round_number} 轮辩论进行结构化总结。

## 轮次信息

- **轮次编号**：第 {round_number} 轮
- **发言角色**：{role}
- **参与专家**：{expert_names}
- **收敛得分**：{convergence_score}（{convergence_status}）

## 本轮论点菜单

```markdown
{argument_menu}
```

## 本轮专家发言

{statements}

## 上一轮总结（参考）

{prev_summary}

## 总结格式

### 1. 共识点（已收敛观点）

```markdown
| 论点 | 置信度 | 收敛来源 |
|------|--------|----------|
| {claim1} | {conf1} | {source_expert1} |
| {claim2} | {conf2} | {source_expert2} |
```

### 2. 核心分歧点

```markdown
### 分歧 {n}：{title}
- **专家A观点**：[@专家名] {claim_a}
- **专家B观点**：[@专家名] {claim_b}
- **分歧焦点**：{divergence_point}
- **关键问题**：{key_question_to_resolve}
```

### 3. 新涌现观点

```markdown
| 观点 | 提出专家 | 置信度 | 重要性 |
|------|----------|--------|--------|
| {new_claim} | {expert} | {conf} | 高/中/低 |
```

### 4. 待澄清问题

```markdown
1. {question_1}
2. {question_2}
```

### 5. 下轮建议

```markdown
**建议关注**：
- {focus_area_1}
- {focus_area_2}

**建议邀请的专家类型**：
- {expert_type_1}
- {expert_type_2}
```

## 统计信息

| 指标 | 本轮 | 相比上轮 |
|------|------|----------|
| 有效论点数 | {arg_count} | {arg_change:+/-} |
| 平均置信度 | {avg_confidence} | {conf_change:+/-} |
| 新论点比例 | {new_arg_ratio} | {new_change:+/-} |

## 主持人备注

{moderator_notes}
