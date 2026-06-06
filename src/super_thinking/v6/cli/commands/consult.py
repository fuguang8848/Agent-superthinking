"""
Consult subcommand for superthink CLI.

Usage: superthink consult EXPERT_ID QUESTION
"""

from __future__ import annotations

import typer

from ..render import MockExpertPool, RichRenderer, get_mock_pool, get_renderer


def consult_cmd(
    expert_id: str = typer.Argument(..., help="Expert ID to consult"),
    question: str = typer.Argument(..., help="Question to ask"),
    mock: bool = typer.Option(True, "--mock", help="Use mock mode"),
) -> None:
    """
    Consult a single expert.
    
    Examples:
    
        superthink consult socrates "What is virtue?"
        superthink consult einstein "Is time travel possible?"
    """
    renderer: RichRenderer = get_renderer()
    
    if mock:
        pool: MockExpertPool = get_mock_pool()
        expert = pool.get_expert(expert_id)
        
        if expert is None:
            renderer.print_error("E001", f"Expert '{expert_id}' not found",
                               "Use 'superthink list experts' to see available experts")
            raise typer.Exit(code=1)
        
        # Display expert info
        renderer.print_title(f"Consultation: {expert['name']}", "SuperThinking v6")
        renderer._console.print(f"[bold {renderer.COLOR_SECONDARY}]Domain:[/bold] {expert['domain']}")
        renderer._console.print(f"[bold {renderer.COLOR_SECONDARY}]Methods:[/bold] {expert['methods']}")
        renderer._console.print()
        renderer._console.print(f"[bold {renderer.COLOR_PRIMARY}]> Question:[/bold]")
        renderer._console.print(f"[white]{question}[/]")
        renderer._console.print()
        renderer._console.print(f"[yellow]Mock response:[/yellow]")
        renderer._console.print(f"[white]As {expert['name']}, I would approach this question from the perspective of {expert['methods']}.[/]")
        renderer._console.print()
        renderer.print_success("Consultation complete")
    else:
        renderer.print_warning("Real LLM mode not yet implemented. Use --mock for demonstration.")


if __name__ == "__main__":
    typer.run(consult_cmd)
