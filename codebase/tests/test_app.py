from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from codebase.config import ROOT, Settings
from codebase.model_client import Completion
from codebase.tutor import fixed_response
from codebase.tests.fakes import routed_reply
from codebase.state import Check, TutorState


def button(app,label):
    return next(b for b in app.button if b.label==label)


def test_missing_key_is_honest_and_source_still_available():
    with patch('codebase.config.Settings.from_env',return_value=Settings()):
        app=AppTest.from_file(str(ROOT/'codebase/app.py')).run(timeout=20)
    assert not app.exception
    assert app.warning and app.chat_input[0].disabled
    assert len(app.selectbox[0].options)==29


def test_chat_rerun_does_not_duplicate_model_calls_and_reset_isolated():
    config=Settings(model='offline-test',api_key='fake-test-key')
    reply=fixed_response('diagnose','Bạn vướng ở model nền hay sản phẩm chatbot?', 'test_only')
    with patch('codebase.config.Settings.from_env',return_value=config), patch('codebase.model_client.ModelClient.complete',side_effect=routed_reply(reply)) as complete:
        app=AppTest.from_file(str(ROOT/'codebase/app.py')).run(timeout=20)
        app.chat_input[0].set_value('Không hiểu.').run()
        assert not app.exception and complete.call_count==2
        assert len(app.session_state['tutor_state'].messages)==2
        app.run()
        assert complete.call_count==2 and len(app.session_state['tutor_state'].messages)==2
        second=AppTest.from_file(str(ROOT/'codebase/app.py')).run(timeout=20)
        assert second.session_state['tutor_state'].messages==[]
        button(app,'Bắt đầu cuộc trò chuyện mới').click().run()
        assert app.session_state['tutor_state'].messages==[]


def test_context_correction_is_free_text_not_a_quick_action():
    with patch('codebase.config.Settings.from_env',return_value=Settings()):
        app=AppTest.from_file(str(ROOT/'codebase/app.py')).run(timeout=20)
    assert not any(b.label=='Sửa ngữ cảnh' for b in app.button)
    assert any(b.label=='Bắt đầu cuộc trò chuyện mới' for b in app.button)


def test_model_page_correction_updates_selector_and_no_stale_check():
    config=Settings(model='offline-test',api_key='fake-test-key')
    reply=fixed_response('correct_context','Mình chuyển sang trang token; bạn vướng ý nào?', 'correction')
    reply.corrected_page=13
    with patch('codebase.config.Settings.from_env',return_value=config),patch('codebase.model_client.ModelClient.complete',side_effect=routed_reply(reply)):
        app=AppTest.from_file(str(ROOT/'codebase/app.py')).run(timeout=20)
        app.chat_input[0].set_value('Ý mình là trang 13.').run()
        assert not app.exception
        assert app.selectbox[0].value==13
        assert app.session_state['tutor_state'].active_page==13


def test_help_button_leaves_check_without_skip_notice_or_routing_call():
    config=Settings(model='offline-test',api_key='fake-test-key')
    reply=fixed_response('diagnose','Bạn vướng ở model hay sản phẩm?', 'help')
    with patch('codebase.config.Settings.from_env',return_value=config),patch(
        'codebase.model_client.ModelClient.complete',side_effect=routed_reply(reply),
    ) as complete:
        app=AppTest.from_file(str(ROOT/'codebase/app.py')).run(timeout=20)
        app.session_state['tutor_state']=TutorState(pending_check=Check(question='Một model nhiều apps?',expected_concepts=['có']))
        app.run()
        button(app,'Mình chưa hiểu').click().run()
        assert not app.exception and complete.call_count==1
        state=app.session_state['tutor_state']
        assert state.pending_check is None and state.check_result=='unverified'
        assert not app.info
        assert not any('Đã bỏ qua' in c.value or 'chưa xác nhận' in c.value for c in app.caption)
        assert not any(b.label=='Bỏ qua kiểm tra' for b in app.button)
        assert not button(app,'Kiểm tra mức hiểu').disabled


def test_skip_button_only_appears_for_pending_check():
    with patch('codebase.config.Settings.from_env',return_value=Settings()):
        app=AppTest.from_file(str(ROOT/'codebase/app.py')).run(timeout=20)
        assert not any(b.label=='Bỏ qua kiểm tra' for b in app.button)
        app.session_state['tutor_state']=TutorState(
            pending_check=Check(question='Một model nhiều apps?',expected_concepts=['có']))
        app.run()
    assert not app.exception
    assert any(b.label=='Bỏ qua kiểm tra' for b in app.button)


def test_check_button_supplies_explicit_permission():
    # The model still needs evidence to produce the check; this verifies the UI intent.
    config=Settings(model='offline-test',api_key='fake-test-key')
    reply=fixed_response('diagnose','Bạn muốn kiểm tra model hay chatbot?', 'clarify')
    with patch('codebase.config.Settings.from_env',return_value=config),patch(
        'codebase.model_client.ModelClient.complete',side_effect=routed_reply(reply),
    ) as complete:
        app=AppTest.from_file(str(ROOT/'codebase/app.py')).run(timeout=20)
        button(app,'Kiểm tra mức hiểu').click().run()
        assert not app.exception and complete.call_count==1
        assert complete.call_args.args[1]['turn_policy']['new_check_allowed']
