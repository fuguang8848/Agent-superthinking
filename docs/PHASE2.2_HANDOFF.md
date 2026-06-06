# Phase 2.2 Hand-off Document

## v6 CLI Entry Point Implementation

**Date:** 2026-06-05
**Status:** Ready for Review
**Phase:** 2.2

---

## Deliverables

### 1. CLI Structure

```
src/super_thinking/v6/cli/
├── __init__.py          # Exposes main()
├── main.py              # Typer app with commands
├── render.py            # Rich renderer (color/table/progress)
└── commands/
    ├── __init__.py      # Subcommand exports
    ├── debate.py        # superthink debate command
    ├── consult.py       # superthink consult command
    └── list_experts.py  # superthink list experts/methods
```

### 2. Entry Points

**pyproject.toml:**
```toml
[project.scripts]
superthink = "super_thinking.v6.cli.main:app"

dependencies = [
    "typer>=0.12.0",
    "rich>=13.7.0",
]
```

### 3. Commands

| Command | Description |
|--------|-------------|
| `superthink debate [--mock] "question"` | Start multi-expert debate |
| `superthink consult <expert_id> "question"` | Consult single expert |
| `superthink list experts` | List available experts |
| `superthink list methods` | List available methods |
| `superthink --help` | Show help |

### 4. Features

- **Mock Mode:** `--mock` flag for demonstration without real LLM
- **Rich Rendering:** Colors, tables, progress bars via Rich library
- **Type Hints:** Full type annotation coverage
- **Separation:** CLI layer separated from rendering layer (testable)

### 5. Testing

To test the CLI (mock mode):
```bash
# Install in editable mode
pip install -e .

# Run mock debate
superthink debate --mock "Will AI replace humans?"

# List experts
superthink list experts

# Consult an expert
superthink consult socrates "What is virtue?"
```

---

## Dependencies Added

- `typer>=0.12.0` - CLI framework
- `rich>=13.7.0` - Terminal rendering

---

## Next Steps

1. **Review:** Code review by QA/Architect
2. **Real LLM Integration:** Connect debate.py to actual v6 business logic
3. **Additional Commands:** `init`, `config`, `info` (see CLI_DESIGN.md)
4. **Error Handling:** Enhance error codes and hints
5. **Streaming:** Implement real-time output streaming

---

## Notes

- All commands support `--mock` mode for demonstration
- MockExpertPool provides 4 demo experts: socrates, confucius, einstein, sunzi
- Real LLM mode is stubbed and will be implemented in later phases
- Render layer (render.py) is 100% testable with injectable Console

---

**Frontend Engineer**
Handoff complete.
