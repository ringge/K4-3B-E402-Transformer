"""Run one golden replay without touching the live learner session."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import streamlit as st

from codebase.config import Settings
from codebase.knowledge import Knowledge
from codebase.model_client import ModelClient
from codebase.state import TutorState
from codebase.tutor import Tutor
from eval.run import evaluate_case, read_cases

st.set_page_config(page_title='VLearn · Replay tests', page_icon='🧪', layout='wide')
st.title('Replay tests')
st.caption('Dành cho nhóm kiểm thử · Live chat vẫn ở trang app trong thanh bên.')
st.info('Lịch sử bên dưới được nạp sẵn từ golden case. Chỉ lượt trả lời cho input kiểm thử '
        'được chạy mới. Mỗi lần chạy bắt đầu lại từ trạng thái gốc của case.')

try:
    cases = read_cases()
    if not cases:
        raise ValueError('Empty case set')
    for item in cases:
        TutorState.model_validate({**item['initial_state'], 'messages': item['history']})
        assert item['id'] and item['input'] and item['expected']['allowed_actions']
except (OSError, ValueError, KeyError, TypeError, AssertionError):
    st.error('Không đọc được bộ case hợp lệ từ eval/golden.json.')
    st.stop()

by_id = {case['id']: case for case in cases}
saved_id = st.session_state.get('replay_selected', cases[0]['id'])
if 'replay_case' not in st.session_state:
    st.session_state.replay_case = saved_id if saved_id in by_id else cases[0]['id']
case_id = st.selectbox('Chọn golden case', list(by_id), key='replay_case',
                       format_func=lambda value: f"{value} · {by_id[value]['name']}")
st.session_state.replay_selected = case_id
case = by_id[case_id]
st.caption(f"Trạng thái case: {case.get('status', 'chưa khai báo')}")

setup, expected = st.columns(2)
with setup:
    st.subheader('Bối cảnh nạp sẵn')
    if not case['history']:
        st.caption('Case bắt đầu với lịch sử trống.')
    for message in case['history']:
        with st.chat_message(message['role']):
            st.caption('Lịch sử nạp sẵn — không phải output của lần chạy này')
            st.write(message['content'])
    with st.expander('Trạng thái ban đầu'):
        st.json(case['initial_state'])
    st.subheader('Input kiểm thử')
    st.write(case['input'])
    st.caption('Intent: ' + case.get('intent', 'chat'))
with expected:
    st.subheader('Hành vi mong đợi')
    st.write('Hành động cho phép: ' + ', '.join(case['expected']['allowed_actions']))
    for field, title in [('must', 'Phải có'), ('must_not', 'Không được')]:
        st.markdown(f'**{title}**')
        for rule in case['expected'].get(field, []):
            st.write('• ' + rule)
    st.caption('Các tiêu chí này chỉ để đối chiếu, không được gửi vào prompt tutor.')

settings = None
knowledge = None
try:
    settings = Settings.from_env()
    knowledge = Knowledge(settings.source_path)
    config_error = settings.configuration_error()
except (OSError, ValueError):
    config_error = 'Chưa đọc được nguồn/cấu hình. Kiểm tra .env và bộ slide Day 1.'
if config_error:
    st.warning(config_error)

if st.button('Chạy replay', type='primary', disabled=bool(config_error)):
    with st.spinner('Đang chạy input trên bối cảnh đã lưu…'):
        record = evaluate_case(case, None, Tutor(knowledge, ModelClient(settings)), False)[0]
    st.session_state.setdefault('replay_results', {})[case_id] = {
        'case': case, 'record': record,
    }

saved = st.session_state.get('replay_results', {}).get(case_id)
if saved:
    if saved['case'] != case:
        st.warning('Case đã thay đổi từ lần chạy trước. Chạy lại để đối chiếu với bản hiện tại.')
    record = saved['record']
    st.divider()
    st.subheader('Kết quả thực tế · ' + case_id)
    st.caption('Lần chạy: ' + record['trace'].get('timestamp', ''))
    if 'provider_or_validation_error' in record['auto']['failures']:
        st.error(record['displayed'])
    else:
        with st.chat_message('assistant'):
            st.write(record['displayed'])
        response = record['trace'].get('response', {})
        st.write('Hành động thực tế: ' + response.get('action', ''))
        for source_id in response.get('source_ids', []):
            if knowledge and source_id in knowledge.pages:
                with st.expander('Nguồn · ' + source_id):
                    st.text(knowledge.pages[source_id].text)
    st.write('Kiểm tra tự động: ' + ('đạt' if record['auto']['pass'] else 'không đạt'))
    st.caption('Đây là kiểm tra cấu trúc/hành động. Nhóm vẫn cần đọc và chấm chất lượng '
               'theo các tiêu chí; đây chưa phải kết quả quality bar hay live rollout.')
    with st.expander('Chi tiết kiểm tra và trace'):
        st.json(record)
    st.download_button('Tải kết quả JSON', json.dumps(saved, ensure_ascii=False, indent=2),
                       file_name=f'{case_id}-replay.json', mime='application/json')
    st.caption('Giữ lần chạy gần nhất của mỗi case trong phiên này. Tải JSON để lưu bằng chứng; '
               'trang này không ghi vào eval/runs hoặc thay đổi golden set.')
