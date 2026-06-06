"""
MenuBuilder -论点菜单构建器
"""
import re
from dataclasses import dataclass

@dataclass
class MenuBuilder:
    def build(self, round_number, suggested_arguments, previous_menu=None):
        items = []
        discarded = []
        prev_claims = set()
        if previous_menu:
            for arg in previous_menu.items:
                prev_claims.add(self._normalize(arg.claim))
        for suggested in suggested_arguments:
            if self._should_discard(suggested):
                discarded.append(suggested); continue
            norm = self._normalize(suggested.claim)
            if norm in prev_claims:
                discarded.append(suggested); continue
            from ..types import Argument, ArgumentStatus, generate_argument_id
            author_id = suggested.targets[0].author_id if suggested.targets else None
            argument = Argument(
                argument_id=generate_argument_id(round_number, len(items)),
                round_number=round_number,
                author_id=author_id,
                author_name='',
                claim=suggested.claim,
                rationale=suggested.rationale,
                supports=(),
                confidence=suggested.confidence,
                methodology_used=None,
                status=ArgumentStatus.ACTIVE,
                original_quote=suggested.quote,
            )
            items.append(argument)
            prev_claims.add(norm)
        focus = tuple(arg.claim for arg in sorted(items, key=lambda x: x.confidence, reverse=True)[:3])
        converged = previous_menu.converged if previous_menu else ()
        from ..types import ArgumentMenu
        return ArgumentMenu(round_number=round_number, items=tuple(items), converged=converged, focus=focus, discarded=tuple(discarded))
    def _normalize(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return re.sub(r'\s+', ' ', text).strip()
    def _should_discard(self, s):
        return len(s.claim) < 15 or s.confidence < 0.3 or not s.claim.strip()

def build_argument_menu(round_number, suggested, prev=None):
    return MenuBuilder().build(round_number, suggested, prev)
