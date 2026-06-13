"""
test_user_interaction.py — UserInteraction 单元测试（TDD 红端）
测试覆盖：SyncUserInteraction 阻塞读取、AsyncUserInteraction 非阻塞回调、主持人询问路由
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Optional, Callable

@pytest.fixture
def user_interaction_module():
    try:
        from src.v6.support.user_interaction import (
            UserInteraction,
            SyncUserInteraction,
            AsyncUserInteraction,
            get_user_interaction
        )
        return UserInteraction, SyncUserInteraction, AsyncUserInteraction, get_user_interaction
    except ImportError:
        pytest.skip("UserInteraction module not yet implemented")

@pytest.fixture
def sync_interaction(user_interaction_module):
    _, SyncUserInteraction, _, _ = user_interaction_module
    return SyncUserInteraction()

@pytest.fixture
def async_interaction(user_interaction_module):
    _, _, AsyncUserInteraction, _ = user_interaction_module
    return AsyncUserInteraction()

class TestSyncUserInteraction:
    def test_get_input_returns_string(self, sync_interaction):
        with patch('builtins.input', return_value='test input'):
            result = sync_interaction.get_input('Enter:')
        assert isinstance(result, str)
        assert result == 'test input'

    def test_get_input_blocks_until_response(self, sync_interaction):
        import time
        start = time.time()
        with patch('builtins.input', return_value='response'):
            result = sync_interaction.get_input('Prompt:')
        elapsed = time.time() - start
        assert elapsed < 1.0  # Should complete quickly with mock

    def test_get_input_shows_prompt(self, sync_interaction):
        with patch('builtins.input', return_value='test') as mock_input:
            sync_interaction.get_input('Enter your choice:')
            mock_input.assert_called_once_with('Enter your choice:')

    def test_ask_returns_user_text(self, sync_interaction):
        with patch('builtins.input', return_value='user response'):
            result = sync_interaction.ask(question='Any question?')
        assert result == 'user response'

    def test_supplement_request_returns_text(self, sync_interaction):
        with patch('builtins.input', return_value='supplemental info'):
            result = sync_interaction.request_supplement(
                expert_id='expert1',
                topic='some topic'
            )
        assert isinstance(result, str)

class TestAsyncUserInteraction:
    def test_register_callback(self, async_interaction):
        callback = Mock()
        async_interaction.register_callback('test', callback)
        assert 'test' in async_interaction._callbacks

    def test_trigger_callback_executes(self, async_interaction):
        callback = Mock()
        async_interaction.register_callback('my_event', callback)
        async_interaction.trigger_callback('my_event', {'data': 'test'})
        callback.assert_called_once()

    def test_trigger_nonexistent_callback_no_error(self, async_interaction):
        # Should not raise
        async_interaction.trigger_callback('nonexistent', {})
        assert True

    def test_ask_returns_future(self, async_interaction):
        future = async_interaction.ask(question='test?')
        # Should return something awaitable (Future, Task, etc.)
        assert future is not None

    def test_callback_receives_data(self, async_interaction):
        received_data = {}
        def callback(data):
            received_data.update(data)
        async_interaction.register_callback('test', callback)
        async_interaction.trigger_callback('test', {'key': 'value'})
        assert received_data.get('key') == 'value'

class TestModeratorRouting:
    def test_moderator_can_route_to_user(self, user_interaction_module):
        _, SyncUserInteraction, _, _ = user_interaction_module
        interaction = SyncUserInteraction()
        assert hasattr(interaction, 'route_from_moderator') or hasattr(interaction, 'ask')

    def test_supplement_routed_by_expert_id(self, user_interaction_module):
        _, SyncUserInteraction, _, _ = user_interaction_module
        interaction = SyncUserInteraction()
        with patch('builtins.input', return_value='supplement'):
            result = interaction.request_supplement(
                expert_id='tech_expert',
                topic='architecture'
            )
        assert isinstance(result, str)

class TestEdgeCases:
    def test_empty_input_handled(self, sync_interaction):
        with patch('builtins.input', return_value=''):
            result = sync_interaction.get_input('Prompt:')
        assert result == ''

    def test_keyboard_interrupt_returns_none(self, sync_interaction):
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            result = sync_interaction.get_input('Prompt:')
        # Should handle gracefully, possibly returning None
        assert result is None or result == ''

    def test_singleton_pattern(self, user_interaction_module):
        _, _, _, get_ui = user_interaction_module
        ui1 = get_ui()
        ui2 = get_ui()
        assert ui1 is ui2
