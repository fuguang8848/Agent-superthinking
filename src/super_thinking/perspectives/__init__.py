"""Perspectives package - thinking perspectives for super_thinking."""

from super_thinking.perspectives._interface import Perspective, PerspectiveOutput
from super_thinking.perspectives.mao_perspective import MaoPerspective
from super_thinking.perspectives.magi_debate import MagiDebatePerspective
from super_thinking.perspectives.meta_thinking import MetaThinkingPerspective
from super_thinking.perspectives.verification import VerificationPerspective
from super_thinking.perspectives.tagmemo_perspective import TagmemoPerspective
from super_thinking.perspectives.msa_perspective import MsaPerspective
from super_thinking.perspectives.vcp_perspective import VcpPerspective
from super_thinking.perspectives.elon_perspective import ElonPerspective
from super_thinking.perspectives.jobs_perspective import JobsPerspective
from super_thinking.perspectives.zhangxuefeng_perspective import ZhangxuefengPerspective
from super_thinking.perspectives.naval_perspective import NavalPerspective
from super_thinking.perspectives.xmentor_perspective import XmentorPerspective
from super_thinking.perspectives.darwin_perspective import DarwinPerspective
from super_thinking.perspectives.risk_detail_perspective import RiskDetailPerspective
from super_thinking.perspectives.doubt_perspective import DoubtPerspective
from super_thinking.perspectives.stakeholder_perspective import StakeholderPerspective
from super_thinking.perspectives.past_experience_perspective import PastExperiencePerspective

ALL_PERSPECTIVES = [
    MaoPerspective,
    MagiDebatePerspective,
    MetaThinkingPerspective,
    VerificationPerspective,
    TagmemoPerspective,
    MsaPerspective,
    VcpPerspective,
    ElonPerspective,
    JobsPerspective,
    ZhangxuefengPerspective,
    NavalPerspective,
    XmentorPerspective,
    DarwinPerspective,
    RiskDetailPerspective,
    DoubtPerspective,
    StakeholderPerspective,
    PastExperiencePerspective,
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
    "ElonPerspective",
    "JobsPerspective",
    "ZhangxuefengPerspective",
    "NavalPerspective",
    "XmentorPerspective",
    "DarwinPerspective",
    "RiskDetailPerspective",
    "DoubtPerspective",
    "StakeholderPerspective",
    "PastExperiencePerspective",
    "ALL_PERSPECTIVES",
]
