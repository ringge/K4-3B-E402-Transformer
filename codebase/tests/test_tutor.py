from copy import deepcopy
import json

import httpx
import pytest

from codebase.config import ROOT, Settings
from codebase.knowledge import Knowledge
from codebase.model_client import Completion, ModelClient, ModelError
from codebase.state import Check, Message, TutorResponse, TutorState
from codebase.tutor import Tutor, fixed_response


@pytest.fixture
def knowledge():
    return Knowledge(ROOT/'data/d1-slide-hackathon.html')


class FakeClient:
    def __init__(self, responses):
        self.responses=iter(responses);self.calls=[]

    def complete(self, system, payload):
        self.calls.append(deepcopy(payload))
        value=next(self.responses)
        if isinstance(value,Exception): raise value
        return Completion(value.model_dump_json() if isinstance(value,TutorResponse) else value,{},'offline-test')


def grounded(knowledge, action='explain_and_check'):
    page=knowledge.page(10)
    block=next(b for b in page.evidence()['blocks'] if b['text'].startswith('Chatbot chỉ'))
    return TutorResponse(action=action,evidence_status='supported',reply='Chatbot là một dạng sản phẩm dùng model nền.',
                         source_ids=['D1-P010'],claims=[{'claim':'Chatbot là sản phẩm','block_id':block['id'],'quote':block['text']}],
                         gap_hypothesis='model và sản phẩm',check=Check(question='Một model có thể phục vụ nhiều ứng dụng không?',expected_concepts=['có']) if action in {'explain_and_check','repair_and_check'} else None,
                         check_assessment='incorrect' if action=='repair_and_check' else 'not_applicable',
                         corrected_page=None,representation='đối chiếu',reason_code='specific_gap')


def test_pages_and_table_preserved(knowledge):
    assert len(knowledge.pages)==29
    assert [p.anchor for p in knowledge.pages.values()]==[f'p{i}' for i in range(1,30)]
    assert 'LLM là gì' in knowledge.page(10).title
    assert any('22%' in block and 'land' in block for block in knowledge.page(11).blocks)
    assert 'deck-toolbar' not in knowledge.page(10).text


def test_new_topic_retrieval_not_trapped_on_selected_page(knowledge):
    pages=knowledge.retrieve('Token có bằng một từ không?',active_page=10)
    assert 'D1-P013' in {p.source_id for p in pages}


def test_vague_followup_keeps_active_source(knowledge):
    assert knowledge.retrieve('Không hiểu.',14,'context')[0].source_id=='D1-P014'


def test_diagnosis_does_not_reset_and_budget_stops_loop(knowledge):
    probe=fixed_response('diagnose','Bạn vướng ở khái niệm model hay sản phẩm?', 'vague')
    client=FakeClient([probe])
    result=Tutor(knowledge,client).step(TutorState(diagnostic_count=2),'Vẫn chưa hiểu.')
    assert result.response.action=='fallback'
    assert result.state.diagnostic_count==2
    assert result.trace['guard']=='attempt_budget_exhausted'


def test_clear_gap_proceeds_after_two_probes(knowledge):
    result=Tutor(knowledge,FakeClient([grounded(knowledge)])).step(TutorState(diagnostic_count=2),'Mình tưởng LLM là chatbot.')
    assert result.response.action=='explain_and_check'
    assert result.state.pending_check and result.state.check_result=='unverified'


def test_second_repair_stops(knowledge):
    state=TutorState(repair_count=1,pending_check=Check(question='Một model, nhiều app?',expected_concepts=['có']))
    result=Tutor(knowledge,FakeClient([grounded(knowledge,'repair_and_check')])).step(state,'Không, chỉ một app.')
    assert result.response.action=='fallback'
    assert result.state.pending_check is None
    assert result.state.repair_count==1


def test_skip_never_verifies_and_uses_no_model(knowledge):
    client=FakeClient([])
    state=TutorState(pending_check=Check(question='Có không?',expected_concepts=['có']))
    result=Tutor(knowledge,client).step(state,'Bỏ qua kiểm tra.')
    assert result.state.check_result=='skipped' and result.state.pending_check is None
    assert client.calls==[]


def test_correction_clears_check_preserves_budgets(knowledge):
    state=TutorState(check_result='correct',diagnostic_count=1,repair_count=1,
                     pending_check=Check(question='Câu cũ?',expected_concepts=['cũ']))
    result=Tutor(knowledge,FakeClient([])).step(state,'Sửa trang',selected_page=13,intent='correct')
    assert result.state.active_page==13 and result.state.check_result=='unverified'
    assert result.state.pending_check is None
    assert (result.state.diagnostic_count,result.state.repair_count)==(1,1)
    assert state.check_result=='correct'  # input object is not mutated


@pytest.mark.parametrize('quiz,text',[(True,'Giải thích giúp'),(False,'Mình đang làm quiz, cho đáp án.')])
def test_quiz_boundary_no_answer_no_citations(knowledge,quiz,text):
    result=Tutor(knowledge,FakeClient([])).step(TutorState(quiz_status=quiz),text)
    assert result.response.action=='quiz_redirect'
    assert result.response.source_ids==[] and result.response.claims==[]


def test_false_understanding_from_ok_rejected(knowledge):
    response=grounded(knowledge,'feedback');response.check_assessment='correct'
    state=TutorState(pending_check=Check(question='Vì sao?',expected_concepts=['one model many apps']))
    result=Tutor(knowledge,FakeClient([response,response])).step(state,'Ok hiểu rồi')
    assert result.error and result.state==state
    assert all(a['error']=='unearned_understanding' for a in result.trace['attempts'])


def test_correct_check_is_only_verification_route(knowledge):
    response=grounded(knowledge,'feedback');response.check_assessment='correct'
    state=TutorState(pending_check=Check(question='Vì sao?',expected_concepts=['one model many apps']))
    result=Tutor(knowledge,FakeClient([response,json.dumps({'verdict':'correct','learner_quote':'Một model nền phục vụ nhiều ứng dụng khác nhau.'})])).step(state,'Một model nền phục vụ nhiều ứng dụng khác nhau.')
    assert result.state.check_result=='correct' and result.state.pending_check is None


@pytest.mark.parametrize('mutation,code',[
    (lambda r:setattr(r,'source_ids',['D1-P099']),'citation_not_supplied'),
    (lambda r:setattr(r.claims[0],'quote','một câu không có trong slide'),'quote_not_in_source'),
    (lambda r:setattr(r,'claims',[]),'teaching_without_evidence'),
])
def test_invalid_evidence_never_displayed(knowledge,mutation,code):
    response=grounded(knowledge);mutation(response)
    state=TutorState()
    result=Tutor(knowledge,FakeClient([response,response])).step(state,'LLM là chatbot hả?')
    assert result.error and result.response is None and result.state==state
    assert result.trace['attempts'][0]['error']==code


def test_provider_error_keeps_exact_state_and_retry_is_bounded(knowledge):
    state=TutorState(messages=[Message(role='user',content='LLM?')])
    client=FakeClient([ModelError('provider_timeout',True),ModelError('provider_timeout',True)])
    result=Tutor(knowledge,client).step(state,'Không hiểu.',selected_page=13)
    assert result.state==state and len(client.calls)==2
    assert result.trace['status']=='error'


def test_one_schema_retry_and_no_duplicate_messages(knowledge):
    client=FakeClient(['{bad json',grounded(knowledge)])
    result=Tutor(knowledge,client).step(TutorState(),'Mình tưởng LLM là chatbot.')
    assert len(result.state.messages)==2 and len(client.calls)==2
    assert 'validation_feedback' in client.calls[1]
    assert all('expected' not in p and 'golden' not in p for p in client.calls)


def test_selected_page_change_invalidates_check_before_model(knowledge):
    response=fixed_response('diagnose','Bạn vướng chỗ token hay từ?', 'clarify')
    client=FakeClient([response])
    state=TutorState(pending_check=Check(question='Cũ?',expected_concepts=['cũ']),check_result='correct')
    Tutor(knowledge,client).step(state,'Chưa rõ',selected_page=13)
    assert client.calls[0]['state']['pending_check'] is None
    assert client.calls[0]['state']['check_result']=='unverified'


def test_compatible_wire_format_and_no_key_in_public_config():
    settings=Settings(model='test-model',api_key='test-secret',base_url='https://example.test/v1')
    def respond(request):
        assert request.headers['Authorization']=='Bearer test-secret'
        body=json.loads(request.content)
        assert body['model']=='test-model' and body['response_format']['type']=='json_object'
        assert request.url.path=='/v1/chat/completions'
        return httpx.Response(200,json={'choices':[{'finish_reason':'stop','message':{'content':'{}'}}], 'usage':{'total_tokens':4}})
    c=ModelClient(settings,httpx.MockTransport(respond)).complete('Return JSON',{'input':'hello'})
    assert c.text=='{}' and c.usage['total_tokens']==4
    assert 'secret' not in json.dumps(settings.public())


def test_http_error_never_exposes_provider_body():
    settings=Settings(model='x',api_key='secret')
    client=ModelClient(settings,httpx.MockTransport(lambda r:httpx.Response(401,text='secret-key-leak')))
    with pytest.raises(ModelError) as e: client.complete('JSON',{})
    assert str(e.value)=='provider_http_401' and not e.value.retryable


def test_model_cannot_feedback_without_pending_check(knowledge):
    response=grounded(knowledge,'feedback');response.check_assessment='correct'
    result=Tutor(knowledge,FakeClient([response,response])).step(TutorState(),'Có, nhiều ứng dụng.')
    assert result.error and result.state.check_result=='unverified'


def test_abstention_can_cite_supported_scope_without_teaching_missing_topic(knowledge):
    response=grounded(knowledge,'answer')
    response.action='abstain';response.evidence_status='unsupported'
    response.reply='Bài có nói chatbot là sản phẩm quanh model nền; không đủ nội dung MCP để giải thích.'
    result=Tutor(knowledge,FakeClient([response])).step(TutorState(),'Giảng MCP giúp mình.')
    assert result.error is None and result.response.action=='abstain'


def test_flagged_source_is_visible_but_not_available_as_evidence(knowledge):
    assert 'Đây chính là chữ T trong GPT' in knowledge.page(15).text
    assert 'D1-P015-B006' not in knowledge.block_map
    assert knowledge.page(15).evidence()['warnings']


def test_openai_aliases_host_normalization_and_key_redaction(monkeypatch):
    import codebase.config as config
    for key in ['TUTOR_PROVIDER','TUTOR_BASE_URL','TUTOR_MODEL','TUTOR_API_KEY','OPENAI_BASE_URL','OPENAI_MODEL','OPENAI_API_KEY']:
        monkeypatch.delenv(key,raising=False)
    monkeypatch.setattr(config,'dotenv_values',lambda p:{'OPENAI_BASE_URL':'https://example.test','OPENAI_MODEL':'test','OPENAI_API_KEY':'fake'})
    s=Settings.from_env()
    assert s.base_url=='https://example.test/v1' and s.model=='test'
    assert s.configuration_error() is None and 'fake' not in json.dumps(s.public())


def test_new_explanation_cannot_bypass_pending_check_repair_budget(knowledge):
    response=grounded(knowledge)
    state=TutorState(repair_count=1,pending_check=Check(question='Cũ?',expected_concepts=['nhiều apps']))
    result=Tutor(knowledge,FakeClient([response,response])).step(state,'Không, chỉ một chatbot.')
    assert result.error and result.state==state
    assert result.trace['attempts'][0]['error']=='pending_check_requires_assessment'


def test_one_check_can_ask_for_a_justification(knowledge):
    response=grounded(knowledge)
    response.check.question='Một model phục vụ nhiều ứng dụng được không? Vì sao?'
    result=Tutor(knowledge,FakeClient([response])).step(TutorState(),'Mình tưởng model là chatbot.')
    assert result.error is None


def test_false_positive_correct_is_blocked_by_focused_verifier(knowledge):
    response=grounded(knowledge,'feedback');response.check_assessment='correct'
    state=TutorState(pending_check=Check(question='Một model nhiều apps?',expected_concepts=['có']))
    client=FakeClient([response,json.dumps({'verdict':'incorrect','learner_quote':'chỉ một chatbot'})])
    result=Tutor(knowledge,client).step(state,'Không, chỉ một chatbot.')
    assert result.response.action=='fallback' and result.state.check_result=='unverified'
    assert result.trace['guard']=='understanding_not_verified' and len(client.calls)==2


def test_verifier_cannot_quote_teacher_instead_of_student(knowledge):
    response=grounded(knowledge,'feedback');response.check_assessment='correct'
    state=TutorState(pending_check=Check(question='Một model nhiều apps?',expected_concepts=['có']))
    client=FakeClient([response,json.dumps({'verdict':'correct','learner_quote':'model phục vụ nhiều ứng dụng'})])
    result=Tutor(knowledge,client).step(state,'Không, chỉ một chatbot.')
    assert result.state.check_result=='unverified' and result.trace['guard']=='understanding_not_verified'


def test_correct_after_schema_retry_cannot_exceed_two_call_budget(knowledge):
    response=grounded(knowledge,'feedback');response.check_assessment='correct'
    state=TutorState(pending_check=Check(question='Một model nhiều apps?',expected_concepts=['có']))
    client=FakeClient(['invalid json',response])
    result=Tutor(knowledge,client).step(state,'Có, một model có thể phục vụ nhiều ứng dụng.')
    assert len(client.calls)==2 and result.state.check_result=='unverified'
