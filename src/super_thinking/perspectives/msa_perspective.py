"""MSA Retrieval Perspective - Sparse Attention Memory Retrieval.

Dual routing: Topic-level filter + Token-level refinement.
Memory interleave: iterative 3-round retrieval.
Tiered storage: L1(LCA)->L2(graph)->L3(vector)->L4(full).
"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class MsaPerspective(Perspective):
    """MSA双重路由检索：主题级筛选 + 词元级精筛，记忆交错最多3轮迭代."""

    @property
    def id(self) -> str:
        return "msa_perspective"

    @property
    def name(self) -> str:
        return "MSA检索"

    @property
    def description(self) -> str:
        return "MSA双重路由：主题级粗筛+词元级精筛，配合记忆交错最多3轮迭代，从L1-L4分层存储中检索。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "记忆", "检索", "回忆", "msa", "MSA", "双重路由",
            "迭代检索", "相关记忆", "上下文", "搜索记忆",
            "记得", "以前", "上次",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """Execute MSA dual-routing retrieval analysis."""
        max_rounds = int(context.get("max_rounds", 3)) if context else 3
        top_k = int(context.get("top_k", 5)) if context else 5
        interleave = context.get("interleave", True) if context else True

        # Round 1: Initial retrieval
        round1_result = self._round_retrieval(
            query=input,
            round_num=1,
            top_k=top_k,
        )

        all_results = [round1_result]

        # Decision: is more retrieval needed?
        if interleave and not self._can_answer(input, round1_result):
            round2_result = self._round_retrieval(
                query=self._generate_next_query(input, round1_result),
                round_num=2,
                top_k=top_k,
            )
            all_results.append(round2_result)

            if round2_result["sufficient"] < 0.7 and max_rounds >= 3:
                round3_result = self._round_retrieval(
                    query=self._generate_next_query(input, round2_result),
                    round_num=3,
                    top_k=top_k,
                )
                all_results.append(round3_result)

        # Build final output
        synthesis = self._synthesize(all_results, input)

        analysis = (
            "## 🔍 MSA双重路由检索分析\n\n"
            f"**查询**：{input}\n"
            f"**检索轮数**：{len(all_results)}\n"
            f"**模式**：{'记忆交错' if interleave else '单轮检索'}\n\n"
            "---\n\n"
        )

        for r in all_results:
            analysis += f"### 第{r['round']}轮检索\n"
            analysis += f"**主题路由**：{r['topics']}\n"
            analysis += f"**候选数量**：{r['candidate_count']}条\n"
            analysis += f"**精筛结果**：{r['top_results']}\n"
            analysis += f"**充分度**：{r['sufficient']:.0%}\n\n---\n\n"

        analysis += f"### 综合答案\n{synthesis}"

        return PerspectiveOutput(
            perspective_id="msa_result",
            perspective_name="MSA检索结果",
            analysis=analysis,
            confidence=min(0.9, 0.6 + 0.1 * len(all_results)),
            warnings=[
                "本框架是检索策略分析，实际检索需要配合向量数据库。",
                "检索质量取决于记忆库内容的完整性。",
            ],
            metadata={
                "query": input,
                "rounds": len(all_results),
                "total_candidates": sum(r["candidate_count"] for r in all_results),
            },        )

    def _round_retrieval(self, query: str, round_num: int, top_k: int) -> dict:
        """Single round of dual-routing retrieval."""
        # First routing: topic-level filter
        topics = self._extract_topics(query)

        # Simulate candidate count (in real impl, would query DB)
        candidate_count = len(topics) * 7 + 10

        # Second routing: token-level refinement
        top_results = self._token_level_refine(query, topics, top_k)

        # Assess sufficiency
        sufficient = self._assess_sufficiency(query, top_results)

        return {
            "round": round_num,
            "query": query,
            "topics": topics,
            "candidate_count": candidate_count,
            "top_results": top_results,
            "sufficient": sufficient,
        }

    def _extract_topics(self, query: str) -> list[str]:
        """Extract topic keywords for first-level routing."""
        # Simple extraction: noun phrases and key terms
        import re

        # Common topic patterns
        topic_indicators = [
            "项目", "技术", "产品", "团队", "公司", "市场",
            "用户", "问题", "方案", "设计", "开发", "测试",
            "数据", "模型", "算法", "架构", "系统", "服务",
        ]

        found_topics: list[str] = []
        for indicator in topic_indicators:
            if indicator in query:
                found_topics.append(indicator)

        # Extract quoted terms
        quoted = re.findall(r'"([^"]+)"', query)
        found_topics.extend(quoted[:2])

        # Fallback
        if not found_topics:
            words = query[:20]
            found_topics = [words]

        return found_topics[:5]

    def _token_level_refine(
        self, query: str, topics: list[str], top_k: int
    ) -> list[str]:
        """Token-level refinement within candidate set."""
        # In real impl: would expand query with LCM, then do fine-grained match
        # Heuristic: return topic-tagged result descriptions
        results: list[str] = []
        for topic in topics[:top_k]:
            results.append(f"{topic}相关记录（语义匹配）")
        return results

    def _assess_sufficiency(self, query: str, results: list[str]) -> float:
        """Assess whether retrieval results are sufficient to answer query."""
        if not results:
            return 0.0

        # Check coverage
        query_words = set(query)
        result_text = " ".join(results)
        coverage = sum(1 for w in query_words if w in result_text) / max(len(query_words), 1)

        # Penalize empty results
        if len(results) == 0:
            return 0.0

        # Base sufficiency on result count and coverage
        count_factor = min(1.0, len(results) / 5)
        sufficiency = (coverage * 0.4 + count_factor * 0.6)

        return sufficiency

    def _can_answer(self, query: str, retrieval_result: dict) -> bool:
        """Check if the retrieval result is sufficient to answer the query."""
        sufficient = retrieval_result.get("sufficient", 0)
        return sufficient >= 0.8

    def _generate_next_query(self, original: str, prev_result: dict) -> str:
        """Generate the next query based on previous retrieval gaps."""
        gaps: list[str] = []

        # Identify gaps based on insufficient topics
        prev_topics = prev_result.get("topics", [])
        prev_sufficient = prev_result.get("sufficient", 0)

        if prev_sufficient < 0.5:
            gaps.append("背景信息")
        if len(prev_result.get("top_results", [])) < 3:
            gaps.append("详细信息")

        # Construct next query
        gap_str = " ".join(gaps) if gaps else "补充信息"
        next_query = f"{original} {gap_str}"

        return next_query

    def _synthesize(self, all_results: list[dict], original_query: str) -> str:
        """Synthesize final answer from all retrieval rounds."""
        if not all_results:
            return "未检索到相关信息。"

        # Aggregate all results
        all_topics = []
        all_result_texts: list[str] = []
        for r in all_results:
            all_topics.extend(r["topics"])
            all_result_texts.extend(r["top_results"])

        # Deduplicate
        unique_topics = list(dict.fromkeys(all_topics))[:10]
        unique_results = list(dict.fromkeys(all_result_texts))[:10]

        synthesis: list[str] = []
        synthesis.append(f"**涉及主题（{len(unique_topics)}个）**：")
        for t in unique_topics:
            synthesis.append(f"• {t}")

        synthesis.append(f"\n**相关记忆片段（{len(unique_results)}条）**：")
        for i, res in enumerate(unique_results[:5], 1):
            synthesis.append(f"{i}. {res}")

        synthesis.append(f"\n**检索结论**：")
        if len(all_results) == 1:
            synthesis.append("单轮检索基本满足查询需求。")
        elif len(all_results) == 2:
            synthesis.append("双轮检索补充了背景和细节信息。")
        else:
            synthesis.append("三轮记忆交错检索，全面覆盖查询需求。")

        return "\n".join(synthesis)
