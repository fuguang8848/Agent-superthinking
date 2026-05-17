"""MSA Retrieval Perspective - Sparse Attention Memory Retrieval.

Dual routing: Topic-level filter + Token-level refinement.
Memory interleave: iterative 3-round retrieval.
Tiered storage: L1(LCA)->L2(graph)->L3(vector)->L4(full).

可移植设计：
- 不依赖任何外部数据库或API
- 记忆数据通过 context["memory"] 传入（list of dict/text）
- 任何框架只要把记忆传入 context 即可使用
"""

import re
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class MsaPerspective(Perspective):
    """MSA双重路由检索：主题级筛选 + 词元级精筛，记忆交错最多3轮迭代。"""

    @property
    def id(self) -> str:
        return "msa_perspective"

    @property
    def name(self) -> str:
        return "MSA检索"

    @property
    def description(self) -> str:
        return (
            "MSA双重路由检索：从context['memory']传入的记忆中，"
            "通过主题级粗筛+词元级精筛+多轮迭代，提取与问题最相关的记忆片段。"
        )

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "记忆", "检索", "回忆", "msa", "MSA", "双重路由",
            "迭代检索", "相关记忆", "上下文", "搜索记忆",
            "记得", "以前", "上次",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """
        执行 MSA 双重路由检索。

        context 支持的键（可移植，任何框架都能传）：
        - memory: list[dict] 或 list[str]，记忆条目列表
        - max_rounds: 迭代轮数上限（默认3）
        - top_k: 每轮返回的最多结果数（默认5）
        """
        # ── 兼容多种 memory 格式 ──
        raw_memory = context.get("memory", []) if context else []
        memories = self._normalize_memories(raw_memory)

        max_rounds = int(context.get("max_rounds", 3)) if context else 3
        top_k = int(context.get("top_k", 5)) if context else 5

        if not memories:
            return PerspectiveOutput(
                perspective_id="msa_result",
                perspective_name="MSA检索结果",
                analysis=(
                    "## 🔍 MSA双重路由检索\n\n"
                    f"**查询**：{input}\n\n"
                    "**结果**：context['memory'] 为空，未检索到任何记忆。\n\n"
                    "请在 context['memory'] 中传入记忆列表（list[dict] 或 list[str]）。"
                ),
                key_points=["context['memory'] 为空，无法检索"],
                confidence=0.0,
                warnings=["缺少记忆数据——context['memory'] 为空或格式不支持"],
                metadata={"query": input, "rounds": 0, "memory_count": 0},
            )

        # ── 第一轮：主题路由 ──
        topics = self._extract_topics(input)
        round1 = self._round_retrieval(input, topics, memories, round_num=1, top_k=top_k)
        all_results = [round1]

        # ── 后续轮：记忆交错 ──
        if round1["sufficient"] < 0.7 and max_rounds >= 2:
            next_query = self._generate_next_query(input, round1)
            topics2 = self._extract_topics(next_query)
            round2 = self._round_retrieval(next_query, topics2, memories, round_num=2, top_k=top_k)
            all_results.append(round2)

            if round2["sufficient"] < 0.6 and max_rounds >= 3:
                next_query2 = self._generate_next_query(next_query, round2)
                topics3 = self._extract_topics(next_query2)
                round3 = self._round_retrieval(next_query2, topics3, memories, round_num=3, top_k=top_k)
                all_results.append(round3)

        # ── 综合 ──
        synthesis = self._synthesize(all_results, input, memories)

        analysis_parts = [
            f"## 🔍 MSA双重路由检索分析\n",
            f"**查询**：{input}",
            f"**记忆总量**：{len(memories)} 条",
            f"**实际检索轮数**：{len(all_results)}",
            f"**提取的主题**：{' / '.join(all_results[0]['topics']) if all_results else '无'}",
            "\n---\n",
        ]

        for r in all_results:
            analysis_parts.append(f"### 第{r['round']}轮检索")
            analysis_parts.append(f"**主题路由**：{' / '.join(r['topics'])}")
            analysis_parts.append(f"**候选数**：{r['candidate_count']} 条")
            analysis_parts.append(f"**充分度**：{r['sufficient']:.0%}")
            if r["top_results"]:
                analysis_parts.append(f"**命中记忆**：")
                for item in r["top_results"][:5]:
                    snippet = item["text"][:120].replace("\n", " ")
                    analysis_parts.append(f"  • [{item['relevance']:.0%}] {snippet}...")
            analysis_parts.append("")

        analysis_parts.append(f"### 综合答案\n{synthesis}")

        return PerspectiveOutput(
            perspective_id="msa_result",
            perspective_name="MSA检索结果",
            analysis="\n".join(analysis_parts),
            key_points=[r["top_results"][0]["text"][:80] + "..." for r in all_results if r["top_results"]][:3],
            confidence=min(0.9, 0.5 + 0.15 * len(all_results)),
            warnings=[],
            metadata={
                "query": input,
                "rounds": len(all_results),
                "memory_count": len(memories),
                "total_candidates": sum(r["candidate_count"] for r in all_results),
            },
        )

    def _normalize_memories(self, raw: list) -> list[dict]:
        """兼容多种 memory 格式，全部转为 {text, source?} 格式。"""
        memories = []
        for item in raw:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or item.get("memory") or str(item)
                memories.append({"text": text, "source": item.get("source", "context")})
            elif isinstance(item, str):
                memories.append({"text": item, "source": "context"})
        return memories

    def _extract_topics(self, query: str) -> list[str]:
        """主题词提取（第一层路由）。"""
        topic_indicators = [
            "项目", "技术", "产品", "团队", "公司", "市场",
            "用户", "问题", "方案", "设计", "开发", "测试",
            "数据", "模型", "算法", "架构", "系统", "服务",
            "训练", "语料", "部署", "服务器", "API", "论文",
            "进度", "决策", "风险", "战略", "竞争", "答辩",
            "省赛", "校赛", "准确率", "语料", "翻译", "训练",
            "移动端", "量化", "ONNX", "M4T", "NLLB",
        ]
        found = [w for w in topic_indicators if w in query]
        # 补充查询中的所有2-4字中文词
        found.extend(re.findall(r'[\u4e00-\u9fff]{2,4}', query))
        return list(dict.fromkeys(found))[:8]

    def _round_retrieval(self, query: str, topics: list[str], memories: list[dict], round_num: int, top_k: int) -> dict:
        """一轮双重路由检索。"""
        query_lower = query.lower()
        topic_lower = [t.lower() for t in topics]

        # 第一层：主题过滤
        topic_matched = []
        for i, m in enumerate(memories):
            text_lower = m["text"].lower()
            score = sum(1 for t in topic_lower if t in text_lower)
            if score > 0:
                topic_matched.append((i, score, m))

        # 第二层：词元级精筛（关键词重叠度）
        query_tokens = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', query_lower))
        scored = []
        for i, topic_score, m in topic_matched:
            text_tokens = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', m["text"].lower()))
            overlap = len(query_tokens & text_tokens) / max(len(query_tokens), 1)
            total_score = topic_score * 0.4 + overlap * 0.6
            scored.append((i, total_score, m))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_results = [
            {"text": m["text"], "relevance": score, "source": m.get("source", "unknown")}
            for _, score, m in scored[:top_k]
        ]

        candidate_count = len(topic_matched)
        sufficient = self._assess_sufficiency(query, top_results, candidate_count)

        return {
            "round": round_num,
            "topics": topics,
            "candidate_count": candidate_count,
            "top_results": top_results,
            "sufficient": sufficient,
        }

    def _assess_sufficiency(self, query: str, results: list[dict], candidate_count: int) -> float:
        """评估检索充分度。"""
        if not results:
            return 0.0
        avg_relevance = sum(r["relevance"] for r in results) / len(results)
        count_factor = min(1.0, candidate_count / 10)
        return avg_relevance * 0.5 + count_factor * 0.5

    def _generate_next_query(self, original: str, prev_result: dict) -> str:
        """基于前轮缺口生成下一轮查询。"""
        gaps = []
        if prev_result["sufficient"] < 0.4:
            gaps.append("背景")
        if prev_result["candidate_count"] < 3:
            gaps.append("详情")
        gap_str = " ".join(gaps) if gaps else "补充"
        return f"{original} {gap_str}"

    def _synthesize(self, all_results: list[dict], original_query: str, memories: list[dict]) -> str:
        """综合所有轮次结果，生成最终答案。"""
        # 收集所有命中的记忆，去重
        seen_texts = set()
        all_hits = []
        for r in all_results:
            for item in r["top_results"]:
                if item["text"] not in seen_texts:
                    seen_texts.add(item["text"])
                    all_hits.append(item)

        if not all_hits:
            return (
                "**结论**：记忆库中未找到与查询直接相关的内容。\n"
                "建议：检查传入的 memory 数据是否包含相关信息，或尝试换用其他视角（如 magi_debate）分析。"
            )

        # 按相关性排序
        all_hits.sort(key=lambda x: x["relevance"], reverse=True)

        lines = [f"**共找到 {len(all_hits)} 条相关记忆（去重后）**：\n"]
        for i, item in enumerate(all_hits[:5], 1):
            snippet = item["text"][:150].replace("\n", " ").strip()
            lines.append(f"{i}. [{item['relevance']:.0%}] {snippet}...")

        lines.append(f"\n**检索质量评估**：")
        if len(all_hits) >= 3 and all_hits[0]["relevance"] > 0.5:
            lines.append("✅ 高相关——前几条记忆与查询高度匹配")
        elif len(all_hits) >= 1:
            lines.append("⚠️ 中等相关——记忆存在但关联度有限，可能需要补充记忆数据")
        else:
            lines.append("❌ 低相关——记忆库内容与查询关联较弱")

        return "\n".join(lines)
