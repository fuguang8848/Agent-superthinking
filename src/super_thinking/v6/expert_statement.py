"""
v6 Expert Statement Module

Dual-track statement parsing and validation.
"""

from __future__ import annotations
import re, time, logging
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable, Any
from .types import ExpertId, ExpertStatement, SpeakRole, ArgumentRef, MethodologyCall, SuggestedArgument

logger = logging.getLogger(__name__)

MAX_CONTENT_LENGTH = 8000
MAX_FREE_ADDENDUM_LENGTH = 600
MIN_CONTENT_LENGTH = 20

DUAL_TRACK_SEPARATOR = "[Free Addendum]"
DUAL_TRACK_SEPARATOR_ALT = "[Supplementary]"

@dataclass
class ParseResult:
    content: str
    free_addendum: str | None = None
    targeted_argument: ArgumentRef | None = None
    extra_targets: list[ArgumentRef] = field(default_factory=list)
    methodology_calls: list[MethodologyCall] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    confidence: float = 0.5
    suggested_arguments: list[SuggestedArgument] = field(default_factory=list)

class StatementParser:
    TARGET_PATTERNS = [
        r'针对\s*["""](.+?)["""]',
        r'针对论点\s*["""](.+?)["""]',
        r'反驳\s*["""](.+?)["""]',
        r'回应\s*["""](.+?)["""]',
    ]
    
    METHODOLOGY_PATTERNS = [
        r'用\s*(博弈论|伦理学|经济学|法学|社会学|心理学|运筹学|管理学)\s*检验',
        r'从\s*(博弈论|伦理学|经济学|法学|社会学|心理学|运筹学|管理学)\s*视角',
    ]
    
    def __init__(self, timestamp_provider=None):
        self._timestamp_provider = timestamp_provider or (lambda: time.time())
        self._compiled_target = [re.compile(p, re.UNICODE) for p in self.TARGET_PATTERNS]
        self._compiled_methodology = [re.compile(p, re.UNICODE) for p in self.METHODOLOGY_PATTERNS]
    
    def parse(self, raw_text: str, expert_id: ExpertId, expert_name: str, role: SpeakRole, existing_arguments=None) -> ParseResult:
        result = ParseResult(content=raw_text.strip())
        if not raw_text or not raw_text.strip():
            result.warnings.append("Empty raw text")
            return result
        self._split_dual_track(raw_text, result)
        self._extract_targets(result.content, existing_arguments, result)
        self._detect_methodology(result.content, expert_id, result)
        self._validate(result, role)
        self._estimate_confidence(result)
        return result
    
    def _split_dual_track(self, text: str, result: ParseResult) -> None:
        for sep in [DUAL_TRACK_SEPARATOR, DUAL_TRACK_SEPARATOR_ALT]:
            if sep in text:
                parts = text.split(sep, 1)
                result.content = parts[0].strip()
                result.free_addendum = parts[1].strip()
                return
    
    def _extract_targets(self, content: str, existing_arguments, result: ParseResult) -> None:
        for pattern in self._compiled_target:
            for match in pattern.finditer(content):
                ref_text = match.group(1)
                if existing_arguments:
                    for arg in existing_arguments:
                        if ref_text.lower() in arg.claim.lower():
                            ref = ArgumentRef(argument_id=arg.argument_id, author_id=arg.author_id, round_number=arg.round_number)
                            if not result.targeted_argument:
                                result.targeted_argument = ref
                            else:
                                result.extra_targets.append(ref)
                            break
    
    def _detect_methodology(self, content: str, expert_id: ExpertId, result: ParseResult) -> None:
        for pattern in self._compiled_methodology:
            for match in pattern.finditer(content):
                method_name = match.group(1)
                from .types import MethodId
                method_id = self._map_methodology_name(method_name)
                call = MethodologyCall(method_id=method_id, arguments={"source": "declaration"}, caller_id=expert_id, requested_at=self._timestamp_provider())
                result.methodology_calls.append(call)
    
    def _map_methodology_name(self, name: str):
        from .types import MethodId
        mapping = {
            "博弈论": MethodId("gametheory"), "伦理学": MethodId("ethics"),
            "经济学": MethodId("economics"), "法学": MethodId("jurisprudence"),
            "社会学": MethodId("sociology"), "心理学": MethodId("psychology"),
            "运筹学": MethodId("operationsresearch"), "管理学": MethodId("management"),
        }
        return mapping.get(name, MethodId(name.lower()))
    
    def _validate(self, result: ParseResult, role: SpeakRole) -> None:
        if len(result.content) > MAX_CONTENT_LENGTH:
            result.warnings.append(f"Content exceeds {MAX_CONTENT_LENGTH} chars")
        if len(result.content) < MIN_CONTENT_LENGTH:
            result.warnings.append("Content is too short")
    
    def _estimate_confidence(self, result: ParseResult) -> None:
        confidence = 0.5
        if result.targeted_argument:
            confidence += 0.1
        if len(result.extra_targets) >= 2:
            confidence += 0.05
        if result.methodology_calls:
            confidence += 0.1
        if result.free_addendum:
            confidence += 0.05
        if 100 <= len(result.content) <= 2000:
            confidence += 0.1
        result.confidence = min(1.0, confidence)

def parse_statement(raw_text: str, expert_id: ExpertId, expert_name: str, role: SpeakRole, existing_arguments=None) -> ExpertStatement:
    parser = StatementParser()
    parse_result = parser.parse(raw_text, expert_id, expert_name, role, existing_arguments)
    return ExpertStatement(
        expert_id=expert_id, expert_name=expert_name, role=role,
        targeted_argument=parse_result.targeted_argument,
        extra_targets=tuple(parse_result.extra_targets),
        content=parse_result.content,
        free_addendum=parse_result.free_addendum,
        methodology_call=parse_result.methodology_calls[0] if parse_result.methodology_calls else None,
        confidence=parse_result.confidence,
        suggested_arguments=tuple(parse_result.suggested_arguments),
        warnings=tuple(parse_result.warnings),
    )

__all__ = ["StatementParser", "ParseResult", "parse_statement", "DUAL_TRACK_SEPARATOR"]

# =============================================================================
# Statement Validator
# =============================================================================

@runtime_checkable
class ExpertStatementValidator(Protocol):
    """Protocol for statement validation."""
    def validate(self, statement: ExpertStatement) -> tuple[bool, list[str]]:
        """Validate statement. Returns (is_valid, error_messages)."""
        ...


class DefaultStatementValidator:
    """Default statement validator implementation."""
    
    def validate(self, statement: ExpertStatement) -> tuple[bool, list[str]]:
        errors = []
        
        if not statement.content or len(statement.content.strip()) < MIN_CONTENT_LENGTH:
            errors.append(f"Content too short (min {MIN_CONTENT_LENGTH} chars)")
        
        if len(statement.content) > MAX_CONTENT_LENGTH:
            errors.append(f"Content too long (max {MAX_CONTENT_LENGTH} chars)")
        
        if statement.free_addendum and len(statement.free_addendum) > MAX_FREE_ADDENDUM_LENGTH:
            errors.append(f"Free addendum too long (max {MAX_FREE_ADDENDUM_LENGTH} chars)")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_reference(self, ref: ArgumentRef, available_args: list) -> bool:
        """Validate that a reference points to a valid argument."""
        for arg in available_args:
            if arg.argument_id == ref.argument_id:
                return True
        return False


__all__ = [
    "StatementParser", "ParseResult", "parse_statement",
    "ExpertStatementValidator", "DefaultStatementValidator",
    "DUAL_TRACK_SEPARATOR"
]
