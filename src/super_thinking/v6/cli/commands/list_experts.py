"""
List experts/methods subcommand for superthink CLI.

Usage: superthink list experts [OPTIONS]
       superthink list methods [OPTIONS]
"""

from __future__ import annotations

from typing import Optional

import typer

from ..render import MockExpertPool, RichRenderer, get_mock_pool, get_renderer


@app.command("list")
def list_cmd(
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
        superthink list experts --search=辩证
    """
    renderer: RichRenderer = get_renderer()
    pool: MockExpertPool = get_mock_pool()
    
    if category == "experts":
        if search:
            results = pool.search_experts(search)
            if not results:
                renderer.print_warning(f"No experts found matching '{search}'")
                return
            renderer.print_expert_table(results, f"Search Results: {search}")
        elif domain:
            results = pool.list_experts(domain=domain)
            if not results:
                renderer.print_warning(f"No experts found in domain '{domain}'")
                return
            renderer.print_expert_table(results, f"Experts in {domain}")
        else:
            results = pool.list_experts()
            renderer.print_expert_table(results, f"Available Experts ({len(results)})")
        
        if format == "json":
            renderer.print_json(results)
    
    elif category == "methods":
        results = pool.list_methods()
        renderer.print_method_table(results, f"Available Methods ({len(results)})")
        
        if format == "json":
            renderer.print_json(results)
    
    else:
        renderer.print_error("E006", f"Unknown category '{category}'",
                           "Use 'experts' or 'methods'")


# Fix: Add typer app decorator
from typer import Typer
app = Typer(help="List subcommand")


if __name__ == "__main__":
    typer.run(list_cmd)
