"""Stakeholder Perspective - 利益相关者视角

分析问题中各方的立场、诉求、关系。
触发关键词: 各方、立场、利益、诉求、关系、谁想要、谁的损失、谁受益
"""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput


class StakeholderPerspective(Perspective):
    """利益相关者视角：分析各方立场、诉求、关系和潜在冲突."""

    @property
    def id(self) -> str:
        return "stakeholder_perspective"

    @property
    def name(self) -> str:
        return "利益相关者视角"

    @property
    def description(self) -> str:
        return "从利益相关者角度分析问题：识别各方立场、核心诉求、相互关系，揭示隐性冲突和潜在联盟机会。"

    @property
    def trigger_keywords(self) -> list[str]:
        return [
            "各方", "立场", "利益", "诉求", "关系",
            "谁想要", "谁的损失", "谁受益", "对手", "竞争",
            "合作", "冲突", "矛盾", "博弈", "分配",
            "牵扯到谁", "涉及哪些人", "多方", "不同意见",
        ]

    def think(self, input: str, context: dict) -> PerspectiveOutput:
        """Execute stakeholder analysis."""
        stakeholders = self._identify_stakeholders(input)
        positions = self._analyze_positions(stakeholders, input)
        relationships = self._analyze_relationships(stakeholders, positions)
        conflicts = self._identify_conflicts(stakeholders, positions)
        alliance_opportunities = self._find_alliance_opportunities(stakeholders, positions)
        recommendations = self._generate_recommendations(stakeholders, conflicts, alliance_opportunities)

        analysis_parts = [
            "## 🤝 利益相关者分析\n",
            f"**问题**: {input}\n",
            "---\n",
            "### 👥 利益相关者识别\n",
        ]

        for i, sh in enumerate(stakeholders, 1):
            analysis_parts.append(f"**{i}. {sh['name']}**")
            analysis_parts.append(f"   角色: {sh['role']}")
            analysis_parts.append(f"   核心诉求: {sh['interest']}")
            analysis_parts.append(f"   影响力度: {sh['influence']}/5 | 关注度: {sh['interest_level']}/5")
            analysis_parts.append("")

        analysis_parts.extend([
            "### 🎯 各方立场分析\n",
        ])

        for pos in positions:
            analysis_parts.append(f"**{pos['who']}**: {pos['position']}")
            analysis_parts.append(f"   底线: {pos['bottom_line']}")
            analysis_parts.append(f"   弹性空间: {pos['flexibility']}\n")

        analysis_parts.extend([
            "### 🔗 关系网络\n",
        ])

        for rel in relationships:
            direction = "→" if not rel.get("reverse") else "←"
            analysis_parts.append(f"{rel['from']} {direction} {rel['to']}: {rel['type']}")
            if rel.get("description"):
                analysis_parts.append(f"   {rel['description']}")

        analysis_parts.extend([
            "",
            "### ⚔️ 核心冲突\n",
        ])

        if conflicts:
            for i, conflict in enumerate(conflicts, 1):
                analysis_parts.append(f"**冲突{i}: {conflict['between']}**")
                analysis_parts.append(f"   焦点: {conflict['issue']}")
                analysis_parts.append(f"   紧张度: {conflict['intensity']}/5")
                analysis_parts.append(f"   可能的解决方案: {conflict['resolution']}\n")
        else:
            analysis_parts.append("暂未识别到显性的核心冲突。\n")

        analysis_parts.extend([
            "### 🤝 联盟机会\n",
        ])

        if alliance_opportunities:
            for opp in alliance_opportunities:
                analysis_parts.append(f"- **{opp['who']}** + **{opp['with']}**: {opp['common_interest']}")
                analysis_parts.append(f"  联盟基础: {opp['basis']}\n")
        else:
            analysis_parts.append("暂无明显的联盟机会。\n")

        analysis_parts.extend([
            "---\n",
            "### ✅ 策略建议\n",
        ])

        for i, rec in enumerate(recommendations, 1):
            analysis_parts.append(f"{i}. {rec}\n")

        analysis = "\n".join(analysis_parts)

        return PerspectiveOutput(
            perspective_id="stakeholder_result",
            perspective_name="利益相关者分析结果",
            analysis=analysis,
            confidence=0.78,
            key_points=[f"识别到{len(stakeholders)}个利益相关方", f"核心冲突{len(conflicts)}个"],
            warnings=[
                "利益相关者分析需要充分的信息支撑，信息不完整时分析可能存在偏差。",
                "各方的实际立场可能与表面表述不一致，需要关注言行差异。",
            ],
            metadata={
                "stakeholder_count": len(stakeholders),
                "conflict_count": len(conflicts),
                "alliance_count": len(alliance_opportunities),
            },
        )

    def _identify_stakeholders(self, input: str) -> list[dict]:
        """识别问题中的利益相关者."""
        stakeholders = []
        input_lower = input.lower()

        # 基于关键词识别可能的利益相关者
        if any(k in input_lower for k in ["工作", "职业", "offer", "跳槽", "公司"]):
            stakeholders.extend([
                {"name": "自己", "role": "决策者/执行者", "interest": "职业发展、薪资、成长", "influence": 5, "interest_level": 5},
                {"name": "现有雇主", "role": "当前组织", "interest": "保留人才、业务连续性", "influence": 3, "interest_level": 4},
                {"name": "潜在雇主", "role": "目标组织", "interest": "获取人才、岗位匹配度", "influence": 3, "interest_level": 5},
                {"name": "家人/伴侣", "role": "支持系统", "interest": "生活稳定、情感满足", "influence": 2, "interest_level": 4},
            ])

        if any(k in input_lower for k in ["创业", "项目", "产品", "商业"]):
            stakeholders.extend([
                {"name": "创始人/团队", "role": "核心决策者", "interest": "项目成功、个人成长", "influence": 5, "interest_level": 5},
                {"name": "投资人", "role": "资金提供方", "interest": "资本回报", "influence": 4, "interest_level": 4},
                {"name": "用户/客户", "role": "产品使用者", "interest": "问题解决、价值获取", "influence": 5, "interest_level": 5},
                {"name": "竞争对手", "role": "市场参与者", "interest": "市场份额、差异化", "influence": 3, "interest_level": 3},
            ])

        if any(k in input_lower for k in ["产品", "功能", "设计", "开发"]):
            stakeholders.extend([
                {"name": "产品经理", "role": "产品负责人", "interest": "产品成功、需求实现", "influence": 4, "interest_level": 5},
                {"name": "开发团队", "role": "实现者", "interest": "技术可行性、工作量合理", "influence": 3, "interest_level": 4},
                {"name": "终端用户", "role": "使用者", "interest": "易用性、价值", "influence": 5, "interest_level": 5},
                {"name": "运营/市场", "role": "推广方", "interest": "推广可行性、市场接受度", "influence": 3, "interest_level": 3},
            ])

        if any(k in input_lower for k in ["家庭", "亲子", "父母", "孩子"]):
            stakeholders.extend([
                {"name": "自己", "role": "核心决策者", "interest": "自我实现、家庭平衡", "influence": 5, "interest_level": 5},
                {"name": "配偶/伴侣", "role": "家庭成员", "interest": "家庭利益、生活质量", "influence": 4, "interest_level": 5},
                {"name": "父母", "role": "上一代", "interest": "代际理解、传统vs现代", "influence": 3, "interest_level": 4},
                {"name": "孩子", "role": "下一代", "interest": "成长环境、教育资源", "influence": 3, "interest_level": 4},
            ])

        # 默认利益相关者（如果没匹配到特定领域）
        if not stakeholders:
            stakeholders = [
                {"name": "自己", "role": "核心决策者", "interest": "利益最大化", "influence": 5, "interest_level": 5},
                {"name": "直接相关方A", "role": "主要参与者", "interest": "待分析", "influence": 4, "interest_level": 4},
                {"name": "直接相关方B", "role": "次要参与者", "interest": "待分析", "influence": 3, "interest_level": 3},
                {"name": "间接受影响方", "role": "外围影响者", "interest": "待分析", "influence": 2, "interest_level": 2},
            ]

        return stakeholders[:6]  # 最多6个核心利益相关者

    def _analyze_positions(self, stakeholders: list[dict], input: str) -> list[dict]:
        """分析各方的立场和底线."""
        positions = []

        for sh in stakeholders:
            position = {
                "who": sh["name"],
                "position": f"关注自身利益: {sh['interest']}",
                "bottom_line": "基本诉求必须满足",
                "flexibility": "在次要问题上可能有商量余地",
            }

            if sh["name"] == "自己":
                position["position"] = "寻求最优决策，平衡短期和长期利益"
                position["bottom_line"] = "核心利益不能受损"
                position["flexibility"] = "在方式方法上可以灵活"
            elif sh.get("influence", 0) >= 4:
                position["position"] = f"作为高影响力方，寻求主导解决方案"
                position["bottom_line"] = "必须保障自身核心利益"
                position["flexibility"] = "可能愿意为达成共识做出调整"

            positions.append(position)

        return positions

    def _analyze_relationships(self, stakeholders: list[dict], positions: list[dict]) -> list[dict]:
        """分析利益相关者之间的关系."""
        relationships = []

        # 基于角色自动推断关系
        names = [sh["name"] for sh in stakeholders]

        for i, sh in enumerate(stakeholders):
            for j, other in enumerate(stakeholders):
                if i >= j:
                    continue

                rel = None

                # 合作类关系
                if any(k in sh.get("role", "").lower() for k in ["团队", "同事", "合作"]):
                    if any(k in other.get("role", "").lower() for k in ["团队", "同事", "合作"]):
                        rel = {"from": sh["name"], "to": other["name"], "type": "协作", "description": "同一团队的伙伴，目标一致"}

                # 对立类关系
                if any(k in sh.get("role", "").lower() for k in ["竞争", "对手"]):
                    if any(k in other.get("role", "").lower() for k in ["竞争", "对手"]):
                        rel = {"from": sh["name"], "to": other["name"], "type": "竞争", "description": "存在直接竞争关系"}

                # 支持类关系
                if sh.get("influence", 0) >= 4 and other.get("influence", 0) <= 2:
                    rel = {"from": sh["name"], "to": other["name"], "type": "影响", "description": "影响力高者对低者有显著影响"}

                if rel:
                    relationships.append(rel)

        # 如果没有推断出关系，添加一些默认描述
        if not relationships:
            if len(stakeholders) >= 2:
                relationships.append({
                    "from": stakeholders[0]["name"],
                    "to": stakeholders[1]["name"],
                    "type": "待明确",
                    "description": "需要根据具体情况判断关系类型",
                })

        return relationships[:8]

    def _identify_conflicts(self, stakeholders: list[dict], positions: list[dict]) -> list[dict]:
        """识别核心利益冲突."""
        conflicts = []
        input_lower = ""

        # 基于利益差异推断冲突
        interests = [sh.get("interest", "") for sh in stakeholders]

        # 检测是否有利益对立
        if any("时间" in i for i in interests) and any("速度" in i for i in interests):
            conflicts.append({
                "between": "效率派 vs 质量派",
                "issue": "在时间压力下，是追求速度还是保证质量",
                "intensity": 4,
                "resolution": "设定明确的优先级，在关键环节保证质量，其他环节追求效率",
            })

        if any("个人" in i for i in interests) and any("团队" in i for i in interests):
            conflicts.append({
                "between": "个人利益 vs 团队利益",
                "issue": "个人目标与团队目标可能不一致",
                "intensity": 3,
                "resolution": "寻找个人与团队利益的结合点，建立共赢机制",
            })

        if any("短期" in i for i in interests) and any("长期" in i for i in interests):
            conflicts.append({
                "between": "短期导向 vs 长期导向",
                "issue": "短期成果和长期发展之间的取舍",
                "intensity": 4,
                "resolution": "分阶段规划，短期成果支撑长期目标，避免只看眼前",
            })

        # 如果没有识别到特定冲突
        if not conflicts:
            conflicts.append({
                "between": stakeholders[0]["name"] + " vs " + stakeholders[1]["name"],
                "issue": "资源有限情况下的利益分配",
                "intensity": 3,
                "resolution": "通过谈判和妥协寻找各方都能接受的方案",
            })

        return conflicts[:3]

    def _find_alliance_opportunities(self, stakeholders: list[dict], positions: list[dict]) -> list[dict]:
        """寻找可能的联盟机会."""
        opportunities = []

        # 寻找利益一致的对
        for i, sh in enumerate(stakeholders):
            for j, other in enumerate(stakeholders):
                if i >= j:
                    continue

                # 简单判断：如果影响力相近，可能是潜在盟友
                if abs(sh.get("influence", 3) - other.get("influence", 3)) <= 1:
                    if any(k in sh.get("interest", "") for k in ["合作", "共赢", "共同"]):
                        opportunities.append({
                            "who": sh["name"],
                            "with": other["name"],
                            "common_interest": "共同推动某项议程",
                            "basis": "影响力相近，利益诉求有重叠",
                        })

        # 如果没有找到机会
        if not opportunities and len(stakeholders) >= 2:
            opportunities.append({
                "who": stakeholders[0]["name"],
                "with": stakeholders[1]["name"],
                "common_interest": "解决问题/达成目标",
                "basis": "有共同的目标基础，可能通过沟通建立信任",
            })

        return opportunities[:2]

    def _generate_recommendations(self, stakeholders: list[dict], conflicts: list[dict], alliances: list[dict]) -> list[str]:
        """生成策略建议."""
        recommendations = []

        recommendations.append("首先明确各方真正的核心利益（有时表面诉求和深层利益不一致）")
        recommendations.append("在冲突点之外寻找共同利益，建立对话基础")

        if alliances:
            recommendations.append(f"优先联合{alliances[0]['who']}和{alliances[0]['with']}，建立核心同盟")

        if conflicts:
            recommendations.append(f"针对核心冲突（{conflicts[0]['issue']}），设定优先级和谈判框架")

        recommendations.append("关注各方的'底线'，在底线之上寻找妥协空间")
        recommendations.append("定期评估各方立场的动态变化，及时调整策略")

        return recommendations[:6]
