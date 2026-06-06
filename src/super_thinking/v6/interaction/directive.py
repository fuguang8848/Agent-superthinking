"""
interaction/directive.py - 用户指令解析

§2.3 主持人双重角色：从用户文本中解析主持人指令。
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = ["ModeratorDirective", "parse_user_directive"]


@dataclass(frozen=True, kw_only=True)
class ModeratorDirective:
    """
    从用户文本中解析出的主持人指令。

    Attributes:
        action: 动作类型
            - continue: 继续辩论
            - converge: 结束辩论，进入最终结论
            - ask_user: 询问用户
            - add_expert: 邀请专家加入
            - remove_expert: 请离专家
        target: 目标（专家ID或论点ID），可为 None
        reason: 解析原因说明
        confidence: 解析置信度 0.0-1.0
    """

    action: str # continue / converge / ask_user / add_expert / remove_expert
    target: str | None = None
    reason: str = ""
    confidence: float = 1.0


# 正则模式
_PATTERNS = [
    # 继续/结束
    (r"继续辩论", "continue", None,1.0),
    (r"^converge$|^结束辩论$", "converge", None, 1.0),
    # 询问用户
    (r"问用户|询问用户|ask[_ ]?user", "ask_user", None, 1.0),
    # 邀请专家
    (r"邀请(.+?)(?:加入|参与)", "add_expert", None, 0.9),
    (r"请(.+?)(?:加入|参与)", "add_expert", None, 0.9),
    # 请离专家
    (r"请离(.+?)(?:离开|退出)", "remove_expert", None, 0.9),
    (r"移除(.+?)(?:离开|退出)", "remove_expert", None, 0.9),
    (r"让(.+?)离?开", "remove_expert", None, 0.8),
]


def parse_user_directive(text: str) -> ModeratorDirective | None:
    """
    从用户文本中解析主持人指令。

    支持的指令模式：
    * 继续辩论 / continue -> action=continue
    * 结束辩论 / converge -> action=converge
    * 问用户 / ask user -> action=ask_user
    * 邀请[专家名]加入 -> action=add_expert, target=专家名
    * 请离[专家名] -> action=remove_expert, target=专家名

    Args:
        text: 用户输入文本

    Returns:
        ModeratorDirective 或 None（无法解析时）
    """
    if not text or not text.strip():
        return None

    text = text.strip()

    for pattern, action, _, base_confidence in _PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            target: str | None = None
            if m.lastindex and m.lastindex >= 1:
                target = m.group(1).strip()

            reason = f"匹配模式 '{pattern}' -> {action}"
            if target:
                reason += f", target='{target}'"

            return ModeratorDirective(
                action=action,
                target=target,
                reason=reason,
                confidence=base_confidence,
            )

    # 无法解析
    return None