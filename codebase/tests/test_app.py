from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from codebase.config import ROOT, Settings
from codebase.model_client import Completion
from codebase.tutor import fixed_response


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
    with patch('codebase.config.Settings.from_env',return_value=config), patch('codebase.model_client.ModelClient.complete',return_value=Completion(reply.model_dump_json(),{})) as complete:
        app=AppTest.from_file(str(ROOT/'codebase/app.py')).run(timeout=20)
        app.chat_input[0].set_value('Không hiểu.').run()
        assert not app.exception and complete.call_count==1
        assert len(app.session_state['tutor_state'].messages)==2
        app.run()
        assert complete.call_count==1 and len(app.session_state['tutor_state'].messages)==2
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
    with patch('codebase.config.Settings.from_env',return_value=config),patch('codebase.model_client.ModelClient.complete',return_value=Completion(reply.model_dump_json(),{})):
        app=AppTest.from_file(str(ROOT/'codebase/app.py')).run(timeout=20)
        app.chat_input[0].set_value('Ý mình là trang 13.').run()
        assert not app.exception
        assert app.selectbox[0].value==13
        assert app.session_state['tutor_state'].active_page==13
