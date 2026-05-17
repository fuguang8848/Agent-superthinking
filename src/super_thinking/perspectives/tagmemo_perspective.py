"""TagMemo Perspective - "浪潮" RAG retrieval optimization.

Four-stage RAG: Sensing → Segmentation → Expansion → Reshaping.

可移植设计：
- 不依赖任何外部数据库或API
- 记忆数据通过 context["memory"] 传入
- 任何框架只要把记忆传入 context 即可使用
"""

import re
from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class TagmemoPerspective(Perspective):
    """TagMemo浪潮检索：四阶段RAG优化：感应、分段、扩张、重塑。"""

    @property
    def id(self) -> str:
        return "tagmemo_perspective"

    @property
    def name(self) -> str:
        return "TagMemo浪潮检索"

    @property
    def description(self) -> str:
        return (
            "TagMemo四阶段RAG分析：从context['memory']中提取记忆，"
            "通过感应（净化+EPA）、分段（语义断层）、扩张（标签扩展）、重塑（相关性重排）四阶段，"
            "输出语义标签和重排后的记忆顺序。"
        )

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "深度记忆", "关联", "检索", "浪潮", "语义引力",
            "记忆检索", "回忆", "相关内容", "知识检索",
            "关联记忆", "上下文",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """
        执行 TagMemo 四阶段检索。

        context 支持的键（可移植）：
        - memory: list[dict] 或 list[str]，记忆条目列表
        """
        # ── 兼容多种 memory 格式 ──
        raw_memory = context.get("memory", []) if context else []
        memories = self._normalize_memories(raw_memory)

        if not memories:
            return PerspectiveOutput(
                perspective_id="tagmemo_result",
                perspective_name="TagMemo浪潮检索结果",
                analysis=(
                    "## 🌊 TagMemo浪潮检索\n\n"
                    f"**查询**：{input}\n\n"
                    "**结果**：context['memory'] 为空，未检索到任何记忆。"
                ),
                key_points=["context['memory'] 为空，无法检索"],
                confidence=0.0,
                warnings=["缺少记忆数据——context['memory'] 为空或格式不支持"],
                metadata={"query": input, "stages_run": 0},
            )

        # ── 四阶段处理 ──
        stage1 = self._sensing_stage(input)
        stage2 = self._segmentation_stage(input, memories)
        stage3 = self._expansion_stage(input, stage2["primary_tags"], memories)
        stage4 = self._reshaping_stage(input, stage3["expanded_memories"])

        analysis = "\n".join([
            f"## 🌊 TagMemo浪潮检索分析\n",
            f"**查询**：{input}",
            f"**记忆量**：{len(memories)} 条",
            "",
            "---",
            "### 阶段一：感应（Sensing）",
            f"**净化**：`{stage1['cleaned']}`",
            f"**EPA · 逻辑深度**：{stage1['depth']}/10",
            f"**EPA · 共振值**：{stage1['resonance']}/10",
            f"→ {'高' if stage1['depth']>=7 else '中' if stage1['depth']>=4 else '低'}复杂度查询，{stage1['recommendation']}",
            "",
            "---",
            "### 阶段二：分段与分解（Segmentation）",
            f"**语义段落数**：{len(stage2['segments'])}",
            f"**主标签**：{' / '.join(stage2['primary_tags'])}",
            f"**语义断层检测**：{stage2['断层检测']}",
            "",
            "---",
            "### 阶段三：扩张与召回（Expansion）",
            f"**扩展标签**：{' / '.join(stage3['expanded_tags'])}",
            f"**关联召回记忆数**：{len(stage3['expanded_memories'])} 条",
            f"**高信号特权词**：{' / '.join(stage3['privileged'])}",
            "",
            "---",
            "### 阶段四：重塑与检索（Reshaping）",
            f"**动态权重**：向量 {stage4['params']['vector_weight']:.0%} / BM25 {stage4['params']['bm25_weight']:.0%}",
            f"**霰弹枪角度数**：{len(stage4['shotgun_queries'])}",
            f"**最终排序（Top {len(stage4['final_order'])}）**：",
            *[f"  {i+1}. [{m['score']:.0%}] {m['text'][:80]}..." for i, m in enumerate(stage4["final_order"][:5])],
        ])

        return PerspectiveOutput(
            perspective_id="tagmemo_result",
            perspective_name="TagMemo浪潮检索结果",
            analysis=analysis,
            key_points=[
                f"EPA深度{stage1['depth']}/10，共振{stage1['resonance']}/10",
                f"主标签：{' / '.join(stage2['primary_tags'][:3])}",
                f"扩展标签：{' / '.join(stage3['expanded_tags'][:3])}",
                f"召回{len(stage3['expanded_memories'])}条记忆，重排后Top{len(stage4['final_order'])}",
            ],
            confidence=0.82,
            warnings=[],
            metadata={
                "query": input,
                "memory_count": len(memories),
                "stages_run": 4,
                "primary_tags": stage2["primary_tags"],
                "expanded_tags": stage3["expanded_tags"],
            },
        )

    def _normalize_memories(self, raw: list) -> list[dict]:
        """兼容多种 memory 格式。"""
        memories = []
        for item in raw:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or item.get("memory") or str(item)
                memories.append({"text": text, "source": item.get("source", "context")})
            elif isinstance(item, str):
                memories.append({"text": item, "source": "context"})
        return memories

    # ── 阶段一：感应 ──
    def _sensing_stage(self, query: str) -> dict:
        cleaned = self._clean_noise(query)
        depth = self._calculate_depth(cleaned)
        resonance = self._calculate_resonance(cleaned)
        return {
            "cleaned": cleaned,
            "depth": depth,
            "resonance": resonance,
            "recommendation": "深度语义检索" if depth >= 7 else "混合关键词+向量检索" if depth >= 4 else "关键词检索优先",
        }

    def _clean_noise(self, text: str) -> str:
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\{[^{}]*\}', '', text)
        emoji = re.compile("[" "\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF" "]+", flags=re.UNICODE)
        text = emoji.sub('', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:100]

    def _calculate_depth(self, text: str) -> int:
        score = min(3, len(text) // 30)
        tech = ["分析", "系统", "逻辑", "推理", "策略", "架构", "方法", "原理", "算法", "模型"]
        score += sum(1 for t in tech if t in text)
        if any(k in text for k in ["为什么", "如何", "怎么", "因果"]):
            score += 2
        return min(10, max(1, score))

    def _calculate_resonance(self, text: str) -> int:
        score = 5
        personal = ["我", "我们", "我的", "想", "感觉", "觉得", "关心"]
        score += sum(1 for t in personal if t in text)
        return min(10, max(1, score))

    # ── 阶段二：分段 ──
    def _segmentation_stage(self, query: str, memories: list[dict]) -> dict:
        segments = self._semantic_split(query)
        primary_tags = self._extract_primary_tags(query, segments)
        断层检测 = self._detect_semantic_gaps(segments, memories)
        return {
            "segments": segments,
            "primary_tags": primary_tags,
            "断层检测": 断层检测,
        }

    def _semantic_split(self, text: str) -> list[str]:
        raw = re.split(r'[，,。.;；\n？！?!]', text)
        return [s.strip() for s in raw if len(s.strip()) >= 3][:8]

    def _extract_primary_tags(self, query: str, segments: list[str]) -> list[str]:
        all_text = query + " " + " ".join(segments)
        keywords = [
            "项目", "技术", "产品", "团队", "公司", "市场", "用户",
            "问题", "方案", "设计", "开发", "训练", "语料", "模型",
            "算法", "架构", "系统", "服务", "进度", "决策", "风险",
            "战略", "竞争", "成本", "数据", "服务器", "API",
        ]
        found = [w for w in keywords if w in all_text]
        if len(found) < 2:
            found.extend(re.findall(r'[\w\u4e00-\u9fff]{2,4}', query)[:3])
        return list(dict.fromkeys(found))[:6]

    def _detect_semantic_gaps(self, segments: list[str], memories: list[dict]) -> str:
        memory_texts = " ".join(m["text"] for m in memories)
        gaps = []
        for seg in segments:
            if not any(seg in m["text"] for m in memories):
                gaps.append(seg[:8])
        if not gaps:
            return "未发现明显语义断层"
        return f"发现 {len(gaps)} 处断层：{' / '.join(gaps[:3])}"

    # ── 阶段三：扩张 ──
    def _expansion_stage(self, query: str, primary_tags: list[str], memories: list[dict]) -> dict:
        expanded_tags = self._expand_tags(primary_tags, query)
        privileged = [t for t in expanded_tags if len(t) >= 3]
        expanded_memories = self._recall_related(expanded_tags, memories)
        return {
            "expanded_tags": expanded_tags,
            "privileged": privileged[:3],
            "expanded_memories": expanded_memories,
        }

    def _expand_tags(self, tags: list[str], query: str) -> list[str]:
        expansion_map = {
            "项目": ["石榴籽", "挑战杯", "省赛", "训练", "语料", "模型"],
            "技术": ["SEAMLESSM4T", "NLLB", "IPA", "微调", "量化", "ONNX"],
            "产品": ["翻译", "语音", "文本", "端到端", "移动端"],
            "团队": ["魏会恩", "白翌平", "敏浩", "优优", "蒙小燕"],
            "训练": ["epochs", "loss", "优化器", "梯度", "收敛"],
            "语料": ["东乡语", "蒙古语", "音频", "例句", "IPA"],
            "模型": ["M4T", "NLLB", "LLM", "embedding"],
            "风险": ["黑天鹅", "尾部风险", "过拟合", "漂移"],
            "决策": ["权衡", "取舍", "优先级", "资源分配"],
        }
        expanded = list(tags)
        for tag in tags:
            if tag in expansion_map:
                expanded.extend(expansion_map[tag][:3])
        expanded.extend(re.findall(r'[\w\u4e00-\u9fff]{2,4}', query))
        return list(dict.fromkeys(expanded))[:12]

    def _recall_related(self, tags: list[str], memories: list[dict]) -> list[dict]:
        if not memories:
            return []
        scored = []
        tag_lower = [t.lower() for t in tags]
        for m in memories:
            text_lower = m["text"].lower()
            score = sum(1 for t in tag_lower if t in text_lower) / max(len(tag_lower), 1)
            scored.append({"text": m["text"], "source": m.get("source", "context"), "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return [m for m in scored if m["score"] > 0]

    # ── 阶段四：重塑 ──
    def _reshaping_stage(self, query: str, memories: list[dict]) -> dict:
        params = self._calc_dynamic_params(query, memories)
        shotgun = self._shotgun_queries(query, params)
        final_order = self._rerank(query, memories, params)
        return {
            "params": params,
            "shotgun_queries": shotgun,
            "final_order": final_order,
        }

    def _calc_dynamic_params(self, query: str, memories: list[dict]) -> dict:
        depth = self._calculate_depth(query)
        if depth >= 7:
            return {"vector_weight": 0.75, "bm25_weight": 0.25, "recall_count": 15}
        elif depth >= 4:
            return {"vector_weight": 0.60, "bm25_weight": 0.40, "recall_count": 10}
        else:
            return {"vector_weight": 0.30, "bm25_weight": 0.70, "recall_count": 8}

    def _shotgun_queries(self, query: str, params: dict) -> list[str]:
        return [
            f"精确关键词匹配 (权重BM25={params['bm25_weight']:.0%})",
            f"语义向量相似 (权重{params['vector_weight']:.0%})",
            f"关联标签扩展 ({params['recall_count']}条)",
        ]

    def _rerank(self, query: str, memories: list[dict], params: dict) -> list[dict]:
        if not memories:
            return []
        vw = params["vector_weight"]
        bw = params["bm25_weight"]
        query_tokens = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', query.lower()))
        scored = []
        for m in memories:
            text_lower = m["text"].lower()
            text_tokens = set(re.findall(r'[\w\u4e00-\u9fff]{2,}', text_lower))
            bm25_score = len(query_tokens & text_tokens) / max(len(query_tokens), 1)
            vec_score = m.get("score", 0.5)
            combined = vec_score * vw + bm25_score * bw
            scored.append({**m, "score": combined})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:10]
