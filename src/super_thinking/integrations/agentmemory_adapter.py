"""
super_thinking + AgentMemory 胶水层 (V 6/15 P1-5 升级版)

P1-5 升级: 之前用 RetrievePipeline 失败 (vector_store/embedder 构造复杂),
改用 BM25Simple — 纯 Python BM25 检索, 不需要 vector store, 不需要 embedder.

P1-5 真集成:
  1. JuryWithMemory.add_memory() → IngestPipeline.run() 写
  2. JuryWithMemory._search() → BM25Simple 检索
  3. JuryWithMemory.think(query) → 检索结果注入 context['memory']
  4. Jury.think(query, context) → tagmemo/msa 这次能拿到真记忆
"""
import sys
import asyncio
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path("/home/fuguang/AgentMemory")))

from agentmemory import IngestPipeline
from agentmemory.pipeline.retrieve import BM25Simple
from super_thinking.core.jury import Jury
from super_thinking.perspectives._interface import PerspectiveOutput


def _memory_item_to_dict(item) -> dict:
    return {
        "text": item.content,
        "source": item.metadata.get("source", "agentmemory") if hasattr(item, "metadata") else "agentmemory",
        "tags": item.metadata.get("tags", []) if hasattr(item, "metadata") else [],
        "id": item.id,
    }


class JuryWithMemory:
    """Jury + AgentMemory 自动注入 context['memory'] (BM25 检索, 无 vector store 依赖)"""

    def __init__(self, default_top_k: int = 5):
        self._jury = Jury()
        self._ingest = IngestPipeline()
        self._bm25 = BM25Simple()
        self._items = []  # MemoryItem 列表 (id → item 索引)
        self._default_top_k = default_top_k
        self._reindex_needed = False

    def add_memory(self, content: str, tags: list[str] = None, **metadata) -> tuple:
        md = {"tags": tags or [], **metadata}
        items, err = asyncio.run(self._ingest.run(content=content, metadata=md))
        self._items.extend(items)
        self._reindex_needed = True
        return items, err

    def _ensure_index(self):
        if self._reindex_needed and self._items:
            self._bm25 = BM25Simple()
            self._bm25.index(self._items)
            self._reindex_needed = False

    def _search(self, query: str, top_k: int) -> list[dict]:
        self._ensure_index()
        if not self._items:
            return []
        # BM25 返 [(id, score)]
        results = self._bm25.search(query, top_k=top_k)
        id_to_item = {it.id: it for it in self._items}
        memories = []
        for mid, score in results:
            if mid in id_to_item and score > 0:
                memories.append(_memory_item_to_dict(id_to_item[mid]))
        return memories

    def think(self, query: str, top_k: Optional[int] = None, mode: str = "auto") -> object:
        k = top_k or self._default_top_k
        memories = self._search(query=query, top_k=k)
        context = {"memory": memories, "query": query}
        return self._jury.think(query, context, mode=mode)


def demo():
    print("=== JuryWithMemory demo (V 6/15) ===\n")
    j = JuryWithMemory()

    # 建 4 条记忆
    docs = [
        ("VCPToolBox 6005 是 VCP 系统的工具调用服务端, 处理 V7.1 协议 TOOL_REQUEST 块", ["vcp", "port"]),
        ("Symphony 18081 是 agent-symphony 编排 API, 暴露 thinking/memory/team/search 4 大端点", ["symphony"]),
        ("AgentMemory 提供 IngestPipeline/RetrievePipeline/CircuitBreaker, M1 升级到 44 个 .py", ["agentmemory"]),
        ("AgentSafety CircuitBreaker 实际工作: 3 次失败后 OPEN, 后续 call 抛 CircuitBreakerError", ["safety"]),
    ]
    for content, tags in docs:
        items, _ = j.add_memory(content=content, tags=tags)
        print(f"  📝 {content[:30]}... → {len(items)} item")

    # 触发 tagmemo/msa 关键词的查询
    queries = [
        "记忆检索: VCP 6005 端口是做什么的",
        "回忆 Symphony 18081",
        "关联: AgentMemory 哪些 pipeline",
        "CircuitBreaker 真工作吗",
    ]

    for q in queries:
        print(f"\n>>> Q: {q}")
        r = j.think(q, top_k=3)
        empty_count = 0
        filled_count = 0
        for pid, out in r.outputs.items():
            if pid in ("tagmemo_perspective", "msa_perspective"):
                is_empty = "为空" in out.analysis
                if is_empty:
                    empty_count += 1
                else:
                    filled_count += 1
                    print(f"  ✅ {pid}: 有记忆 ({len(out.analysis)} chars)")
                    print(f"     首句: {out.analysis.split(chr(10))[1] if chr(10) in out.analysis else out.analysis[:60]}")
        if empty_count and not filled_count:
            print(f"  ❌ {empty_count} 个检索专家仍报空")


if __name__ == "__main__":
    demo()
