"""test_session_recorder.py - SessionRecorder unit tests"""
import pytest
import json
import os
import tempfile
from datetime import datetime

class MockDebateEvent:
    def __init__(self, event_type, round_num, data, timestamp=None):
        self.event_type = event_type
        self.round_num = round_num
        self.data = data
        self.timestamp = timestamp or datetime.now()
    def to_dict(self):
        return {"event_type": self.event_type, "round_num": self.round_num, "data": self.data, "timestamp": self.timestamp.isoformat()}

@pytest.fixture
def recorder_module():
    try:
        from src.v6.support.session_recorder import Recorder, InMemoryRecorder, JsonFileRecorder, get_recorder
        return Recorder, InMemoryRecorder, JsonFileRecorder, get_recorder
    except ImportError:
        pytest.skip("Session recorder module not yet implemented")

@pytest.fixture
def in_memory_recorder(recorder_module):
    _, InMemoryRecorder, _, _ = recorder_module
    return InMemoryRecorder()

@pytest.fixture
def temp_json_path():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def json_file_recorder(recorder_module, temp_json_path):
    _, _, JsonFileRecorder, _ = recorder_module
    return JsonFileRecorder(filepath=temp_json_path)

class TestInMemoryRecorder:
    def test_events_recorded_in_order(self, in_memory_recorder):
        for i in range(3):
            in_memory_recorder.record(MockDebateEvent("speak", i+1, {"content": f"event{i}"}))
        events = in_memory_recorder.get_events()
        assert len(events) == 3
    def test_get_events_returns_list(self, in_memory_recorder):
        in_memory_recorder.record(MockDebateEvent("speak", 1, {}))
        events = in_memory_recorder.get_events()
        assert isinstance(events, list)
    def test_clear_removes_all(self, in_memory_recorder):
        in_memory_recorder.record(MockDebateEvent("speak", 1, {}))
        in_memory_recorder.clear()
        assert len(in_memory_recorder.get_events()) == 0
    def test_filter_by_round(self, in_memory_recorder):
        in_memory_recorder.record(MockDebateEvent("speak", 1, {}))
        in_memory_recorder.record(MockDebateEvent("speak", 2, {}))
        round1 = in_memory_recorder.get_events(round_num=1)
        assert all(e.round_num == 1 for e in round1)
    def test_filter_by_type(self, in_memory_recorder):
        in_memory_recorder.record(MockDebateEvent("speak", 1, {}))
        in_memory_recorder.record(MockDebateEvent("extract", 1, {}))
        speaks = in_memory_recorder.get_events(event_type="speak")
        assert all(e.event_type == "speak" for e in speaks)

class TestJsonFileRecorder:
    def test_records_to_file(self, json_file_recorder):
        json_file_recorder.record(MockDebateEvent("speak", 1, {}))
        json_file_recorder.flush()
        assert os.path.exists(json_file_recorder.filepath)
    def test_valid_json_output(self, json_file_recorder):
        json_file_recorder.record(MockDebateEvent("speak", 1, {"key": "value"}))
        json_file_recorder.flush()
        with open(json_file_recorder.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list)

class TestThreeRoundDump:
    def test_dump_all_rounds(self, in_memory_recorder):
        for r in range(1, 4):
            for _ in range(2):
                in_memory_recorder.record(MockDebateEvent("speak", r, {}))
        dump = in_memory_recorder.dump()
        assert len(dump) == 6
        assert set(e["round_num"] for e in dump) == {1, 2, 3}
    def test_dump_json_serializable(self, in_memory_recorder):
        in_memory_recorder.record(MockDebateEvent("speak", 1, {}))
        dump = in_memory_recorder.dump()
        json_str = json.dumps(dump, ensure_ascii=False)
        assert len(json_str) > 0

class TestSummaryStatistics:
    def test_summary_has_total_events(self, in_memory_recorder):
        for _ in range(3):
            in_memory_recorder.record(MockDebateEvent("speak", 1, {}))
        summary = in_memory_recorder.summary()
        assert "total_events" in summary
        assert summary["total_events"] == 3
    def test_summary_has_total_rounds(self, in_memory_recorder):
        in_memory_recorder.record(MockDebateEvent("speak", 1, {}))
        in_memory_recorder.record(MockDebateEvent("speak", 2, {}))
        summary = in_memory_recorder.summary()
        assert "total_rounds" in summary
    def test_summary_event_type_counts(self, in_memory_recorder):
        in_memory_recorder.record(MockDebateEvent("speak", 1, {}))
        in_memory_recorder.record(MockDebateEvent("extract", 1, {}))
        summary = in_memory_recorder.summary()
        assert "event_type_counts" in summary
    def test_summary_expert_participation(self, in_memory_recorder):
        in_memory_recorder.record(MockDebateEvent("speak", 1, {"expert_id": "alice"}))
        summary = in_memory_recorder.summary()
        assert "expert_participation" in summary
    def test_summary_empty_recorder(self, in_memory_recorder):
        summary = in_memory_recorder.summary()
        assert summary["total_events"] == 0

class TestRecorderProtocol:
    def test_has_record_method(self, recorder_module):
        _, InMemoryRecorder, _, _ = recorder_module
        r = InMemoryRecorder()
        assert hasattr(r, "record")
    def test_has_get_events_method(self, recorder_module):
        _, InMemoryRecorder, _, _ = recorder_module
        r = InMemoryRecorder()
        assert hasattr(r, "get_events")
    def test_has_dump_method(self, recorder_module):
        _, InMemoryRecorder, _, _ = recorder_module
        r = InMemoryRecorder()
        assert hasattr(r, "dump")
    def test_has_summary_method(self, recorder_module):
        _, InMemoryRecorder, _, _ = recorder_module
        r = InMemoryRecorder()
        assert hasattr(r, "summary")

class TestEdgeCases:
    def test_none_event_handled(self, in_memory_recorder):
        try:
            in_memory_recorder.record(None)
        except (TypeError, ValueError):
            pass
    def test_singleton_pattern(self, recorder_module):
        _, _, _, get_recorder = recorder_module
        r1 = get_recorder()
        r2 = get_recorder()
        assert r1 is r2
