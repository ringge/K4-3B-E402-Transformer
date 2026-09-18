from copy import deepcopy
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from codebase.config import ROOT, Settings
from codebase.model_client import Completion, ModelError
from codebase.tutor import fixed_response
from codebase.tests.fakes import routed_reply
from eval.run import read_cases


def run_button(app):
    return next(button for button in app.button if button.label == 'Chạy replay')


def test_replay_requires_configuration_but_shows_case():
    with patch('codebase.config.Settings.from_env', return_value=Settings()):
        app = AppTest.from_file(str(ROOT / 'codebase/pages/1_Replay_tests.py')).run()
    assert not app.exception
    assert len(app.selectbox[0].options) == 24
    assert run_button(app).disabled
    assert app.warning


def test_replay_uses_saved_state_and_history_and_restarts_each_run():
    case = next(c for c in read_cases() if c['id'] == 'GS-009')
    config = Settings(model='offline-test', api_key='fake-test-key')
    reply = fixed_response('diagnose', 'Bạn có thể nói rõ ý này không?', 'test_only')
    with patch('codebase.config.Settings.from_env', return_value=config), patch(
        'codebase.model_client.ModelClient.complete',
        side_effect=routed_reply(reply, 'check_answer'),
    ) as complete:
        app = AppTest.from_file(str(ROOT / 'codebase/pages/1_Replay_tests.py')).run()
        app.selectbox[0].select('GS-009').run()
        assert complete.call_count == 0
        run_button(app).click().run()
        assert not app.exception and complete.call_count == 2
        payload = complete.call_args.args[1]
        assert payload['user_input'] == case['input']
        assert payload['state']['pending_check'] == case['initial_state']['pending_check']
        assert [(m['role'], m['content']) for m in payload['history']] == [
            (m['role'], m['content']) for m in case['history']]
        assert 'expected' not in payload
        original = deepcopy(payload)
        app.run()
        assert complete.call_count == 2
        run_button(app).click().run()
        assert complete.call_count == 4
        assert complete.call_args.args[1] == original
        app.selectbox[0].select('GS-001').run()
        assert not any('Kết quả thực tế' in header.value for header in app.subheader)


def test_page_switch_preserves_live_chat_and_controls():
    config = Settings(model='offline-test', api_key='fake-test-key')
    reply = fixed_response('diagnose', 'Bạn vướng ở khái niệm nào?', 'test_only')
    with patch('codebase.config.Settings.from_env', return_value=config), patch(
        'codebase.model_client.ModelClient.complete',
        side_effect=routed_reply(reply),
    ) as complete:
        app = AppTest.from_file(str(ROOT / 'codebase/app.py')).run()
        app.selectbox[0].select(13).run()
        app.chat_input[0].set_value('Không hiểu.').run()
        app.checkbox[0].check().run()
        live_state = app.session_state['tutor_state'].model_dump()
        traces = deepcopy(app.session_state['traces'])
        app.switch_page('pages/1_Replay_tests.py').run()
        run_button(app).click().run()
        assert not app.exception
        assert app.session_state['tutor_state'].model_dump() == live_state
        assert app.session_state['traces'] == traces
        app.switch_page('app.py').run()
        assert not app.exception
        assert app.selectbox[0].value == 13
        assert app.checkbox[0].value is True
        assert app.session_state['tutor_state'].model_dump() == live_state
        assert complete.call_count == 4


def test_provider_error_is_displayed_and_retry_is_explicit():
    config = Settings(model='offline-test', api_key='fake-test-key')
    with patch('codebase.config.Settings.from_env', return_value=config), patch(
        'codebase.model_client.ModelClient.complete', side_effect=ModelError('network_error'),
    ) as complete:
        app = AppTest.from_file(str(ROOT / 'codebase/pages/1_Replay_tests.py')).run()
        run_button(app).click().run()
        assert not app.exception and app.error
        calls = complete.call_count
        app.run()
        assert complete.call_count == calls
        record = app.session_state['replay_results']['GS-001']['record']
        assert not record['auto']['pass']
        run_button(app).click().run()
        assert complete.call_count > calls
