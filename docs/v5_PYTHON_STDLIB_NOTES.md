# Python 标准库可复用能力笔记

> 版本：v1.0
> 日期：2026-06-05
> 作者：后端工程师

---

## 1. 概述

本文档调研 Python 标准库中可用于 v6 实现的并发、数据结构、序列化等能力。

---

## 2. 并发相关（concurrent.futures）

### 2.1 ThreadPoolExecutor

**v5 用法：**
```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
    future_to_pid = {
        executor.submit(self._execute_perspective, p, input, context): p.id
        for p in perspectives
    }
    for future in future_to_pid:
        try:
            result = future.result(timeout=self.timeout_per_perspective)
        except FuturesTimeoutError:
            errors[pid] = "Timeout"
```

**v6 可复用场景：**
- 第一轮并行发言
- 外部咨询并行调用
- 方法论工具并行执行

### 2.2 Future 对象

**关键方法：**
- future.result(timeout=None) - 获取结果
- future.exception() - 获取异常
- future.cancelled() - 检查是否取消

---

## 3. 数据结构（collections, dataclasses）

### 3.1 dataclasses

**v5 已用：**
```python
from dataclasses import dataclass, field

@dataclass
class RoutingResult:
    activated: list[str]
    mode: str
    reason: str
    scores: dict[str, float]
```

**v6 推荐用法：**
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ExpertStatement:
    expert_id: str
    statement: str
    targets: list[str] = field(default_factory=list)
    arguments: list[str] = field(default_factory=list)
    uses_methodology: Optional[str] = None
    is_final: bool = False

@dataclass
class DebateRound:
    round_num: int
    statements: list[ExpertStatement] = field(default_factory=list)
    argument_menu: list[str] = field(default_factory=list)
    convergence_score: float = 0.0
```

**优点：**
- 自动生成 __init__, __repr__, __eq__
- 支持默认值和字段工厂
- 便于 JSON 序列化

### 3.2 deque（双端队列）

**位置：** collections.deque

**v6 适用场景：**
```python
from collections import deque

debate_history = deque(maxlen=10)
speaking_order = deque(expert_ids)
```

### 3.3 defaultdict

**v6 适用场景：**
```python
from collections import defaultdict

expert_arguments = defaultdict(list)
for stmt in statements:
    expert_arguments[stmt.expert_id].append(stmt.arguments)
```

### 3.4 Counter

**v6 适用场景：**
```python
from collections import Counter

argument_counts = Counter()
for stmt in statements:
    argument_counts.update(stmt.arguments)
most_common = argument_counts.most_common(5)
```

---

## 4. 异步编程（asyncio）

### 4.1 asyncio.run()

**v6 适用场景：** 异步 LLM 调用

```python
import asyncio

async def call_llm_async(prompt: str) -> str:
    return await llm_call(prompt)

async def debate_round_async(experts: list, prompt: str) -> list:
    tasks = [call_llm_async(f"{prompt}") for e in experts]
    results = await asyncio.gather(*tasks)
    return results

statements = asyncio.run(debate_round_async(experts, prompt))
```

### 4.2 asyncio.Queue

**适用场景：** 生产者-消费者模式

```python
async def moderator_queue_example():
    queue = asyncio.Queue()
    
    async def collect_statement(expert_id: str):
        result = await call_llm_async(expert_id)
        await queue.put((expert_id, result))
    
    await asyncio.gather(collect_statement("e1"), collect_statement("e2"))
```

### 4.3 asyncio.Semaphore（限流）

```python
semaphore = asyncio.Semaphore(3)

async def limited_call(prompt: str):
    async with semaphore:
        return await call_llm_async(prompt)
```

---

## 5. 序列化（json, dataclasses.asdict）

### 5.1 json.dumps / json.loads

**v6 适用场景：**
- 会议记录序列化
- 辩论状态持久化

```python
import json
from dataclasses import asdict

state = DebateState(...)
json_str = json.dumps(asdict(state), ensure_ascii=False, indent=2)
```

### 5.2 __post_init__ 验证

```python
from dataclasses import dataclass

@dataclass
class DebateState:
    round_num: int
    statements: list
    
    def __post_init__(self):
        if self.round_num < 0:
            raise ValueError("round_num must be non-negative")
```

---

## 6. 时间控制（time, datetime）

### 6.1 time.perf_counter()

```python
import time

start = time.perf_counter()
elapsed = time.perf_counter() - start
```

### 6.2 datetime.timedelta

```python
from datetime import datetime, timedelta

debate_start = datetime.now()
if datetime.now() - debate_start > timedelta(minutes=5):
    pass
```

---

## 7. 迭代工具（itertools）

### 7.1 combinations

**v6 适用场景：** 专家两两冲突检测

```python
from itertools import combinations

for expert_a, expert_b in combinations(experts, 2):
    conflict = check_conflict(statements[expert_a], statements[expert_b])
```

### 7.2 pairwise

```python
from itertools import pairwise

for prev_round, curr_round in pairwise(rounds):
    new_arguments = set(curr_round) - set(prev_round)
```

---

## 8. 堆（heapq）

**v6 适用场景：** 优先级队列

```python
import heapq

priority_queue = []
heapq.heappush(priority_queue, (1 - convergence_score, round_num))
_, best_round = heapq.heappop(priority_queue)
```

---

## 9. 随机采样（random）

**v6 适用场景：** 专家随机排序

```python
import random

random.shuffle(expert_ids)
subset = random.sample(expert_ids, k=min(5, len(expert_ids)))
```

---

## 10. 类型提示（typing）

### 10.1 typing.Protocol

**v5 已用：**
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Perspective(Protocol):
    @property
    def id(self) -> str: ...
    def think(self, input: str, context: dict) -> PerspectiveOutput: ...
```

### 10.2 typing.TypeAlias

**v6 推荐用法：**
```python
from typing import TypeAlias

ExpertID: TypeAlias = str
ArgumentID: TypeAlias = str
RoundNumber: TypeAlias = int
```

---

## 11. 总结

### 推荐使用的标准库

| 模块 | 用途 | 优先级 |
|------|------|--------|
| dataclasses | 数据结构定义 | 必须 |
| concurrent.futures.ThreadPoolExecutor | 并行执行 | 必须 |
| collections.deque | 辩论历史 | 推荐 |
| collections.defaultdict | 数据聚合 | 推荐 |
| collections.Counter | 统计计数 | 推荐 |
| itertools.combinations | 冲突检测 | 推荐 |
| asyncio | 异步 LLM | 建议（可选） |
| json | 序列化 | 必须 |
| typing | 类型提示 | 必须 |

### 不推荐的库

| 模块 | 原因 |
|------|------|
| multiprocessing | 进程开销大，不适合 LLM 调用 |
| threading | 低层 API，concurrent.futures 更好 |

---

_文档版本：Python 标准库可复用能力笔记 v1.0_
