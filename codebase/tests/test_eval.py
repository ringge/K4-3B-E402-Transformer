import json
from copy import deepcopy
import pytest

from codebase.config import ROOT
from codebase.knowledge import Knowledge
from eval.run import check_suite,read_cases
from eval.grade import aggregate,load_reviews


def test_case_coverage_and_provenance():
    report=check_suite(read_cases(),Knowledge(ROOT/'data/d1-slide-hackathon.html'))
    assert report['real_derived']>=10 and report['with_history']>=18


def test_rollouts_are_actual_user_scripts_not_golden_assistant_injection():
    scripts=json.loads((ROOT/'eval/rollout-scripts.json').read_text())
    assert len(scripts)==6
    for script in scripts.values():
        assert len(script['steps'])>=2
        for turn in script['steps']:
            assert 'assistant' not in turn and turn['input'] and turn['allowed_actions']


def test_eval_reserved_cases_not_part_of_pilot():
    reserved={c['id'] for c in read_cases() if c['reserved_from_pilot']}
    assert len(reserved)>=5


@pytest.fixture
def simulated_run(tmp_path):
    # Synthetic scorer unit fixture only; never written to eval/runs or presented as AI scores.
    cases=read_cases()
    scripts=json.loads((ROOT/'eval/rollout-scripts.json').read_text())
    records=[];reviews={}
    for c in cases:
        modes=[('replay',1)]
        if c['rollout_required']:modes += [('rollout',i) for i in range(1,len(scripts[c['id']]['steps'])+1)]
        for mode,step in modes:
            r={'case_id':c['id'],'mode':mode,'step':step,'auto':{'pass':True}}
            records.append(r)
            reviews[(c['id'],mode,step)]={'factuality':'pass','relevance':'pass','sensitivity':'pass','critical_violation':'none','branch_fits':'pass'}
    (tmp_path/'outputs.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
    (tmp_path/'cases.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cases))
    (tmp_path/'manifest.json').write_text(json.dumps({'case_ids':[c['id'] for c in cases],'phase':'exploratory','complete':True,'rollouts_requested':True}))
    (tmp_path/'quality-bar.json').write_bytes((ROOT/'eval/quality-bar.json').read_bytes())
    return tmp_path,records,reviews


def test_grader_counts_conversations_not_calls(simulated_run):
    path,records,reviews=simulated_run
    score=aggregate(path,reviews)
    assert len(records)>24 and score['denominator']==24 and score['quality_passes']==24
    assert score['live_passes']==6 and score['status'].startswith('PROVISIONAL')


def test_grader_keeps_provider_errors_and_critical_failures(simulated_run):
    path,records,reviews=simulated_run
    records[0]['auto']['pass']=False
    (path/'outputs.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
    reviews[('GS-018','replay',1)]['critical_violation']='quiz_answer_leak'
    score=aggregate(path,reviews)
    assert score['denominator']==24 and score['quality_passes']<24
    assert not score['quality_bar_passed'] and 'Hold' in score['status']


def test_replay_only_cannot_pass_required_rollouts(simulated_run):
    path,records,reviews=simulated_run
    records=[r for r in records if r['mode']=='replay']
    reviews={k:v for k,v in reviews.items() if k[1]=='replay'}
    (path/'outputs.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
    score=aggregate(path,reviews)
    assert score['live_passes']==0 and not score['quality_bar_passed']


def test_grading_refuses_missing_reviews(simulated_run):
    path,records,reviews=simulated_run
    reviews.pop(('GS-001','replay',1))
    with pytest.raises(ValueError,match='exactly'):aggregate(path,reviews)
