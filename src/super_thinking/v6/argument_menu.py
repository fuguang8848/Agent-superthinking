"""
v6 论点菜单模块

负责从专家发言中提取论点、合并菜单、计算重叠率等。
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .types import (
    Argument,
    ArgumentId,
    ArgumentMenu,
    ArgumentRef,
    ArgumentStatus,
    ExpertId,
    RoundNumber,
    SuggestedArgument,
)

if TYPE_CHECKING:
    from .types import DebateSession, ExpertStatement

logger = logging.getLogger(__name__)


# =============================================================================
# ArgumentMenu 扩展方法（作为模块函数）
# =============================================================================

def compute_overlap_ratio(menu1: ArgumentMenu, menu2: ArgumentMenu) -> float:
    """
    计算两个菜单的重叠率（Jaccard 相似度）。
    
    基于论点 claim 的文本相似度计算，允许语义重叠而不仅是字符串相等。
    """
    if not menu1.items and not menu2.items:
        return 1.0
    if not menu1.items or not menu2.items:
        return 0.0
    
    claims1 = {arg.claim.lower().strip() for arg in menu1.items}
    claims2 = {arg.claim.lower().strip() for arg in menu2.items}
    
    # Jaccard: |A ∩ B| / |A ∪ B|
    intersection = len(claims1 & claims2)
    union = len(claims1 | claims2)
    
    if union == 0:
        return 1.0
    
    return intersection / union


def merge_menus(
    prev_menu: ArgumentMenu | None,
    new_menu: ArgumentMenu,
    keep_history: bool = True
) -> tuple[ArgumentMenu, dict]:
    """
    合并两个轮次的菜单。
    
    Args:
        prev_menu: 上一轮菜单（可为 None 表示首轮）
        new_menu: 本轮新菜单
        keep_history: 是否保留历史论点
    
    Returns:
        (合并后的菜单, 统计信息)
    """
    stats = {
        "new_count": 0,
        "overlap_count": 0,
        "replaced_count": 0,
        "discarded_count": len(new_menu.discarded),
    }
    
    # 收集已有论点 ID
    existing_ids: set[ArgumentId] = set()
    all_items: list[Argument] = []
    
    if keep_history and prev_menu is not None:
        for arg in prev_menu.items:
            existing_ids.add(arg.argument_id)
            if arg.status == ArgumentStatus.ACTIVE:
                all_items.append(arg)
    
    # 处理新论点
    for arg in new_menu.items:
        if arg.argument_id in existing_ids:
            stats["overlap_count"] += 1
            # 保留新版本（覆盖）
            all_items.append(arg)
        else:
            stats["new_count"] += 1
            all_items.append(arg)
        existing_ids.add(arg.argument_id)
    
    # 收集已收敛的论点
    converged_items: list[Argument] = list(new_menu.converged)
    if keep_history and prev_menu is not None:
        for arg in prev_menu.converged:
            if arg not in converged_items:
                converged_items.append(arg)
    
    merged = ArgumentMenu(
        round_number=new_menu.round_number,
        items=tuple(all_items),
        converged=tuple(converged_items),
        focus=new_menu.focus,
        discarded=new_menu.discarded,
    )
    
    return merged, stats


# =============================================================================
# StructuredExtractor — 从发言中提取论点
# =============================================================================

@dataclass
class ExtractionResult:
    """提取结果"""
    arguments: list[SuggestedArgument] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class StructuredExtractor:
    """
    结构化论点提取器。
    
    从专家发言中解析出候选论点列表，支持：
    - 序号论点（1. xxx / - xxx / * xxx）
    - 针对引用（"针对论点A" / "反驳B"）
    - 证据标记（"证据：" / "研究表明"）
    - 方法论声明（"用博弈论检验"）
    """
    
    # 论点序号模式
    ARGUMENT_PATTERNS = [
        # Markdown 序号: 1. xxx, 2. xxx
        r'^\s*(\d+)\.\s+(.+)$',
        # 短横线: - xxx, - [xxx]
        r'^\s*[-−•▪]\s+(.+)$',
        # 星号: * xxx
        r'^\s*\*\s+(.+)$',
        # 中文序号: （一）、（二）、第一、
        r'^\s*[（(]?(一|二|三|四|五|六|七|八|九|十|\d+)[）)]\s*[\.、:]?\s*(.+)$',
    ]
    
    # 证据标记
    EVIDENCE_PATTERNS = [
        r'证据[:：]\s*(.+?)(?=\n|$)',
        r'研究表明[:：]\s*(.+?)(?=\n|$)',
        r'数据显示[:：]\s*(.+?)(?=\n|$)',
        r'根据[^。]+[:：]\s*(.+?)(?=\n|$)',
    ]
    
    # 针对引用模式
    TARGET_PATTERNS = [
        r'针对\s*["""](.+?)["""]',
        r'针对论点\s*["""](.+?)["""]',
        r'反驳\s*["""](.+?)["""]',
        r'回应\s*["""](.+?)["""]',
        r'不同意\s*["""](.+?)["""]',
        r'同意\s*["""](.+?)["""]',
    ]
    
    # 方法论声明模式
    METHODOLOGY_PATTERNS = [
        r'用([' + '|'.join([
            '博弈论', '伦理学', '经济学', '法学', '社会学', '心理学',
            '博弈论', '运筹学', '管理学', '政治哲学', '分析哲学',
            '现象学', '存在主义', '后现代', '结构主义', '功能主义',
            '康德', '罗尔斯', '哈贝马斯', '尼采', '海德格尔',
        ]) + r'])检验',
        r'从([' + '|'.join([
            '博弈论', '伦理学', '经济学', '法学', '社会学', '心理学',
            '博弈论', '运筹学', '管理学', '政治哲学', '分析哲学',
            '现象学', '存在主义', '后现代', '结构主义', '功能主义',
            '康德', '罗尔斯', '哈贝马斯', '尼采', '海德格尔',
        ]) + r'])视角',
    ]
    
    def __init__(self, *, use_llm: bool = False, llm_provider=None):
        """
        Args:
            use_llm: 是否使用 LLM 增强提取（实验性）
            llm_provider: LLM provider 实例
        """
        self.use_llm = use_llm
        self.llm = llm_provider
        self._compiled_arg_patterns = [re.compile(p, re.MULTILINE) for p in self.ARGUMENT_PATTERNS]
        self._compiled_target_patterns = [re.compile(p, re.UNICODE) for p in self.TARGET_PATTERNS]
        self._compiled_evidence_patterns = [re.compile(p, re.UNICODE | re.DOTALL) for p in self.EVIDENCE_PATTERNS]
    
    def extract(
        self,
        text: str,
        expert_id: ExpertId,
        round_number: RoundNumber,
        existing_arguments: tuple[Argument, ...] = (),
    ) -> ExtractionResult:
        """
        从发言文本中提取论点。
        
        Args:
            text: 发言原文
            expert_id: 发言专家 ID
            round_number: 当前轮次
            existing_arguments: 现有论点列表（用于解析针对引用）
        
        Returns:
            ExtractionResult: 包含提取的论点和警告
        """
        result = ExtractionResult()
        
        if not text or not text.strip():
            result.warnings.append("Empty text provided for extraction")
            return result
        
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 尝试匹配论点序号
            claim = None
            for pattern in self._compiled_arg_patterns:
                match = pattern.match(line)
                if match:
                    # 第二组是论点内容
                    claim = match.group(2).strip() if match.lastindex >= 2 else match.group(1).strip()
                    break
            
            # 如果没匹配到序号，检查是否是实质性内容行
            if claim is None:
                # 跳过过于简短的行
                if len(line) < 20:
                    continue
                # 跳过可能是标题或分隔符的行
                if line.endswith(':') or line.endswith('：'):
                    continue
                if re.match(r'^#{1,6}\s', line):
                    continue
                claim = line
            
            # 提取证据
            supports: list[str] = []
            for pattern in self._compiled_evidence_patterns:
                matches = pattern.findall(text)
                supports.extend(matches)
            
            # 解析针对引用
            targets: list[ArgumentRef] = []
            for pattern in self._compiled_target_patterns:
                match = pattern.search(text)
                if match:
                    ref_text = match.group(1)
                    # 在现有论点中查找匹配
                    for arg in existing_arguments:
                        if ref_text.lower() in arg.claim.lower():
                            targets.append(ArgumentRef(
                                argument_id=arg.argument_id,
                                author_id=arg.author_id,
                                round_number=arg.round_number,
                            ))
            
            # 检查方法论声明
            methodology_call = None
