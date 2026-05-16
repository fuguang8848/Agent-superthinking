"""Formatter - formats jury synthesis into final output."""

from typing import Optional

from super_thinking.perspectives._interface import PerspectiveOutput


class Formatter:
    """Formats deliberation results into final verdict."""

    def format(
        self,
        outputs: list[PerspectiveOutput],
        conflicts: Optional[list[dict]] = None,
        consensus: Optional[list[str]] = None,
    ) -> PerspectiveOutput:
        """Format all outputs, conflicts, and consensus into a final verdict."""
        if not outputs:
            raise ValueError("No outputs to format")

        # Build summary of each perspective
        summary_parts: list[str] = []
        for o in outputs:
            summary_parts.append(
                f"**{o.perspective_name}**（置信度：{o.confidence:.2f}）：\n{o.analysis[:200]}..."
            )

        # Format conflicts
        conflict_parts: list[str] = []
        if conflicts:
            conflict_parts.append(f"**检测到 {len(conflicts)} 个冲突**：")
            for c in conflicts:
                conflict_parts.append(f"• {c['description']}")

        # Format consensus
        consensus_parts: list[str] = []
        if consensus:
            consensus_parts.append("**共识点**：")
            for c in consensus:
                consensus_parts.append(f"• {c}")

        # Build final analysis
        analysis_lines = ["## 🔮 多元视角综合裁决\n"]
        analysis_lines.append(f"综合 {len(outputs)} 个视角的分析结果：\n")

        for summary in summary_parts:
            analysis_lines.append(f"{summary}\n")

        if conflict_parts:
            analysis_lines.append("\n".join(conflict_parts) + "\n")

        if consensus_parts:
            analysis_lines.append("\n".join(consensus_parts) + "\n")

        # Final synthesis
        avg_confidence = sum(o.confidence for o in outputs) / len(outputs)
        analysis_lines.append(
            f"**综合置信度**：{avg_confidence:.2f}\n"
        )
        analysis_lines.append(
            "各视角分析已综合，请参考上述结论做出判断。"
        )

        return "\n".join(analysis_lines)
