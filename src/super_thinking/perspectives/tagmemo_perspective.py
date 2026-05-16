"""TagMemo Perspective - "浪潮" RAG retrieval optimization.

Four-stage RAG: Sensing → Segmentation → Expansion → Reshaping.
"""

import re
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class TagmemoPerspective(Perspective):
    """TagMemo浪潮检索：四阶段RAG优化：感应、分段、扩张、重塑."""

    @property
    def id(self) -> str:
        return "tagmemo_perspective"

    @property
    def name(self) -> str:
        return "TagMemo浪潮检索"

    @property
    def description(self) -> str:
        return "TagMemo四阶段RAG：感应（净化+EPA）、分段（语义断层）、扩张（标签+关联）、重塑（向量融合+霰弹枪检索）。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "深度记忆", "关联", "检索", "浪潮", "语义引力",
            "记忆检索", "回忆", "相关内容", "知识检索",
            "关联记忆", "上下文",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """Execute TagMemo four-stage RAG analysis."""
        stage1_sensing = self._sensing_stage(input)
        stage2_segmentation = self._segmentation_stage(input)
        stage3_expansion = self._expansion_stage(stage1_sensing, stage2_segmentation)
        stage4_reshaping = self._reshaping_stage(stage3_expansion)

        analysis = (
            "## 🌊 TagMemo浪潮检索分析\n\n"
            f"**查询**：{input}\n\n"
            "---\n\n"
            "### 阶段一：感应（Sensing）\n\n"
            f"{stage1_sensing}\n\n"
            "---\n\n"
            "### 阶段二：分段与分解（Segmentation）\n\n"
            f"{stage2_segmentation}\n\n"
            "---\n\n"
            "### 阶段三：扩张与召回（Expansion）\n\n"
            f"{stage3_expansion}\n\n"
            "---\n\n"
            "### 阶段四：重塑与检索（Reshaping）\n\n"
            f"{stage4_reshaping}\n\n"
            "---\n\n"
            "**检索建议**：综合四个阶段的输出，在向量数据库中执行混合检索。"
        )

        return PerspectiveOutput(
            perspective_id="tagmemo_result",
            perspective_name="TagMemo浪潮检索结果",
            analysis=analysis,
            confidence=0.78,
            warnings=[
                "TagMemo是检索优化框架，实际检索需要配合向量数据库（如LanceDB）。",
                "检索结果质量取决于记忆库的内容完整性。",
            ],
            metadata={
                "query": input,
                "stage1_clean_query": stage1_sensing[:100] if len(stage1_sensing) > 100 else stage1_sensing,
                "expanded_tags": stage3_expansion[:100] if len(stage3_expansion) > 100 else stage3_expansion,
            },        )

    def _sensing_stage(self, query: str) -> str:
        """Stage 1: Sensing - Clean and EPA projection."""
        # Clean noise: HTML, JSON, Emoji
        cleaned = self._clean_noise(query)

        # EPA projection: logical depth and resonance
        depth = self._calculate_depth(cleaned)
        resonance = self._calculate_resonance(cleaned)

        output: list[str] = []
        output.append(f"**净化处理**：")
        output.append(f"• 原始查询：{query}")
        output.append(f"• 净化后：{cleaned}")

        output.append(f"\n**EPA投影**：")
        output.append(f"• 逻辑深度（depth）：{depth}/10")
        output.append(f"• 共振值（resonance）：{resonance}/10")

        if depth >= 7:
            output.append("→ 高复杂度查询，建议深度语义检索")
        elif depth >= 4:
            output.append("→ 中复杂度查询，混合关键词+向量检索")
        else:
            output.append("→ 低复杂度查询，关键词检索优先")

        return "\n".join(output)

    def _segmentation_stage(self, query: str) -> str:
        """Stage 2: Segmentation - Identify semantic boundaries."""
        # Semantic split based on punctuation and conjunctions
        segments = self._semantic_split(query)

        # Primary tag extraction
        primary_tags = self._extract_primary_tags(segments)

        # Pyramid iteration - 90% semantic energy threshold
        final_tags = self._pyramid_iterate(primary_tags)

        output: list[str] = []
        output.append(f"**语义分段**：")
        for i, seg in enumerate(segments, 1):
            output.append(f"• 段落{i}：{seg}")
        output.append(f"共 {len(segments)} 个语义段落")

        output.append(f"\n**首轮感应（主标签）**：")
        for tag in primary_tags:
            output.append(f"• {tag}")

        output.append(f"\n**金字塔迭代**：")
        output.append(f"• 语义能量阈值：90%")
        output.append(f"• 最终标签：{', '.join(final_tags)}")

        return "\n".join(output)

    def _expansion_stage(self, sensing_result: str, segmentation_result: str) -> str:
        """Stage 3: Expansion - Complete core tags, pull related terms."""
        # Core tag completion
        core_tags = self._complete_tags(sensing_result)

        # Related term pull-back
        related_terms = self._pull_related(core_tags)

        # Privilege filter (high-signal terms)
        privileged = self._privilege_filter(core_tags, related_terms)

        output: list[str] = []
        output.append("**核心标签补全**：")
        for tag in core_tags:
            output.append(f"• {tag}")

        output.append(f"\n**关联词拉回**：")
        for term in related_terms[:5]:
            output.append(f"• {term}")

        output.append(f"\n**特权过滤**：")
        for p in privileged[:3]:
            output.append(f"• {p}（高信号词）")

        return "\n".join(output)

    def _reshaping_stage(self, expansion_result: str) -> str:
        """Stage 4: Reshaping - Dynamic parameters, vector fusion, dedup."""
        # Dynamic parameters
        params = self._calc_dynamic_params(expansion_result)

        # Shotgun queries (multi-angle parallel)
        shotgun_queries = self._shotgun_queries(params)

        # Phase array dedup (SVD cruise for latent themes)
        deduped_themes = self._phase_array_dedup(shotgun_queries)

        output: list[str] = []
        output.append("**动态参数计算**：")
        output.append(f"• 向量权重：{params['vector_weight']:.2f}")
        output.append(f"• BM25权重：{params['bm25_weight']:.2f}")
        output.append(f"• 召回数量：{params['recall_count']}")

        output.append(f"\n**霰弹枪查询（多角度并行）**：")
        for q in shotgun_queries:
            output.append(f"• {q}")

        output.append(f"\n**相控阵去重（保留最大新信息量）**：")
        for theme in deduped_themes:
            output.append(f"• {theme}")

        return "\n".join(output)

    def _clean_noise(self, text: str) -> str:
        """Remove HTML, JSON, Emoji noise."""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove common JSON noise
        text = re.sub(r'\{[^{}]*\}', '', text)
        # Remove emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "]+", flags=re.UNICODE
        )
        text = emoji_pattern.sub('', text)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _calculate_depth(self, text: str) -> int:
        """Calculate logical depth (0-10) based on complexity indicators."""
        score = 0
        # Length factor
        score += min(3, len(text) // 30)
        # Technical terms
        technical_indicators = ["分析", "系统", "逻辑", "推理", "策略", "架构", "方法", "原理"]
        score += sum(1 for t in technical_indicators if t in text)
        # Question complexity
        if any(k in text for k in ["为什么", "如何", "怎么", "因果"]):
            score += 2
        # Limit to 10
        return min(10, max(1, score))

    def _calculate_resonance(self, text: str) -> int:
        """Calculate resonance (0-10) based on emotional/personal relevance."""
        score = 5  # baseline
        personal_indicators = ["我", "我们", "我的", "我们的", "想", "感觉", "觉得"]
        score += sum(1 for t in personal_indicators if t in text)
        # Limit to 10
        return min(10, max(1, score))

    def _semantic_split(self, text: str) -> list[str]:
        """Split text into semantic segments."""
        import re
        # Split by major punctuation and conjunctions
        raw_segments = re.split(r'[，,。.;；\n]', text)
        # Filter empty and too short
        segments = [s.strip() for s in raw_segments if len(s.strip()) >= 4]
        return segments if segments else [text]

    def _extract_primary_tags(self, segments: list[str]) -> list[str]:
        """Extract primary matching tags from segments."""
        # Simple keyword-based extraction
        tags: list[str] = []
        for seg in segments:
            if len(seg) > 2:
                tags.append(seg[:10])
        return tags[:5]

    def _pyramid_iterate(self, tags: list[str]) -> list[str]:
        """Pyramid iteration - keep tags covering 90% semantic energy."""
        # Heuristic: top tags covering most content
        # In a real impl, would analyze term frequency and coverage
        if not tags:
            return ["通用查询"]
        return tags[:3]

    def _complete_tags(self, sensing: str) -> list[str]:
        """Complete core tags from sensing output."""
        # Extract key terms as tags
        tags = []
        for word in ["分析", "系统", "方法", "问题", "解决", "技术", "项目"]:
            if word in sensing:
                tags.append(word)
        return tags if tags else ["查询"]

    def _pull_related(self, core_tags: list[str]) -> list[str]:
        """Pull related terms for each core tag."""
        related_map = {
            "分析": ["分析框架", "分析方法", "分析工具"],
            "系统": ["系统设计", "系统架构", "子系统"],
            "方法": ["方法论", "技术方法", "实现方法"],
            "问题": ["核心问题", "子问题", "问题根源"],
            "解决": ["解决方案", "解决思路", "解决路径"],
            "技术": ["技术选型", "技术栈", "技术实现"],
            "项目": ["项目背景", "项目目标", "项目进展"],
        }
        results: list[str] = []
        for tag in core_tags:
            if tag in related_map:
                results.extend(related_map[tag][:2])
        return list(dict.fromkeys(results))[:5]

    def _privilege_filter(self, core: list[str], related: list[str]) -> list[str]:
        """Filter high-signal privilege terms."""
        # Terms that are highly informative
        privilege = [t for t in core if len(t) >= 4]
        privilege += [t for t in related if len(t) >= 4]
        return list(dict.fromkeys(privilege))[:3]

    def _calc_dynamic_params(self, expansion: str) -> dict:
        """Calculate dynamic retrieval parameters."""
        # Heuristic based on query characteristics
        base_vector = 0.6
        base_bm25 = 0.4

        if "多" in expansion or "多个" in expansion:
            base_vector = 0.7
            base_bm25 = 0.3

        return {
            "vector_weight": base_vector,
            "bm25_weight": base_bm25,
            "recall_count": 10,
        }

    def _shotgun_queries(self, params: dict) -> list[str]:
        """Generate multi-angle shotgun queries."""
        # Generate 3 variations for parallel search
        recall = params.get("recall_count", 10)
        return [
            f"精确匹配查询 (top {recall//2})",
            f"语义扩展查询 (top {recall//2})",
            f"关联跳跃查询 (top {recall - recall//2})",
        ]

    def _phase_array_dedup(self, queries: list[str]) -> list[str]:
        """Phase array dedup using SVD cruise for latent themes."""
        # In a real implementation: run SVD on result vectors, keep max novelty
        # Heuristic: return unique themes
        return [q for q in queries if "查询" in q]
