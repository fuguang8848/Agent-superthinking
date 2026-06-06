"""
v6 CLI Render Module

Uses Rich library for colors, tables, progress bars.
Separates CLI invocation layer from rendering layer for testability.

Author: Frontend Engineer
Version: 6.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generator, Optional

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table


@dataclass
class RenderConfig:
    color: bool = True
    emoji: bool = True
    verbosity: str = "normal"
    width: Optional[int] = None


class RichRenderer:
    COLOR_PRIMARY = "cyan"
    COLOR_SECONDARY = "blue"
    COLOR_ACCENT = "yellow"
    COLOR_SUCCESS = "green"
    COLOR_WARNING = "yellow"
    COLOR_ERROR = "red"
    COLOR_MUTED = "dim"
    
    EXPERT_COLORS = [
        "cyan", "magenta", "green", "yellow", 
        "blue", "red", "white", "bright_black"
    ]
    
    def __init__(self, console: Optional[Console] = None, config: Optional[RenderConfig] = None):
        self._console = console or Console()
        self._config = config or RenderConfig()
        self._expert_color_idx = 0
    
    @property
    def console(self) -> Console:
        return self._console
    
    @property
    def config(self) -> RenderConfig:
        return self._config
    
    def _next_expert_color(self) -> str:
        color = self.EXPERT_COLORS[self._expert_color_idx]
        self._expert_color_idx = (self._expert_color_idx + 1) % len(self.EXPERT_COLORS)
        return color
    
    def reset_expert_colors(self) -> None:
        self._expert_color_idx = 0
    
    def print(self, *args: Any, **kwargs: Any) -> None:
        self._console.print(*args, **kwargs)
    
    def print_json(self, data: Any) -> None:
        import json
        syntax = Syntax(json.dumps(data, ensure_ascii=False, indent=2), "json")
        self._console.print(syntax)
    
    def print_title(self, title: str, subtitle: Optional[str] = None) -> None:
        self._console.print()
        sep = "=" * 60
        self._console.print(f"[bold {self.COLOR_PRIMARY}]{sep}[/bold]")
        self._console.print(f"[bold {self.COLOR_PRIMARY}]{title.center(60)}[/bold]")
        if subtitle:
            self._console.print(f"[bold {self.COLOR_PRIMARY}]{'-' * 60}[/bold]")
            self._console.print(f"[{self.COLOR_SECONDARY}]{subtitle}[/]")
        self._console.print(f"[bold {self.COLOR_PRIMARY}]{sep}[/bold]")
        self._console.print()
    
    def print_header(self, text: str) -> None:
        self._console.print()
        self._console.print(f"[bold {self.COLOR_SECONDARY}]{text}[/bold]")
        self._console.print(f"[{self.COLOR_MUTED}]{'-' * 60}[/]")
        self._console.print()
    
    def print_expert_table(self, experts: list[dict[str, Any]], title: str = "Available Experts") -> None:
        table = Table(title=title, show_header=True, header_style=f"bold {self.COLOR_PRIMARY}")
        table.add_column("ID", style="cyan", width=15)
        table.add_column("Name", style="green", width=12)
        table.add_column("Domain", style="blue", width=12)
        table.add_column("Methods", style="yellow", width=20)
        table.add_column("Description", style="white", width=40)
        
        for expert in experts:
            table.add_row(
                expert.get("id", ""),
                expert.get("name", ""),
                expert.get("domain", ""),
                expert.get("methods", ""),
                expert.get("description", ""),
            )
        
        self._console.print()
        self._console.print(table)
        self._console.print()
    
    def print_method_table(self, methods: list[dict[str, Any]], title: str = "Available Methods") -> None:
        table = Table(title=title, show_header=True, header_style=f"bold {self.COLOR_PRIMARY}")
        table.add_column("ID", style="cyan", width=15)
        table.add_column("Name", style="green", width=15)
        table.add_column("Type", style="blue", width=12)
        table.add_column("Description", style="white", width=50)
        
        for method in methods:
            table.add_row(
                method.get("id", ""),
                method.get("name", ""),
                method.get("type", ""),
                method.get("description", ""),
            )
        
        self._console.print()
        self._console.print(table)
        self._console.print()
    
    def print_expert_speech(
        self, 
        expert_name: str, 
        content: str, 
        role: str = "initial",
        color: Optional[str] = None
    ) -> None:
        color = color or self._next_expert_color()
        
        role_emoji = ""
        role_text = ""
        if role == "initial":
            role_emoji = ">" if self._config.emoji else ""
            role_text = "Initial"
        elif role == "rebuttal":
            role_emoji = ">>" if self._config.emoji else ""
            role_text = "Rebuttal"
        elif role == "final":
            role_emoji = "***" if self._config.emoji else ""
            role_text = "Final"
        
        header = f"[bold {color}]{role_emoji}【{expert_name}】[/bold]"
        if role_text:
            header += f" [dim]({role_text})[/dim]"
        
        self._console.print()
        self._console.print(header)
        self._console.print(f"[{color}]{'-' * 40}[/]")
        
        for line in content.split("\n"):
            if line.strip():
                self._console.print(f"[{color}]{line}[/{color}]")
            else:
                self._console.print()
        
        self._console.print()
    
    def print_argument_menu(self, arguments: list[dict[str, Any]], focus: list[str]) -> None:
        self._console.print()
        self._console.print(f"[bold {self.COLOR_ACCENT}]## Argument Menu[/bold]")
        self._console.print(f"[{self.COLOR_MUTED}]{'-' * 40}[/]")
        
        for i, arg in enumerate(arguments, 1):
            author = arg.get("author", "Unknown")
            claim = arg.get("claim", "")
            confidence = arg.get("confidence", 0.5)
            
            confidence_bar = "=" * int(confidence * 10) + "-" * (10 - int(confidence * 10))
            confidence_str = f"[{self.COLOR_SUCCESS}]{confidence_bar}[/] {confidence:.1f}"
            
            self._console.print(f"[{self.COLOR_PRIMARY}]{i}.[/] [bold]{author}[/bold]: {claim}")
            self._console.print(f"   {confidence_str}")
        
        if focus:
            self._console.print()
            self._console.print(f"[bold {self.COLOR_WARNING}]>> Focus Areas:[/bold]")
            for item in focus:
                self._console.print(f"  - {item}")
        
        self._console.print()
    
    def round_progress(
        self, 
        current: int, 
        total: int, 
        phase: str,
        expert_status: dict[str, str]
    ) -> None:
        self._console.print()
        
        bar_length = 40
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "=" * filled + "-" * (bar_length - filled)
        percentage = int(100 * current / total) if total > 0 else 0
        
        self._console.print(f"[bold {self.COLOR_PRIMARY}][{current}/{total}] Round {current}: {phase}[/bold]")
        self._console.print(f"[{self.COLOR_PRIMARY}]{bar}[/] {percentage}%")
        
        self._console.print()
        for expert, status in expert_status.items():
            status_icon = "OK" if status == "done" else ".." if status == "active" else "--"
            status_color = self.COLOR_SUCCESS if status == "done" else self.COLOR_WARNING if status == "active" else self.COLOR_MUTED
            self._console.print(f"  [{status_color}]{status_icon}[/] {expert}")
        
    
    def print_error(self, code: str, message: str, hint: Optional[str] = None) -> None:
        self._console.print()
        self._console.print(f"[bold {self.COLOR_ERROR}]> ERROR] {code}[/bold]")
        self._console.print(f"[{self.COLOR_ERROR}]{message}[/]")
        
        if hint:
            self._console.print()
            self._console.print(f"[bold {self.COLOR_WARNING}]>> Hint:[/bold]")
            self._console.print(f"[{self.COLOR_MUTED}]{hint}[/]")
        
        self._console.print()
    
    def print_warning(self, message: str) -> None:
        self._console.print()
        self._console.print(f"[bold {self.COLOR_WARNING}]> WARNING] {message}[/bold]")
        self._console.print()
    
    def print_success(self, message: str) -> None:
        self._console.print(f"[bold {self.COLOR_SUCCESS}]{message}[/bold]")
    
    def print_init_welcome(self) -> None:
        self._console.print()
        self._console.print(f"[bold {self.COLOR_PRIMARY}]+=============================================================+[/]")
        self._console.print(f"[bold {self.COLOR_PRIMARY}]|           SuperThinking v6 - CLI                       |[/]")
        self._console.print(f"[bold {self.COLOR_PRIMARY}]+=============================================================+[/]")
        self._console.print()
        self._console.print(f"[{self.COLOR_MUTED}]Quick Start:[/]")
        self._console.print(f"  superthink debate --mock \"your question\"  # Start mock debate")
        self._console.print(f"  superthink list experts               # List experts")
        self._console.print(f"  superthink --help                   # Show help")
        self._console.print()


class MockExpertPool:
    """Mock expert pool for --mock mode"""
    
    MOCK_EXPERTS = [
        {"id": "socrates", "name": "Socrates", "domain": "Philosophy", "type": "Historical", 
         "methods": "Dialectics", "keywords": "Know thyself", 
         "description": "Ancient Greek philosopher.", "scenarios": "Critical thinking"},
        {"id": "confucius", "name": "Confucius", "domain": "Philosophy", "type": "Historical",
         "methods": "Ethics", "keywords": "Harmony",
         "description": "Chinese philosopher.", "scenarios": "Ethics"},
        {"id": "einstein", "name": "Einstein", "domain": "Science", "type": "Historical",
         "methods": "First principles", "keywords": "Imagination",
         "description": "20th century physicist.", "scenarios": "Innovation"},
        {"id": "sunzi", "name": "Sun Tzu", "domain": "Military", "type": "Historical",
         "methods": "Strategy", "keywords": "Win without fighting",
         "description": "Military strategist.", "scenarios": "Strategy"},
    ]
    
    MOCK_METHODS = [
        {"id": "bayesian", "name": "Bayesian", "type": "Probabilistic", "description": "Probability reasoning."},
        {"id": "gametheory", "name": "Game Theory", "type": "Strategy", "description": "Strategic interactions."},
        {"id": "dialectics", "name": "Dialectics", "type": "Analysis", "description": "Thesis-antithesis."},
    ]
    
    def list_experts(self, domain: Optional[str] = None) -> list[dict[str, Any]]:
        if domain:
            return [e for e in self.MOCK_EXPERTS if e["domain"] == domain]
        return self.MOCK_EXPERTS
    
    def get_expert(self, expert_id: str) -> Optional[dict[str, Any]]:
        for expert in self.MOCK_EXPERTS:
            if expert["id"] == expert_id:
                return expert
        return None
    
    def list_methods(self) -> list[dict[str, Any]]:
        return self.MOCK_METHODS
    
    def search_experts(self, query: str) -> list[dict[str, Any]]:
        query_lower = query.lower()
        return [e for e in self.MOCK_EXPERTS
                if query_lower in e["id"].lower() or query_lower in e["name"].lower()]
    
    def mock_debate(
        self, 
        question: str, 
        experts: list[str],
        renderer: RichRenderer,
        rounds: int = 2
    ) -> dict[str, Any]:
        renderer.print_title("Multi-Expert Debate", "SuperThinking v6")
        renderer._console.print(f"[bold {renderer.COLOR_PRIMARY}]> Question[/bold]")
        renderer._console.print(f"[white]{question}[/]")
        
        expert_names = [self.get_expert(e)["name"] for e in experts if self.get_expert(e)]
        renderer._console.print()
        renderer._console.print(f"[bold {renderer.COLOR_PRIMARY}]> Participants:[/bold]" + ", ".join(expert_names))
        
        for round_num in range(1, rounds + 1):
            renderer.print_header(f"Round {round_num} - Parallel Statements")
            
            for expert_id in experts:
                expert = self.get_expert(expert_id)
                if not expert:
                    continue
                
                content = self._generate_mock_speech(expert, question, round_num)
                renderer.print_expert_speech(expert["name"], content, role="initial" if round_num == 1 else "rebuttal")
            
            if round_num < rounds:
                renderer.print_argument_menu(
                    [{"author": "Socrates", "claim": "Need to clarify definition", "confidence": 0.8},
                     {"author": "Confucius", "claim": "AI is a tool", "confidence": 0.7}],
                    ["AI ethics"]
                )
        
        renderer.print_header("Conclusion")
        renderer._console.print("[bold green]OK Debate completed[/]")
        
        return {"status": "completed", "question": question, "experts": experts, "rounds": rounds}
    
    def _generate_mock_speech(self, expert: dict, question: str, round_num: int) -> str:
        return f"Regarding '{question}', from a {expert['domain'].lower()} perspective.\n\n[Mock response for {expert['name']}]"


# Global instances
_default_renderer: Optional[RichRenderer] = None
_mock_pool: Optional[MockExpertPool] = None


def get_renderer() -> RichRenderer:
    global _default_renderer
    if _default_renderer is None:
        _default_renderer = RichRenderer()
    return _default_renderer


def get_mock_pool() -> MockExpertPool:
    global _mock_pool
    if _mock_pool is None:
        _mock_pool = MockExpertPool()
    return _mock_pool
