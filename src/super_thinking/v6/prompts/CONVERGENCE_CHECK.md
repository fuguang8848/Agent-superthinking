# 收敛检测 Prompt

## 任务

判断当前辩论轮次是否达到收敛状态。

## 当前辩论状态

**轮次**：第 {round_number} 轮
**参与专家数**：{num_experts}
**收敛阈值**：score >= {score_threshold}
**连续达标要求**：{require_consecutive} 轮

## 本轮论点菜单

```markdown
{argument_menu_text}
```

## 本轮专家发言摘要

{statements_summary}

## 上一轮收敛信号

```json
{prev_convergence_signal}
```

## 收敛判断算法

### 综合得分计算

```
score = w_overlap × overlap + w_density × (1 − new_arg_density) + w_drift × (1 − drift)
```

其中：
- **w_overlap** = {w_overlap}（重叠率权重）
- **w_density** = {w_density}（新论点密度权重）
- **w_drift** = {w_drift}（置信度漂移权重）

### 指标计算

| 指标 | 计算方法 | 本轮值 |
|------|----------|--------|
| `overlap` | Jaccard(本轮claims, 上轮claims) | {overlap} |
| `new_arg_density` | 归一化(每专家新论点平均数) | {new_arg_density} |
| `drift` | \|avg(confidence) − 0.5\| × 2 | {drift} |

### 收敛条件

**软收敛**（满足其一）：
- `score >= {score_threshold}` 持续 `require_consecutive={require_consecutive}` 轮
- `score = {current_score}`

**硬收敛**（同时满足）：
- `overlap >= {overlap_hard_threshold}`
- `new_arg_density <= {new_arg_hard_threshold}`

## 判断输出

```json
{
  "round_number": {round_number},
  "overlap_rate": {overlap},
  "new_arg_density": {new_arg_density},
  "confidence_drift": {drift},
  "score": {score},
  "consecutive_count": {consecutive_count},
  "converged": {converged},
  "hard_converged": {hard_converged},
  "details": {
    "overlap_component": {overlap_component},
    "density_component": {density_component},
    "drift_component": {drift_component}
  },
  "reason": "{判断理由}"
}
```

## 收敛解读

- **converged = true**：综合判断已达到软收敛，辩论可以进入总结阶段
- **hard_converged = true**：论点高度重叠且新论点极少，辩论达到强收敛
- **两者都为 false**：辩论尚未收敛，需要继续下一轮
