"""
external_consultation.py - 外部咨询模块

实现同步阻塞的外部咨询功能，包含超时控制和失败降级。
每轮最多 2 次咨询，单次 30s 超时。
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from dataclasses import dataclass, field
from typing import Any, Callable

from .types import (
    ExpertId,
    ExpertStatement,
    ExternalConsultation,
    ExternalConsultationRequest,
    ModeratorDirective,
    SpeakPrompt,
    SpeakRole,
    SessionId,
    RoundNumber,
)

logger = logging.getLogger(__name__)


@dataclass
class ConsultationRecord:
    """咨询记录"""
    expert_id: ExpertId
    expert_name: str
    question: str
    requested_at: float
    response: str | None
    received_at: float | None
    timed_out: bool
    error: str | None = None
    elapsed_s: float = 0.0


class ExternalConsultationManager:
    """
    外部咨询管理器。
    
    特性：
    - 同步阻塞调用（使用 ThreadPoolExecutor 实现超时）
    - 每轮最多 2 次咨询
    - 单次 30s 超时
    - 失败自动降级（返回 None）
    - 完整咨询历史记录
    """

    def __init__(
        self,
        expert_pool: Any,  # ExpertPool
        max_per_round: int = 2,
        default_timeout_s: float = 30.0,
    ) -> None:
        self._expert_pool = expert_pool
        self._max_per_round = max_per_round
        self._default_timeout_s = default_timeout_s
        self._history: list[ConsultationRecord] = []
        self._round_count = 0

    def consult(
        self,
        expert_id: ExpertId,
        question: str,
        *,
        context: str = "",
        timeout_s: float | None = None,
        max_chars: int = 1500,
    ) -> ExternalConsultation:
        """
        执行外部咨询。
        
        Args:
            expert_id: 专家 ID
            question: 咨询问题
            context: 上下文摘要
            timeout_s: 超时秒数（默认 30.0）
            max_chars: 最大响应字符数
            
        Returns:
            ExternalConsultation 对象，包含请求和响应
        """
        timeout = timeout_s or self._default_timeout_s
        
        request = ExternalConsultationRequest(
            expert_id=expert_id,
            question=question,
            relevant_arguments=(),
            context_summary=context,
            max_response_chars=max_chars,
            deadline_s=timeout,
        )

        record = ConsultationRecord(
            expert_id=expert_id,
            expert_name="",
            question=question,
            requested_at=time.time(),
            response=None,
            received_at=None,
            timed_out=False,
            error=None,
        )

        # 获取专家名称
        expert = self._expert_pool.get(expert_id) if self._expert_pool else None
        if expert:
            record.expert_name = expert.name

        try:
            # 使用 ThreadPoolExecutor 实现超时
            response_text = self._do_consult_with_timeout(
                expert_id, question, timeout, max_chars
            )
            
            if response_text is None:
                # 超时
                record.timed_out = True
                record.error = "Consultation timed out"
                logger.warning(f"Consultation with {expert_id} timed out after {timeout}s")
            else:
                record.response = response_text
                record.received_at = time.time()
                record.elapsed_s = record.received_at - record.requested_at
                logger.info(
                    f"Consultation with {expert_id} completed in {record.elapsed_s:.2f}s"
                )

        except Exception as e:
            record.error = str(e)
            logger.error(f"Consultation with {expert_id} failed: {e}")

        self._history.append(record)

        return ExternalConsultation(
            request=request,
            response_text=record.response or "",
            received_at=record.received_at or 0.0,
            timed_out=record.timed_out,
        )

    def _do_consult_with_timeout(
        self,
        expert_id: ExpertId,
        question: str,
        timeout_s: float,
        max_chars: int,
    ) -> str | None:
        """使用线程池执行带超时的咨询"""

        def _sync_consult() -> str:
            if self._expert_pool is None:
                return "Expert pool not available"
            
            return self._expert_pool.consult(
                expert_id,
                question,
                timeout_s=timeout_s,
                max_chars=max_chars,
            ) or ""

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_sync_consult)
                return future.result(timeout=timeout_s)
        except FuturesTimeoutError:
            logger.warning(f"Consultation timed out after {timeout_s}s")
            return None
        except Exception as e:
            logger.error(f"Consultation error: {e}")
            raise

    def can_consult_this_round(self) -> bool:
        """检查本轮是否还可以咨询"""
        return len(self._get_current_round_consults()) < self._max_per_round

    def remaining_consults(self) -> int:
        """返回本轮剩余咨询次数"""
        return max(0, self._max_per_round - len(self._get_current_round_consults()))

    def _get_current_round_consults(self) -> list[ConsultationRecord]:
        """获取当前轮次的咨询记录"""
        # 简单实现：取最后 _max_per_round 条记录
        return self._history[-self._max_per_round:] if self._history else []

    def new_round(self) -> None:
        """开始新的一轮"""
        self._round_count += 1
        logger.debug(f"Starting round {self._round_count}")

    def get_history(self) -> list[ConsultationRecord]:
        """获取咨询历史"""
        return list(self._history)

    def get_history_for_session(self, session_id: str) -> list[dict[str, Any]]:
        """获取指定会话的咨询历史"""
        return [
            {
                "expert_id": r.expert_id,
                "expert_name": r.expert_name,
                "question": r.question,
                "requested_at": r.requested_at,
                "response_length": len(r.response) if r.response else 0,
                "timed_out": r.timed_out,
                "elapsed_s": r.elapsed_s,
            }
            for r in self._history
        ]

    def stats(self) -> dict[str, Any]:
        """获取统计信息"""
        total = len(self._history)
        timed_out = sum(1 for r in self._history if r.timed_out)
        failed = sum(1 for r in self._history if r.error is not None and not r.timed_out)
        success = total - timed_out - failed
        avg_elapsed = (
            sum(r.elapsed_s for r in self._history if r.elapsed_s > 0) / max(success, 1)
        )

        return {
            "total_consultations": total,
            "successful": success,
            "timed_out": timed_out,
            "failed": failed,
            "average_elapsed_s": avg_elapsed,
            "rounds": self._round_count,
        }


class MockExpertPool:
    """
    用于测试的 Mock 专家池。
    
    提供简单的响应模拟。
    """

    def __init__(self) -> None:
        self._experts: dict[ExpertId, Any] = {}

    def add_mock_expert(self, expert_id: str, response: str) -> None:
        """添加模拟专家"""
        self._experts[ExpertId(expert_id)] = MockExpert(expert_id, response)

    def get(self, expert_id: ExpertId) -> Any | None:
        """获取专家"""
        return self._experts.get(expert_id)

    def register(self, expert: Any) -> None:
        """注册专家"""
        self._experts[expert.id] = expert


class MockExpert:
    """模拟专家"""

    def __init__(self, expert_id: str, response: str) -> None:
        self.id = ExpertId(expert_id)
        self.name = f"Mock Expert {expert_id}"
        self.response = response

    def speak(self, prompt: SpeakPrompt) -> ExpertStatement:
        """模拟发言"""
        return ExpertStatement(
            expert_id=self.id,
            expert_name=self.name,
            role=prompt.role,
            content=self.response,
            confidence=0.8,
        )


# =============================================================================
# 工厂函数
# =============================================================================
