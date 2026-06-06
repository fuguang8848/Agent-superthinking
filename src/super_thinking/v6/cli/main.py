"""
v6 CLI Main Module

Main entry point for the superthink CLI using Typer.

Usage:
    superthink --help
    superthink debate "question"
    superthink list experts
    superthink consult socrates "question"
"""

from __future__ import annotations

from typing import Optional

import typer
from typing_extensions import Annotated

from .render import RichRenderer, get_renderer

# Create Typer app
app = typer.Typer(
    name="superthink",
    help="SuperThinking v6 - Multi-Expert Thinking Framework",
    add_completion=False,
)

# Subapps for commands
from .commands.debate import debate_cmd
from .commands.consult import consult_cmd


@app.command()
def debate(
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
    debate_cmd(question, experts, methods, rounds, mock, format)


@app.command()
def consult(
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
    consult_cmd(expert_id, question, mock)


@app.command()
def list_experts(
    category: str = typer.Argument("experts", help="Category: experts or methods"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Filter by domain"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search experts"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text/json"),
) -> None:
    """
    List available experts or methods.
    
    Examples:
    
        superthink list experts
        superthink list methods
        superthink list experts --domain=philosophy
    """
    from .commands.list_experts import list_cmd
    list_cmd(category, domain, search, format)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
) -> None:
    """
    SuperThinking v6 CLI - Multi-Expert Thinking Framework
    """
    if version:
        typer.echo("SuperThinking v6.0.0")
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        renderer: RichRenderer = get_renderer()
        renderer.print_init_welcome()
        typer.echo("Use --help to see available commands.")


if __name__ == "__main__":
    app()
