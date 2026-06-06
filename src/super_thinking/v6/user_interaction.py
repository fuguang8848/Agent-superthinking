"""
user_interaction.py - 用户交互模块

实现用户交互协议，支持同步/异步两种模式。
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from .types import (
    ModeratorDirective,
    QuestionId,
    UserInteraction,
    UserQuestion,
    UserResponse,
)

logger = logging.getLogger(__name__)


class AsyncUserInteraction:
    """
    异步用户交互（适用于 CLI/REPL 场景）。
    
    使用 input() 进行同步等待，实际为异步模拟。
    """

    def __init__(self, prompt_prefix: str = "> ") -> None:
        self._prompt_prefix = prompt_prefix
        self._history: list[tuple[UserQuestion, UserResponse | None]] = []
        self._directives: list[ModeratorDirective] = []

    def ask(self, question: UserQuestion) -> UserResponse:
        """
        向用户提问并等待回答。
        
        Args:
            question: 问题对象
            
        Returns:
            用户响应
        """
        # 打印问题
        print()
        print(f"【系统】{question.text}")
        
        if question.options:
            print("选项:")
            for i, opt in enumerate(question.options, 1):
                print(f"  {i}. {opt}")
        
        # 等待用户输入
        try:
            user_input = input(self._prompt_prefix)
        except (EOFError, KeyboardInterrupt):
            user_input = ""

        # 记录
        response = self._parse_response(question, user_input)
        self._history.append((question, response))
        
        return response

    def _parse_response(
        self, question: UserQuestion, user_input: str
    ) -> UserResponse:
        """解析用户响应"""
        # 如果是选择题，尝试解析选项编号
        answer = user_input.strip()
        new_info = []
        
        if question.options:
            # 检查是否是数字选项
            try:
                idx = int(answer) - 1
                if 0 <= idx < len(question.options):
                    answer = question.options[idx]
            except ValueError:
                pass
        
        # 简单的新信息检测
        if len(user_input) > 50:
            new_info = [user_input.strip()]
        
        return UserResponse(
            question_id=question.question_id,
            answer=answer,
            new_information=tuple(new_info),
            answered_at=time.time(),
        )

    def on_user_input(self, text: str) -> ModeratorDirective:
        """
        处理用户的自由输入。
        
        将其解析为主持人指令。
        """
        text = text.strip().lower()
        
        # 简单指令解析
        if text in ["继续", "c", "continue", "go"]:
            return ModeratorDirective(action="continue")
        elif text in ["退出", "q", "quit", "exit"]:
            return ModeratorDirective(action="abort")
        elif text.startswith("加专家") or text.startswith("add "):
            return ModeratorDirective(
                action="add_expert",
                payload={"raw": text},
            )
        elif text.startswith("删专家") or text.startswith("remove "):
            return ModeratorDirective(
                action="remove_expert",
                payload={"raw": text},
            )
        else:
            return ModeratorDirective(action="no_op", payload={"raw": text})

    def get_history(self) -> list[tuple[UserQuestion, UserResponse | None]]:
        """获取交互历史"""
        return list(self._history)


class SyncUserInteraction:
    """
    同步用户交互（适用于程序化调用场景）。
    
    通过回调函数或预配置的方式处理用户交互。
    """

    def __init__(
        self,
        ask_callback: Any = None,
        directive_callback: Any = None,
    ) -> None:
        self._ask_callback = ask_callback
        self._directive_callback = directive_callback
        self._history: list[tuple[UserQuestion, UserResponse | None]] = []
        self._pending_questions: list[UserQuestion] = []

    def ask(self, question: UserQuestion) -> UserResponse:
        """
        通过回调函数处理问题。
        
        如果没有设置回调，则返回默认响应。
        """
        self._pending_questions.append(question)
        
        if self._ask_callback:
            response = self._ask_callback(question)
        else:
            # 返回默认响应
            response = UserResponse(
                question_id=question.question_id,
                answer="(未设置回调，请通过 set_ask_callback 配置)",
                new_information=(),
                answered_at=time.time(),
            )
        
        self._history.append((question, response))
        self._pending_questions.pop()
        
        return response

    def on_user_input(self, text: str) -> ModeratorDirective:
        """
        通过回调函数处理用户输入。
        
        如果没有设置回调，则返回 no_op。
        """
        if self._directive_callback:
            return self._directive_callback(text)
        else:
            return ModeratorDirective(action="no_op", payload={"raw": text})

    def set_ask_callback(self, callback: Any) -> None:
        """设置问题回调"""
        self._ask_callback = callback

    def set_directive_callback(self, callback: Any) -> None:
        """设置指令回调"""
        self._directive_callback = callback

    def get_pending_question(self) -> UserQuestion | None:
        """获取当前待回答的问题"""
        return self._pending_questions[-1] if self._pending_questions else None


class MockUserInteraction:
    """
    Mock 用户交互（适用于测试场景）。
    
    提供预设的响应序列。
    """

    def __init__(self) -> None:
        self._responses: list[UserResponse] = []
        self._directives: list[ModeratorDirective] = []
        self._current_idx = 0
        self._history: list[tuple[UserQuestion, UserResponse | None]] = []

    def add_response(self, response: UserResponse) -> None:
        """添加预设响应"""
        self._responses.append(response)

    def add_responses(self, responses: list[UserResponse]) -> None:
        """批量添加预设响应"""
        self._responses.extend(responses)

    def add_directive(self, directive: ModeratorDirective) -> None:
        """添加预设指令"""
        self._directives.append(directive)

    def ask(self, question: UserQuestion) -> UserResponse:
        """获取下一个预设响应"""
        if self._current_idx < len(self._responses):
            response = self._responses[self._current_idx]
            # 确保 question_id 匹配
            response = UserResponse(
                question_id=question.question_id,
                answer=response.answer,
                new_information=response.new_information,
                answered_at=time.time(),
            )
            self._current_idx += 1
        else:
            # 没有更多预设响应，返回默认
            response = UserResponse(
                question_id=question.question_id,
                answer="",
                new_information=(),
                answered_at=time.time(),
            )
        
        self._history.append((question, response))
        return response

    def on_user_input(self, text: str) -> ModeratorDirective:
        """获取下一个预设指令"""
        if self._directives:
            return self._directives.pop(0)
        
        # 默认继续
        if text.strip():
            return ModeratorDirective(action="continue")
        return ModeratorDirective(action="no_op")

    def reset(self) -> None:
        """重置状态"""
        self._current_idx = 0

    def get_history(self) -> list[tuple[UserQuestion, UserResponse | None]]:
        """获取交互历史"""
        return list(self._history)


# =============================================================================
# 工厂函数
# =============================================================================

def create_user_interaction(
    mode: str = "sync",
    **kwargs: Any,
) -> UserInteraction:
    """
    创建用户交互实例。
    
    Args:
        mode: "async" | "sync" | "mock"
        **kwargs: 传递给对应实现的参数
    """
    if mode == "async":
        return AsyncUserInteraction(prompt_prefix=kwargs.get("prompt_prefix", "> "))
    elif mode == "mock":
        return MockUserInteraction()
    else:
        return SyncUserInteraction(
            ask_callback=kwargs.get("ask_callback"),
            directive_callback=kwargs.get("directive_callback"),
        )


# =============================================================================
# 辅助函数
# =========
