# Examples | 示例

This document provides detailed usage examples for SuperThinking v6.

## Table of Contents | 目录

- [Decision Making](#decision-making--决策分析)
- [Cross-Domain Analysis](#cross-domain-analysis--跨学科分析)
- [Quick Consensus](#quick-consensus--快速共识)

---

## Decision Making | 决策分析

### Scenario | 场景

Use SuperThinking to analyze complex decisions from multiple expert perspectives before making a choice.

**Example Question:** "Should we invest in renewable energy or fossil fuels?"

### Running the Example | 运行示例

```bash
# Using CLI
python examples/decision_making.py --question "Should we invest in renewable energy or fossil fuels?" --experts=socrates,confucius,einstein,sunzi

# Using Python API
python -c "
from examples.decision_making import run_decision_making
result = run_decision_making(
    question='Should we invest in renewable energy or fossil fuels?',
    experts=['socrates', 'confucius', 'einstein', 'sunzi']
)
print(result)
"
```

### Expected Output | 预期输出

```
═══════════════════════════════════════════════════════════════
  Decision Analysis: Should we invest in renewable energy?
═══════════════════════════════════════════════════════════════

Experts: Socrates (Philosophy), Confucius (Ethics), 
         Einstein (Science), Sun Tzu (Strategy)

───────────────────────────────────────────────────────────────
Round 1 - Initial Statements
───────────────────────────────────────────────────────────────

>【Socrates】(Initial)
  Before deciding, we must clarify what we mean by "invest."
  What is the goal of investment? Profit? Sustainability? Both?

>【Confucius】(Initial)
  Investment should serve the greater good. Consider the impact
  on future generations, not just immediate returns.

>【Einstein】(Initial)
  From a scientific perspective, renewable energy is the clear
  choice based on long-term evidence and sustainability data.

>【Sun Tzu】(Initial)
  Consider the strategic implications. Which investment
  offers better risk-adjusted returns?

───────────────────────────────────────────────────────────────
## Argument Menu
───────────────────────────────────────────────────────────────
1. Socrates: Need to clarify "investment" definition (0.8)
2. Confucius: Consider impact on future generations (0.7)
3. Einstein: Renewable energy based on evidence (0.75)
4. Sun Tzu: Strategic risk assessment needed (0.7)

Suggestion: Focus on defining success criteria

═══════════════════════════════════════════════════════════════
Conclusion: Multi-perspective analysis recommends renewable
energy investment with strategic risk management.
═══════════════════════════════════════════════════════════════
```

### Parameters | 参数说明

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--question` | str | required | The decision question to analyze |
| `--experts` | list | auto | Expert IDs to include |
| `--methods` | list | none | Methodology tools to use |
| `--rounds` | int | 3 | Number of debate rounds |
| `--format` | str | text | Output format (text/json) |

---

## Cross-Domain Analysis | 跨学科分析

### Scenario | 场景

Analyze complex problems that span multiple knowledge domains using experts from different fields.

**Example Question:** "How will AI impact employment in the next decade?"

### Running the Example | 运行示例

```bash
# Using CLI
python examples/cross_domain_analysis.py --question "How will AI impact employment in the next decade?"

# Using Python API
python -c "
from examples.cross_domain_analysis import run_analysis
result = run_analysis(
    question='How will AI impact employment in the next decade?',
    domains=['philosophy', 'science', 'business', 'economics']
)
"
```

### Expected Output | 预期输出

```
═══════════════════════════════════════════════════════════════
  Cross-Domain Analysis: AI & Employment
═══════════════════════════════════════════════════════════════

Domains: Philosophy, Science, Business, Economics

───────────────────────────────────────────────────────────────
Expert Panel
───────────────────────────────────────────────────────────────

Philosophy Domain:
  - Socrates: Dialectical analysis
  - Confucius: Ethical considerations

Science Domain:
  - Einstein: Technical innovation perspective
  - Curie: Scientific method

Business Domain:
  - Buffett: Economic fundamentals
  - Musk: Innovation strategy

───────────────────────────────────────────────────────────────
Round 1 - Domain Perspectives
───────────────────────────────────────────────────────────────

>【Socrates】(Philosophy)
  What do we mean by "employment"? Has its definition
  changed historically?

>【Buffett】(Business)
  From an economic standpoint, AI will shift employment
  patterns rather than eliminate jobs entirely.

>【Einstein】(Science)
  Historical pattern: Technology creates more jobs than
  it displaces. Expect similar dynamics with AI.

───────────────────────────────────────────────────────────────
## Cross-Domain Synthesis
───────────────────────────────────────────────────────────────

Philosophical: Employment is about meaning, not just income
Economic: Jobs will transform, not disappear
Scientific: Historical precedent suggests adaptation
Strategic: Upskilling is key to transition

═══════════════════════════════════════════════════════════════
Recommendation: Invest in education and upskilling programs
═══════════════════════════════════════════════════════════════
```

### Parameters | 参数说明

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--question` | str | required | Complex question to analyze |
| `--domains` | list | all | Knowledge domains to include |
| `--experts-per-domain` | int | 2 | Number of experts per domain |
| `--synthesis-method` | str | auto | Cross-domain synthesis method |

---

## Quick Consensus | 快速共识

### Scenario | 场景

When you need a quick multi-perspective answer without extensive debate.

**Example Question:** "Is this a good business idea?"

### Running the Example | 运行示例

```bash
# Using CLI
python examples/quick_consensus.py --question "Is this a good business idea?" --idea="AI-powered tutoring platform"

# Using Python API
python -c "
from examples.quick_consensus import run_quick_consensus
result = run_quick_consensus(
    question='Is this a good business idea?',
    idea='AI-powered tutoring platform'
)
print(result['verdict'])
"
```

### Expected Output | 预期输出

```
═══════════════════════════════════════════════════════════════
  Quick Consensus: Business Idea Evaluation
═══════════════════════════════════════════════════════════════

Idea: AI-powered tutoring platform

───────────────────────────────────────────────────────────────
Expert Quick Votes | 专家快速投票
───────────────────────────────────────────────────────────────

  ✓ Buffett: Strong YES - Clear market need
  ✓ Musk: YES - Scalable technology
  ✓ Jobs: CONDITIONAL - User experience critical
  ✓ Sun Tzu: YES - Competition is winnable

───────────────────────────────────────────────────────────────
Consensus Score | 共识得分: 0.78 / 1.0
───────────────────────────────────────────────────────────────

Strengths:
  - Clear market demand for education tech
  - AI technology is mature
  - Scalable business model

Concerns:
  - User experience differentiation needed
  - Competition from established players
  - Trust-building with parents/students

═══════════════════════════════════════════════════════════════
Quick Verdict: PROCEED with caution - strong fundamentals,
need differentiation strategy.
═══════════════════════════════════════════════════════════════
```

### Parameters | 参数说明

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--question` | str | required | Question to answer |
| `--idea` | str | none | Business idea or proposal |
| `--experts` | list | 4 | Number of experts (faster with fewer) |
| `--time-limit` | int | 30 | Maximum analysis time (seconds) |

---

## Additional Examples | 更多示例

### Using Mock Mode | 
