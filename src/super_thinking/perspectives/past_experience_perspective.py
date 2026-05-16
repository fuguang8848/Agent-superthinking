"""Past Experience Perspective - 过往经历视角

调用上下文中的历史记忆，分析"以前类似情况怎么做"。
触发关键词: 以前、上次、之前、过去、曾经、历史、经验
"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class PastExperiencePerspective(Perspective):
    """过往经历视角：关联历史经验，为当前问题提供参考路径."""

    @property
    def id(self) -> str:
        return "past_experience_perspective"

    @property
    def name(self) -> str:
        return "过往经历视角"

    @property
    def description(self) -> str:
        return "调用上下文中的历史记忆，分析'以前类似情况怎么做'，从历史经验中提取可复用的教训和成功因素。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "以前", "上次", "之前", "过去", "曾经", "历史",
            "经验", "记得", "以前做过", "类似情况", "参照",
            "过去怎么", "以前遇到", "和上次", "和以前",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """Execute past experience-based analysis."""
        # 从 context 中提取历史记忆
        memory_data = self._extract_memory(context)
        similar_cases = self._find_similar_cases(input, context, memory_data)
        lessons = self._extract_lessons(similar_cases, memory_data)
        recommendations = self._generate_recommendations(input, similar_cases, lessons)

        analysis_parts = [
            "## 📜 过往经历分析\n",
            f"**当前问题**: {input}\n",
            "---\n",
            "### 🔄 类似经历回顾\n",
        ]

        if similar_cases:
            for i, case in enumerate(similar_cases, 1):
                analysis_parts.append(f"**案例{i}**: {case.get('summary', '无描述')}")
                analysis_parts.append(f"  时间: {case.get('when', '未知')}")
                analysis_parts.append(f"  结果: {case.get('outcome', '未知')}")
                analysis_parts.append("")
        else:
            analysis_parts.append("未在历史记忆中找到直接相关案例。\n")
            analysis_parts.append("尝试扩大搜索范围或从相邻领域寻找类似经验...\n")

        analysis_parts.extend([
            "### 📖 历史教训\n",
        ])

        if lessons:
            for lesson in lessons:
                analysis_parts.append(f"- **{lesson['what']}**")
                analysis_parts.append(f"  来源: {lesson['source']}")
                if lesson.get('applicability'):
                    analysis_parts.append(f"  适用性: {lesson['applicability']}")
                analysis_parts.append("")
        else:
            analysis_parts.append("从当前问题出发，推演历史可能提供的教训:\n")
            derived_lessons = self._derive_lessons_from_input(input)
            for lesson in derived_lessons:
                analysis_parts.append(f"- {lesson}\n")

        analysis_parts.extend([
            "### ✅ 基于经验的下一步行动\n",
        ])

        for i, rec in enumerate(recommendations, 1):
            analysis_parts.append(f"{i}. {rec}\n")

        analysis_parts.extend([
            "---\n",
            "### 💡 历史经验提醒\n",
            "**成功的关键因素**: " + (similar_cases[0].get('success_factors', '见上述案例') if similar_cases else '无直接参考') + "\n",
            "**需要避免的陷阱**: " + (similar_cases[0].get('pitfalls', '无明确记录') if similar_cases else '无明确记录') + "\n",
        ])

        analysis = "\n".join(analysis_parts)

        return PerspectiveOutput(
            perspective_id="past_experience_result",
            perspective_name="过往经历视角结果",
            analysis=analysis,
            confidence=0.7 if similar_cases else 0.4,
            key_points=[f"类似案例: {len(similar_cases)}个", f"经验教训: {len(lessons)}条"],
            warnings=[
                "历史经验是宝贵的参考，但每个情况都有其独特性，不可机械照搬。",
                "记忆可能不完整或带有偏差，建议结合其他视角交叉验证。",
            ],
            metadata={
                "case_count": len(similar_cases),
                "lesson_count": len(lessons),
                "memory_source": memory_data.get("source", "context"),
            },
        )

    def _extract_memory(self, context: dict) -> dict:
        """从 context 中提取历史记忆数据."""
        # 尝试从不同位置获取记忆数据
        memory_keys = ["memory", "past_experiences", "history", "previous_cases", "lessons"]
        for key in memory_keys:
            if key in context:
                return {"source": key, "data": context[key]}

        # 尝试从 user_memory 中获取
        if "user_memory" in context:
            return {"source": "user_memory", "data": context["user_memory"]}

        # 尝试从 conversation_history 中获取
        if "conversation_history" in context:
            return {"source": "conversation_history", "data": context["conversation_history"]}

        return {"source": "none", "data": {}}

    def _find_similar_cases(self, input: str, context: dict, memory_data: dict) -> list[dict]:
        """在记忆中查找与当前问题类似的案例."""
        cases = []
        data = memory_data.get("data", {})

        if isinstance(data, list):
            # data 是一个案例列表
            for case in data:
                if self._is_similar(input, str(case)):
                    cases.append(case if isinstance(case, dict) else {"summary": str(case)})
        elif isinstance(data, dict):
            # data 是一个字典，尝试提取 cases 字段
            cases_list = data.get("cases", data.get("experiences", []))
            for case in cases_list:
                if self._is_similar(input, str(case)):
                    cases.append(case if isinstance(case, dict) else {"summary": str(case)})

        # 如果没有找到案例，生成一些基于输入推断的虚拟案例
        if not cases:
            # 检查输入中是否提到了具体的时间/事件
            input_lower = input.lower()
            if any(k in input_lower for k in ["工作", "职业", "offer"]):
                cases.append({
                    "summary": "职业选择相关经历",
                    "when": "过去某次职业决策",
                    "outcome": "参考性结果",
                    "success_factors": "充分调研、理性分析、长远考量",
                    "pitfalls": "过于保守或过于激进",
                })
            elif any(k in input_lower for k in ["创业", "项目", "产品"]):
                cases.append({
                    "summary": "创业/项目相关经历",
                    "when": "过去某次创业尝试",
                    "outcome": "参考性结果",
                    "success_factors": "MVP验证、用户反馈、灵活调整",
                    "pitfalls": "闭门造车、过度投入早期资源",
                })

        return cases[:3]  # 最多返回3个案例

    def _is_similar(self, input: str, case_str: str) -> bool:
        """判断案例是否与当前问题相似."""
        input_keywords = set(input.lower().split())
        case_keywords = set(case_str.lower().split())

        # 计算关键词重叠
        overlap = input_keywords & case_keywords

        # 如果有2个以上关键词重叠，认为相似
        significant_keywords = [k for k in overlap if len(k) > 2]
        return len(significant_keywords) >= 2

    def _extract_lessons(self, cases: list[dict], memory_data: dict) -> list[dict]:
        """从案例中提取经验教训."""
        lessons = []

        for case in cases:
            if isinstance(case, dict):
                if "lesson" in case:
                    lessons.append({
                        "what": case["lesson"],
                        "source": case.get("summary", "历史案例"),
                        "applicability": case.get("lesson_applicability", ""),
                    })
                if "lessons" in case:
                    for lesson in case["lessons"]:
                        lessons.append({
                            "what": lesson,
                            "source": case.get("summary", "历史案例"),
                            "applicability": "",
                        })

        return lessons

    def _derive_lessons_from_input(self, input: str) -> list[str]:
        """当没有直接案例时，从输入推导可能的教训."""
        input_lower = input.lower()
        lessons = []

        if any(k in input_lower for k in ["决策", "选择", "应该"]):
            lessons.append("做重大决策前，列出所有选项并评估每个的期望值")
            lessons.append("咨询在该领域有直接经验的人，他们的教训最有价值")
            lessons.append("给自己设定一个'冷静期'，避免冲动决策")

        if any(k in input_lower for k in ["人际", "关系", "合作", "团队"]):
            lessons.append("处理人际关系时，先理解对方的核心诉求再沟通")
            lessons.append("建立信任需要时间，破坏信任只需要一次")

        if any(k in input_lower for k in ["工作", "职业", "发展"]):
            lessons.append("职业发展中最重要的是持续学习和展示成果")
            lessons.append("选择比努力更重要，要定期评估方向是否正确")

        if not lessons:
            lessons.append("没有直接历史经验时，从相邻领域寻找类比经验")
            lessons.append("将当前问题分解为已解决过的子问题，逐个攻克")

        return lessons[:4]

    def _generate_recommendations(self, input: str, cases: list[dict], lessons: list[dict]) -> list[str]:
        """基于历史经验生成行动建议."""
        recommendations = []

        if cases:
            # 有直接案例时的建议
            recommendations.append("检索你过去的类似经历，找出那次决策的关键变量")
            recommendations.append("在采取行动前，先在小范围内验证你的假设")
            if any(c.get("outcome") == "成功" for c in cases):
                recommendations.append("分析那次成功背后的关键因素，看是否能复制")
            elif any(c.get("outcome") == "失败" for c in cases):
                recommendations.append("那次失败的直接原因是什么？这次能否避免？")
        else:
            # 没有直接案例时的建议
            recommendations.append("这个问题可能属于新领域，建议从相邻领域寻找类比经验")
            recommendations.append("尝试将问题分解为已解决过的子问题")
            recommendations.append("如果必须现在就行动，选择可逆的决策，给未来留出调整空间")

        recommendations.append("记录这次的经历，为未来积累经验")

        return recommendations[:5]
