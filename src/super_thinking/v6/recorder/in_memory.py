"""
recorder/in_memory.py - In-Memory Session Recorder

Re-exports InMemoryRecorder from the top-level session_recorder module
for the path expected by the v6 entrypoint API.
"""

from ..session_recorder import InMemoryRecorder

__all__ = ["InMemoryRecorder"]
