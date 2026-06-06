# conftest.py for test_v6_debate — re-exports fixtures from debate_conftest
# We use importlib to load debate_conftest by filesystem path.
import importlib.util
import sys
import os

_spec = importlib.util.spec_from_file_location(
    "_debate_fixtures",
    os.path.join(os.path.dirname(__file__), "debate_conftest.py"),
)
_debate_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_debate_mod)

# Register in sys.modules so test files importing 'from debate_conftest import ...'
# get the SAME module/classes as the fixtures
sys.modules['debate_conftest'] = _debate_mod

# Pull out what we need and expose at module level for pytest fixture discovery
mock_experts = _debate_mod.mock_experts
mock_moderator = _debate_mod.mock_moderator
sample_question = _debate_mod.sample_question
sample_debate_session = _debate_mod.sample_debate_session
ExpertStatement = _debate_mod.ExpertStatement
MockExpert = _debate_mod.MockExpert
MockModerator = _debate_mod.MockModerator
ArgumentMenu = _debate_mod.ArgumentMenu
DebateRound = _debate_mod.DebateRound
DebateSession = _debate_mod.DebateSession

# Make pytest fixtures available (pytest discovers fixtures from conftest.py
# via its own loader, not Python's normal import machinery)
# The pytest fixtures below are plain objects — pytest handles them via its own registry.
pytest_plugins = []
