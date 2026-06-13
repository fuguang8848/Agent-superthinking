"""
Debate subcommand for superthink CLI.

Usage: superthink debate [OPTIONS] QUESTION
"""

from __future__ import annotations

from typing import Optional

import typer

from ..render import MockExpertPool, RichRenderer, get_mock_pool, get_renderer

# Type hints
QuestionStr = str
ExpertsList = list[str]


def debate_cmd(
    question: str = typer.Argument(..., help="Question to analyze"),
    experts: Optional[str] = typer.Option(None, "--experts", "-e", help="Comma-separated expert IDs"),
    methods: Optional[str] = typer.Option(None, "--methods", "-m", help="Comma-separated method IDs"),
    rounds: int = typer.Option(2, "--rounds", "-r", help="Number of debate rounds"),
    mock: bool = typer.Option(False, "--mock", help="Use mock mode (no LLM required)"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text/json"),
) -> None:
    """
    Start a multi-expert debate.
    
    Examples:
    
        superthink debate "Will AI replace humans?"
        superthink debate --experts=socrates,confucius "What is the meaning of life?"
        superthink debate --mock "Should we colonize Mars?"
    """
    renderer: RichRenderer = get_renderer()
    
    # Parse experts
    expert_ids: ExpertsList = []
    if experts:
        expert_ids = [e.strip() for e in experts.split(",")]
    else:
        # Default experts for mock mode
        expert_ids = ["socrates", "confucius"]
    
    # Validate experts
    if mock:
        pool: MockExpertPool = get_mock_pool()
        for expert_id in expert_ids:
            if pool.get_expert(expert_id) is None:
                renderer.print_warning(f"Expert '{expert_id}' not found, skipping")
                expert_ids.remove(expert_id)
        
        if not expert_ids:
            renderer.print_error("E001", "No valid experts specified", 
                               f"Use 'superthink list experts' to see available experts")
            raise typer.Exit(code=1)
        
        # Run mock debate
        result = pool.mock_debate(question, expert_ids, renderer, rounds)
        
        if format == "json":
            renderer.print_json(result)
    else:
        # Real LLM mode - placeholder for now
        renderer.print_title("Multi-Expert Debate", "SuperThinking v6")
        renderer._console.print(f"[yellow]Real LLM mode not yet implemented.[/]")
        renderer._console.print(f"[yellow]Use --mock flag for demonstration.[/]")
        raise typer.Exit(code=0)


if __name__ == "__main__":
    typer.run(debate_cmd)
