"""Risk Detail Perspective - 详细风险分解视角

比 magi_debate 更细的风险分析，量化概率和影响。
触发关键词: 风险、最坏、万一、失败、不确定、概率、影响、风险评估、黑天鹅
"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class RiskDetailPerspective(Perspective):
    """详细风险分解视角：量化概率和影响，提供风险矩阵和缓解策略."""

    @property
    def id(self) -> str:
        return "risk_detail_perspective"

    @property
    def name(self) -> str:
        return "详细风险分解视角"

    @property
    def description(self) -> str:
        return "量化风险概率和影响，输出风险矩阵+缓解策略。比mag_debate更细粒度的风险分析，涵盖黑天鹅事件考量。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "风险", "最坏", "万一", "失败", "不确定", "概率",
            "影响", "风险评估", "黑天鹅", "最坏情况", "最好情况",
            "不利", "隐患", "担忧", "顾虑", "怕", "万一失败",
            "不可控", "意外", "最坏打算",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """Execute detailed risk analysis."""
        risks = self._identify_risks(input)
        risk_matrix = self._build_risk_matrix(risks)
        black_swan = self._assess_black_swan(input)
        mitigation = self._generate_mitigation_strategies(risks)
        overall_assessment = self._overall_risk_assessment(risks, risk_matrix, black_swan)

        analysis_parts = [
            "## 🔬 详细风险分解分析\n",
            f"**被分析事项**: {input}\n",
            "---\n",
            "### 📊 风险矩阵\n",
            "| 风险项 | 概率 | 影响 | 风险值 | 等级 |\n",
            "| --- | --- | --- | --- | --- |\n",
        ]

        for risk in risks:
            level = self._risk_level(risk["score"])
            analysis_parts.append(
                f"| {risk['name']} | {risk['probability']}/5 | {risk['impact']}/5 | "
                f"{risk['score']} | {level} |"
            )

        analysis_parts.extend([
            "",
            "**风险矩阵可视化**（X=概率, Y=影响）:\n",
        ])

        # 生成文字版矩阵
        matrix_viz = self._generate_matrix_viz(risks)
        analysis_parts.append(matrix_viz)

        analysis_parts.extend([
            "",
            "### 🦢 黑天鹅事件评估\n",
            f"**是否可能**: {'⚠️ 可能' if black_swan['possible'] else '✓ 低可能'}\n",
            f"**评估**: {black_swan['assessment']}\n",
        ])

        if black_swan["possible"]:
            analysis_parts.append("**潜在黑天鹅场景**:\n")
            for scenario in black_swan.get("scenarios", []):
                analysis_parts.append(f"- {scenario}\n")

        analysis_parts.extend([
            "### 🛡️ 缓解策略\n",
        ])

        for strategy in mitigation:
            analysis_parts.append(f"**{strategy['risk']}**: {strategy['action']}")
            analysis_parts.append(f"   成本: {strategy['cost']} | 效果: {strategy['effectiveness']}\n")

        analysis_parts.extend([
            "---\n",
            "### 📈 整体风险评估\n",
            f"**总体风险等级**: {overall_assessment['level']}\n",
            f"**评估依据**: {overall_assessment['reasoning']}\n",
            f"**核心风险**: {overall_assessment['core_risk']}\n",
            "\n**建议行动**:\n",
        ])

        for rec in overall_assessment["recommendations"]:
            analysis_parts.append(f"- {rec}\n")

        analysis = "\n".join(analysis_parts)

        return PerspectiveOutput(
            perspective_id="risk_detail_result",
            perspective_name="详细风险分解结果",
            analysis=analysis,
            confidence=0.8,
            key_points=[
                f"识别到{len(risks)}个主要风险",
                f"最高风险: {risks[0]['name'] if risks else '无'} (风险值{risks[0]['score'] if risks else 0})",
                f"黑天鹅可能: {'是' if black_swan['possible'] else '否'}",
            ],
            warnings=[
                "风险评估基于当前信息和主观判断，实际概率可能与估计有偏差。",
                "黑天鹅事件本质上不可预测，本分析仅做可能性提示。",
            ],
            metadata={
                "risk_count": len(risks),
                "high_risk_count": len([r for r in risks if r["score"] >= 15]),
                "black_swan_possible": black_swan["possible"],
                "overall_score": overall_assessment.get("score", 0),
            },
        )

    def _identify_risks(self, input: str) -> list[dict]:
        """识别并量化风险."""
        risks = []
        input_lower = input.lower()

        # 基于问题类型推断风险
        if any(k in input_lower for k in ["工作", "offer", "职业", "跳槽"]):
            risks = [
                {"name": "薪资不达预期", "probability": 3, "impact": 4, "score": 12},
                {"name": "职位描述与实际不符", "probability": 3, "impact": 4, "score": 12},
                {"name": "团队氛围差/文化不匹配", "probability": 2, "impact": 5, "score": 10},
                {"name": "晋升空间有限", "probability": 3, "impact": 3, "score": 9},
                {"name": "被裁员/项目取消", "probability": 2, "impact": 4, "score": 8},
                {"name": "新工作不如现有工作稳定", "probability": 3, "impact": 3, "score": 9},
            ]

        elif any(k in input_lower for k in ["创业", "项目", "产品"]):
            risks = [
                {"name": "市场需求不达预期", "probability": 4, "impact": 5, "score": 20},
                {"name": "资金链断裂", "probability": 3, "impact": 5, "score": 15},
                {"name": "核心成员离职", "probability": 2, "impact": 4, "score": 8},
                {"name": "竞争对手超越", "probability": 3, "impact": 4, "score": 12},
                {"name": "技术路线选错", "probability": 2, "impact": 4, "score": 8},
                {"name": "监管政策变化", "probability": 2, "impact": 4, "score": 8},
            ]

        elif any(k in input_lower for k in ["投资", "理财", "钱"]):
            risks = [
                {"name": "本金损失", "probability": 3, "impact": 5, "score": 15},
                {"name": "流动性风险", "probability": 2, "impact": 4, "score": 8},
                {"name": "市场波动", "probability": 4, "impact": 3, "score": 12},
                {"name": "机会成本", "probability": 3, "impact": 3, "score": 9},
                {"name": "通胀侵蚀", "probability": 3, "impact": 3, "score": 9},
            ]

        elif any(k in input_lower for k in ["关系", "人际", "家庭", "感情"]):
            risks = [
                {"name": "沟通不畅导致误解", "probability": 3, "impact": 4, "score": 12},
                {"name": "期望不一致", "probability": 3, "impact": 4, "score": 12},
                {"name": "外部压力/干预", "probability": 2, "impact": 4, "score": 8},
                {"name": "关系恶化/破裂", "probability": 2, "impact": 5, "score": 10},
            ]

        else:
            # 默认风险类型
            risks = [
                {"name": "执行不达预期", "probability": 3, "impact": 4, "score": 12},
                {"name": "资源不足", "probability": 3, "impact": 4, "score": 12},
                {"name": "外部环境变化", "probability": 2, "impact": 4, "score": 8},
                {"name": "关键假设错误", "probability": 2, "impact": 5, "score": 10},
                {"name": "时间延误", "probability": 3, "impact": 3, "score": 9},
            ]

        # 按风险值排序
        risks.sort(key=lambda x: x["score"], reverse=True)
        return risks[:8]

    def _build_risk_matrix(self, risks: list[dict]) -> dict:
        """构建风险矩阵."""
        matrix = {"high_high": [], "high_low": [], "low_high": [], "low_low": []}

        for risk in risks:
            if risk["probability"] >= 3 and risk["impact"] >= 4:
                matrix["high_high"].append(risk["name"])
            elif risk["probability"] >= 3 and risk["impact"] < 4:
                matrix["high_low"].append(risk["name"])
            elif risk["probability"] < 3 and risk["impact"] >= 4:
                matrix["low_high"].append(risk["name"])
            else:
                matrix["low_low"].append(risk["name"])

        return matrix

    def _risk_level(self, score: int) -> str:
        """根据风险值判断等级."""
        if score >= 16:
            return "🔴 极高"
        elif score >= 12:
            return "🟠 高"
        elif score >= 8:
            return "🟡 中"
        else:
            return "🟢 低"

    def _generate_matrix_viz(self, risks: list[dict]) -> str:
        """生成文字版风险矩阵可视化."""
        lines = [
            "         影响",
            "         高 | 低",
            "概率 高 | ■■ | □□ ",
            "     低 | □□ | ○○ ",
            "",
            "■■ = 高风险区 (需重点关注)  □□ = 中风险区  ○○ = 低风险区",
        ]
        return "\n".join(lines)

    def _assess_black_swan(self, input: str) -> dict:
        """评估黑天鹅事件可能性."""
        input_lower = input.lower()
        result = {"possible": False, "assessment": "", "scenarios": []}

        # 黑天鹅触发词
        black_swan_triggers = [
            "第一次", "从未", "全新", "开创", "史上首次",
            "没有任何先例", "前所未有的",
        ]

        if any(k in input_lower for k in black_swan_triggers):
            result["possible"] = True
            result["assessment"] = "该事项具有开创性或前所未有性，存在黑天鹅事件的可能性"
            result["scenarios"] = [
                "假设A: 出现了完全意料之外的技术突破",
                "假设B: 监管环境发生重大变化",
                "假设C: 市场需求出现根本性转变",
            ]
            return result

        # 高度不确定的领域
        uncertain_domains = ["创业", "投资", "未知领域", "新产品"]
        if any(k in input_lower for k in uncertain_domains):
            result["possible"] = True
            result["assessment"] = "该领域存在高度不确定性，黑天鹅事件概率相对较高"
            result["scenarios"] = [
                "假设A: 核心技术被颠覆",
                "假设B: 关键假设被证伪",
                "假设C: 外部宏观环境突变",
            ]
            return result

        # 相对成熟的领域
        result["possible"] = False
        result["assessment"] = "该领域相对成熟，黑天鹅事件概率较低，但仍存在尾部风险"
        return result

    def _generate_mitigation_strategies(self, risks: list[dict]) -> list[dict]:
        """为每个主要风险生成缓解策略."""
        strategies = []

        mitigation_templates = {
            "本金损失": {
                "action": "分散投资，设置止损线，不要All-in单一标的",
                "cost": "中等（分散收益）",
                "effectiveness": "高",
            },
            "市场需求不达预期": {
                "action": "先做MVP验证，持续获取用户反馈，敏捷迭代",
                "cost": "低",
                "effectiveness": "高",
            },
            "资金链断裂": {
                "action": "保持充足的现金储备，制定清晰的烧钱计划，多元化融资渠道",
                "cost": "中等",
                "effectiveness": "高",
            },
            "团队氛围差": {
                "action": "入职前多了解团队文化，与潜在同事交流，设置试用期观察",
                "cost": "低",
                "effectiveness": "中",
            },
            "被裁员": {
                "action": "持续积累可迁移技能，建立行业人脉，准备应急资金",
                "cost": "低",
                "effectiveness": "中",
            },
            "执行不达预期": {
                "action": "设置阶段性里程碑，定期复盘，及早发现问题",
                "cost": "低",
                "effectiveness": "高",
            },
            "外部环境变化": {
                "action": "保持对宏观环境的敏感度，建立应急预案，保持灵活性",
                "cost": "低",
                "effectiveness": "中",
            },
        }

        for risk in risks[:5]:
            if risk["name"] in mitigation_templates:
                template = mitigation_templates[risk["name"]]
                strategies.append({
                    "risk": risk["name"],
                    **template,
                })
            else:
                strategies.append({
                    "risk": risk["name"],
                    "action": f"针对{risk['name']}制定专项应对方案",
                    "cost": "待评估",
                    "effectiveness": "待评估",
                })

        return strategies

    def _overall_risk_assessment(self, risks: list[dict], matrix: dict, black_swan: dict) -> dict:
        """给出整体风险评估."""
        if not risks:
            return {
                "level": "🟢 低",
                "score": 0,
                "reasoning": "未识别到明显风险",
                "core_risk": "无",
                "recommendations": ["保持正常监控即可"],
            }

        # 计算整体风险分
        total_score = sum(r["score"] for r in risks) / len(risks)

        # 确定核心风险
        core_risk = risks[0]["name"] if risks else "无"

        # 确定等级
        if total_score >= 15 or black_swan["possible"]:
            level = "🔴 极高风险"
        elif total_score >= 12:
            level = "🟠 高风险"
        elif total_score >= 8:
            level = "🟡 中等风险"
        else:
            level = "🟢 低风险"

        reasoning = (
            f"基于{len(risks)}个风险因素的平均风险值{total_score:.1f}，"
            f"其中{core_risk}为最突出风险。"
            f"{'且存在黑天鹅事件可能，需特别关注。' if black_swan['possible'] else ''}"
        )

        recommendations = []
        if total_score >= 12:
            recommendations.append("建议推迟决策，充分收集更多信息后再评估")
            recommendations.append("制定详细的风险应对计划，明确触发条件和响应机制")
        elif total_score >= 8:
            recommendations.append("识别并重点监控最高风险因素")
            recommendations.append("准备风险缓解措施，但可以继续推进")
        else:
            recommendations.append("风险整体可控，保持常规监控即可")

        recommendations.append("定期重新评估风险矩阵，及时更新判断")

        return {
            "level": level,
            "score": total_score,
            "reasoning": reasoning,
            "core_risk": core_risk,
            "recommendations": recommendations,
        }
