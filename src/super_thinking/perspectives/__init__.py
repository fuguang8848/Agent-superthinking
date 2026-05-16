"""Perspectives package - thinking perspectives for super_thinking."""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput
from super_thinking.perspectives.mao_perspective import MaoPerspective
from super_thinking.perspectives.magi_debate import MagiDebatePerspective
from super_thinking.perspectives.meta_thinking import MetaThinkingPerspective
from super_thinking.perspectives.verification import VerificationPerspective
from super_thinking.perspectives.tagmemo_perspective import TagmemoPerspective
from super_thinking.perspectives.msa_perspective import MsaPerspective
from super_thinking.perspectives.vcp_perspective import VcpPerspective

ALL_PERSPECTIVES = [
    MaoPerspective,
    MagiDebatePerspective,
    MetaThinkingPerspective,
    VerificationPerspective,
    TagmemoPerspective,
    MsaPerspective,
    VcpPerspective,
]

__all__ = [
    "Perspective",
    "PerspectiveOutput",
    "MaoPerspective",
    "MagiDebatePerspective",
    "MetaThinkingPerspective",
    "VerificationPerspective",
    "TagmemoPerspective",
    "MsaPerspective",
    "VcpPerspective",
    "ALL_PERSPECTIVES",
]
