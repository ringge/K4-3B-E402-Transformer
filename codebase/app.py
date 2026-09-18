"""Run from the repository root: streamlit run codebase/app.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st

from codebase.config import Settings
from codebase.knowledge import Knowledge
from codebase.model_client import ModelClient
from codebase.state import TutorState
from codebase.tutor import Tutor

st.set_page_config(page_title='VLearn · Hiểu từng ý', page_icon='🌱', layout='wide')
st.markdown('''<style>
.block-container {max-width:1200px;padding-top:3.5rem}
[data-testid="stSidebar"] {background:#f3f7f5}
[data-testid="stChatMessage"] {border:1px solid #e2e9e5;border-radius:16px}
h1 {letter-spacing:-.04em} .scope {color:#60716a;font-size:.95rem;margin-bottom:1rem}
</style>''', unsafe_allow_html=True)


@st.cache_resource
def load_source(path, modified):
    return Knowledge(Path(path))


try:
    settings = Settings.from_env()
    knowledge = load_source(str(settings.source_path), settings.source_path.stat().st_mtime_ns)
except (OSError, ValueError):
    st.error('Chưa đọc được nguồn/cấu hình. Đặt bộ HTML 29 trang tại data/d1-slide-hackathon.html và kiểm tra .env theo README.')
    st.stop()

if 'tutor_state' not in st.session_state:
    st.session_state.tutor_state = TutorState()
    st.session_state.traces = []
    st.session_state.failed_input = None

# Widget keys are cleaned up when visiting another Streamlit page. Keep the
# live controls separately so a replay visit cannot change the live context.
for key, default in [('page', 10), ('quiz', False)]:
    if key not in st.session_state:
        st.session_state[key] = st.session_state.get('live_' + key, default)

if 'page_next' in st.session_state:
    st.session_state.page = st.session_state.pop('page_next')


def start_new_chat():
    st.session_state.tutor_state = TutorState(active_page=st.session_state.get('page', 10))
    st.session_state.traces = []
    st.session_state.failed_input = None


with st.sidebar:
    st.caption('VLEARN / AI IN ACTION')
    st.header('Bài học của bạn')
    page = st.selectbox('Day 1 · AI & LLM Foundation', list(range(1, 30)), index=None,
                        format_func=lambda n: f'{n:02} · {knowledge.page(n).title}', key='page')
    st.caption('Nguồn duy nhất: bộ slide Day 1 · 29 trang')
    st.markdown('---')
    st.subheader(knowledge.page(page).title)
    for warning in knowledge.page(page).evidence()['warnings']:
        st.warning(warning)
    st.text(knowledge.page(page).text)
    quiz = st.checkbox('Tôi đang làm quiz', key='quiz')
    st.session_state.live_page = page
    st.session_state.live_quiz = quiz
    st.caption('Khi bật, tutor không cung cấp đáp án. Bỏ chọn khi đã kết thúc quiz để ôn bài.')
    st.button('Bắt đầu cuộc trò chuyện mới', on_click=start_new_chat, use_container_width=True)
    st.caption('Hội thoại chỉ ở phiên hiện tại. Tải lại hoặc mở phiên mới có thể làm mất lịch sử.')

st.caption('GIA SƯ DAY 1')
st.title('Hiểu từng ý, tiến từng bước.')
st.markdown('<div class="scope">Hỏi về bài đang học. Nếu chưa hiểu, mình sẽ cùng bạn tìm đúng chỗ vướng.</div>', unsafe_allow_html=True)
config_error = settings.configuration_error()
if config_error:
    st.warning(config_error + ' Xem hướng dẫn trong codebase/README.md. Đây chưa phải một cuộc trò chuyện AI đang chạy.')
else:
    st.caption('AI trả lời trực tiếp · có thể sai · hãy mở nguồn để kiểm tra')

state = st.session_state.tutor_state
if not state.messages:
    with st.chat_message('assistant'):
        st.write('Chào bạn! Mình chỉ dựa vào bộ slide Day 1. Bạn có thể bắt đầu với “LLM khác chatbot thế nào?”. Khi một ý chưa rõ, cứ nói “Mình chưa hiểu”.')

for message in state.messages:
    with st.chat_message(message.role):
        st.markdown(message.content)
        for source_id in message.source_ids:
            source = knowledge.pages[source_id]
            with st.expander(f'Day 1 · trang {source.file_page} — {source.title}'):
                st.text(source.text)

if state.check_result == 'correct':
    st.success('Câu trả lời vừa kiểm tra đúng với ý chính của bài. Đây chưa phải đánh giá toàn bộ mức hiểu.')
elif state.check_result == 'skipped':
    st.caption('Đã bỏ qua câu kiểm tra.')
elif state.pending_check:
    st.caption('Bạn có thể trả lời câu kiểm tra, hỏi thêm hoặc bỏ qua.')

buttons = st.columns(4)
requested = None
for col, label, text, intent in [
    (buttons[0], 'Mình chưa hiểu', 'Mình chưa hiểu.', 'help'),
    (buttons[1], 'Cho ví dụ', 'Cho mình một ví dụ minh hoạ dễ hiểu cho ý vừa nói.', 'example'),
    (buttons[2], 'Tự kiểm tra', 'Cho mình một câu hỏi để tự kiểm tra mức hiểu về ý vừa học.', 'check'),
    (buttons[3], 'Bỏ qua kiểm tra', 'Bỏ qua kiểm tra.', 'skip'),
]:
    if col.button(label, use_container_width=True, disabled=bool(config_error) or (intent == 'skip' and state.pending_check is None)):
        requested = (text, intent)

with st.expander('Soạn câu hỏi để mang đến TA'):
    st.text_area('Bản nháp — chưa gửi', value=f'Mình đang học Day 1, trang {page}: {knowledge.page(page).title}.\n'
                 f'Chỗ mình còn vướng: {state.hypothesized_gap or "[điền ý chưa rõ]"}.\n'
                 'Mình đã thử đọc giải thích và vẫn cần một ví dụ/giải thích khác.', height=130)

if st.session_state.failed_input:
    st.error(st.session_state.failed_input['error'])
    if st.button('Thử lại câu vừa gửi', disabled=bool(config_error)):
        requested = (st.session_state.failed_input['text'], st.session_state.failed_input['intent'])
    st.caption('Câu chưa xử lý: ' + st.session_state.failed_input['text'])

typed = st.chat_input('Bạn đang vướng ở ý nào?', max_chars=4000, disabled=bool(config_error))
if typed:
    requested = (typed, 'chat')
if requested:
    text, intent = requested
    state = state.model_copy(deep=True)
    state.quiz_status = quiz
    with st.spinner('Đang đọc bài và tìm cách giải thích…'):
        result = Tutor(knowledge, ModelClient(settings)).step(state, text, selected_page=page, intent=intent)
    st.session_state.traces.append(result.trace)
    if result.error:
        st.session_state.failed_input = {'text': text, 'intent': intent, 'error': result.error}
    else:
        st.session_state.tutor_state = result.state
        if result.state.active_page is not None and result.state.active_page != page:
            st.session_state.page_next = result.state.active_page
        st.session_state.failed_input = None
    st.rerun()

with st.expander('Thông tin kiểm thử dành cho nhóm'):
    st.caption('Không lưu hội thoại tự động xuống đĩa. Không chứa API key hoặc suy nghĩ nội bộ.')
    st.write({'model': settings.model or 'chưa cấu hình', 'provider': settings.provider,
              'diagnostic_count': state.diagnostic_count, 'repair_count': state.repair_count,
              'check_result': state.check_result})
    if st.session_state.traces:
        trace = st.session_state.traces[-1]
        st.json({k: trace.get(k) for k in ['status', 'latency_ms', 'retrieved_ids', 'guard']})
