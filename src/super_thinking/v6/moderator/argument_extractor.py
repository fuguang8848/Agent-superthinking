"""
ArgumentExtractor - 论点提取器
"""
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

@dataclass
class ArgumentExtractor:
    use_llm: bool = False

    def extract(self, statement):
        suggestions = []
        sentences = self._split_sentences(statement.content)
        for sentence in sentences:
            if len(sentence) < 20:
                continue
            if self._is_argument(sentence):
                claim = self._extract_claim(sentence)
                rationale = self._extract_rationale(sentence, statement.content)
                confidence = self._estimate_confidence(sentence)
                from ..types import SuggestedArgument
                suggestion = SuggestedArgument(
                    claim=claim,
                    rationale=rationale,
                    quote=sentence,
                    confidence=confidence,
                    targets=self._find_targets(statement),
                )
                suggestions.append(suggestion)
        if not suggestions and len(statement.content) > 50:
            from ..types import SuggestedArgument
            suggestion = SuggestedArgument(
                claim=self._extract_claim(statement.content),
                rationale="",
                quote=statement.content[:200],
                confidence=statement.confidence,
                targets=self._find_targets(statement),
            )
            suggestions.append(suggestion)
        return suggestions

    def _split_sentences(self, text):
        # Split on Chinese sentence delimiters and newlines
        return [s.strip() for s in re.split(r"[。！？；\n]", text) if s.strip()]

    def _is_argument(self, sentence):
        markers = ["我认为", "我的观点是", "应该", "必须", "主要观点", "所以"]
        return any(m in sentence for m in markers)

    def _extract_claim(self, sentence):
        claim = sentence
        for m in ["我认为", "我的观点是", "因为"]:
            if claim.startswith(m):
                claim = claim[len(m):]
        return (claim[:200] + '...') if len(claim) > 200 else claim.strip()

    def _extract_rationale(self, sentence, context):
        idx = context.find(sentence)
        if idx > 0 and ("因为" in context or "所以" in context):
            return context[max(0, idx-100):idx].strip()
        return ""

    def _estimate_confidence(self, sentence):
        high = ["一定", "绝对", "肯定", "显然"]
        med = ["应该", "可能", "大概"]
        low = ["也许", "可能", "不确定"]
        if any(m in sentence for m in high): return 0.85
        if any(m in sentence for m in med): return 0.65
        if any(m in sentence for m in low): return 0.45
        return 0.5

    def _find_targets(self, statement):
        if statement.targeted_argument:
            return (statement.targeted_argument,) + statement.extra_targets
        return statement.extra_targets


def extract_arguments_from_statement(statement) -> list:
    """
    Standalone function that wraps ArgumentExtractor.extract().
    """
    extractor = ArgumentExtractor()
    return extractor.extract(statement)
