"""Real-provider replay/rollout runner. Structural checks are NOT human quality scores."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase.config import ROOT, Settings
from codebase.knowledge import Knowledge
from codebase.model_client import ModelClient
from codebase.state import TutorState
from codebase.tutor import Tutor
from codebase.turns import ROUTE_PROMPT

EVAL = ROOT/'eval'
CONTRACT = ['eval/golden.json','eval/rollout-scripts.json','eval/source-manifest.json',
            'eval/rubric.md','eval/quality-bar.json','codebase/prompts/baseline.md','codebase/prompts/common.md',
            'codebase/turns.py']


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read_cases():
    return json.loads((EVAL/'golden.json').read_text(encoding='utf-8'))


def check_suite(cases, knowledge):
    assert len(cases) == 24 and len({c['id'] for c in cases}) == 24
    expected_counts = {'normal':10,'source':3,'ambiguity':3,'scope':3,'education':3,'rare':2}
    assert {b:sum(c['bucket']==b for c in cases) for b in expected_counts} == expected_counts
    assert sum(c['origin']['kind']=='adapted_from_real' and c['origin']['sequence_verified'] for c in cases) >= 10
    assert sum(bool(c['history']) for c in cases) >= 18
    assert sum(c['rollout_required'] for c in cases) == 6
    for c in cases:
        assert set(c['source_ids']) <= set(knowledge.pages)
        TutorState.model_validate({**c['initial_state'],'messages':c['history']})
        assert c['expected']['allowed_actions'] and c['expected']['must']
    return {'cases':len(cases),'buckets':expected_counts,
            'real_derived':sum(c['origin']['kind']=='adapted_from_real' for c in cases),
            'with_history':sum(bool(c['history']) for c in cases), 'rollouts':6,
            'human_review_pending':sum(c['reviewer'] is None for c in cases)}


def structural(result, allowed):
    failures=[]
    if result.error:
        failures.append('provider_or_validation_error')
    elif result.response.action not in allowed:
        failures.append('unexpected_action:'+result.response.action)
    return {'pass':not failures,'failures':failures,
            'note':'Checks action/schema/citations/state only. Semantic quality remains ungraded.'}


def evaluate_case(case, script, tutor, run_rollouts):
    state=TutorState.model_validate({**case['initial_state'],'messages':case['history']})
    result=tutor.step(state,case['input'],intent=case.get('intent','chat'))
    records=[{'case_id':case['id'],'mode':'replay','step':1,
              'expected':case['expected'], 'auto':structural(result,case['expected']['allowed_actions']),
              'trace':result.trace,'displayed':result.response.visible_text() if result.response else result.error}]
    if case['rollout_required'] and run_rollouts:
        state=TutorState(active_page=script['active_page'])
        for i,turn in enumerate(script['steps'],1):
            result=tutor.step(state,turn['input'],intent=turn.get('intent','chat'))
            record={'case_id':case['id'],'mode':'rollout','step':i,'expected':turn,
                    'auto':structural(result,turn['allowed_actions']), 'trace':result.trace,
                    'displayed':result.response.visible_text() if result.response else result.error,
                    'branch_fit_review_required':bool(turn.get('requires_semantic_review'))}
            records.append(record)
            if result.error:
                # A failed preceding turn makes later learner turns uninterpretable.
                record['remaining_steps_not_run']=len(script['steps'])-i
                break
            state=result.state
    return records


def write_report(out, records, manifest):
    cases=sorted({r['case_id'] for r in records})
    auto_cases=sum(all(r['auto']['pass'] for r in records if r['case_id']==c) for c in cases)
    summary={'run_id':out.name,'phase':manifest['phase'],'variant':manifest['variant'],
             'planned_cases':len(manifest['case_ids']),'executed_cases':len(cases),
             'automatic_structural_passes':auto_cases,'automatic_structural_denominator':len(cases),
             'quality_passes':None,'quality_bar_result':'PENDING_HUMAN_GRADING',
             'provider_or_validation_errors':sum(r['trace'].get('status')!='ok' for r in records),
             'model_calls':sum(len(r['trace'].get('attempts',[])) for r in records),
             'critical_violations':None,
             'note':'Automatic passes are not factuality scores, model accuracy, or evidence of learning.'}
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    lines=[f'# Evaluation run {out.name}', '',f'Phase: **{manifest["phase"]}** · Prompt: **{manifest["variant"]}**',
           '',f'Automatic structural checks: **{auto_cases}/{len(cases)} conversation cases**.',
           '**Quality score and Ship/Limited/Hold decision: pending human grading.**',
           'An automatic pass does not establish semantic grounding or good pedagogy. All errors remain in the denominator.', '']
    for r in records:
        lines += [f'## {r["case_id"]} · {r["mode"]} · step {r["step"]}', '',
                  '**Input:** '+r['trace']['input'], '',
                  '**Actual output:**', '',r['displayed'], '',
                  '**Automatic checks:** '+json.dumps(r['auto'],ensure_ascii=False), '',
                  '**Expected behavior:** '+json.dumps(r['expected'],ensure_ascii=False), '',
                  '**Retrieved pages:** '+', '.join(r['trace'].get('retrieved_ids',[])), '']
    (out/'report.md').write_text('\n'.join(lines))
    # One row per scored turn; independent reviewers copy/fill their own sheet.
    import csv
    with (out/'review-template.csv').open('w',newline='') as f:
        fields=['case_id','mode','step','factuality','relevance','critical_violation',
                'branch_fits','evidence_note','reviewer']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in records:
            writer.writerow({k:r[k] for k in ['case_id','mode','step']})
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=['pilot','exploratory','scored'],default='exploratory')
    parser.add_argument('--variant',choices=['candidate','baseline'],default='candidate')
    parser.add_argument('--rollouts',action='store_true')
    parser.add_argument('--limit',type=int)
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--validate-only',action='store_true')
    args=parser.parse_args()
    settings=Settings.from_env();knowledge=Knowledge(settings.source_path)
    all_cases=read_cases(); coverage=check_suite(all_cases,knowledge)
    if args.validate_only:
        print(json.dumps(coverage,indent=2));return
    if error:=settings.configuration_error():
        raise SystemExit(error)
    if not 1 <= args.workers <= 4:
        raise SystemExit('--workers must be between 1 and 4')
    hashes={p:digest(ROOT/p) for p in CONTRACT}
    freeze_path=EVAL/'freeze.json'
    if args.phase=='scored':
        if not freeze_path.exists():
            raise SystemExit('No reviewed freeze.json. Use --phase exploratory; see eval/README.md for human calibration/freeze.')
        frozen=json.loads(freeze_path.read_text())
        if frozen['files']!=hashes or frozen['source_sha256']!=knowledge.sha256:
            raise SystemExit('Frozen contract/source changed. Restore it; do not silently change the scoring contract.')
        if args.limit or not args.rollouts:
            raise SystemExit('A scored run must include all cases and required rollouts.')
    selected=all_cases
    if args.phase=='pilot':
        pilot_ids={f'GS-{n:03}' for n in [1,2,3,4,6,7,8,9,10,11,13,14,15,16,18]}
        selected=[c for c in all_cases if c['id'] in pilot_ids]
    if args.limit:
        if args.limit < 1: raise SystemExit('--limit must be positive')
        selected=selected[:args.limit]
    scripts=json.loads((EVAL/'rollout-scripts.json').read_text())
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+args.phase+'-'+args.variant+'-'+uuid4().hex[:6]
    out=EVAL/('pilot' if args.phase=='pilot' else 'runs')/run_id
    out.mkdir(parents=True,exist_ok=False)
    tutor=Tutor(knowledge,ModelClient(settings),args.variant)
    tracked=[p for p in (ROOT/'codebase').rglob('*') if p.suffix in {'.py','.md','.txt'} and '__pycache__' not in p.parts]
    tracked += [ROOT/'eval/run.py', ROOT/'eval/grade.py']
    manifest={'run_id':run_id,'phase':args.phase,'variant':args.variant,'settings':settings.public(),
              'case_ids':[c['id'] for c in selected], 'source_sha256':knowledge.sha256,
              'contract_hashes':hashes,'prompt_sha256':tutor.prompt_hash,
              'route_prompt_sha256':tutor.route_prompt_hash,
              'code_hashes':{str(p.relative_to(ROOT)):digest(p) for p in tracked if p.exists()},
              'rollouts_requested':args.rollouts,'human_review_status':'pending',
              'git_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip(),
              'started_at':datetime.now(timezone.utc).isoformat()}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (out/'prompt.txt').write_text(tutor.system)
    (out/'route-prompt.txt').write_text(ROUTE_PROMPT)
    for name in ['rubric.md','quality-bar.json','rollout-scripts.json','source-manifest.json']:
        (out/name).write_bytes((EVAL/name).read_bytes())
    # Snapshot the actual contract so a later draft revision cannot erase the context of this run.
    (out/'cases.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in selected))
    records=[]
    print('Run directory:',out.relative_to(ROOT),flush=True)
    try:
        with (out/'outputs.jsonl').open('a') as log, ThreadPoolExecutor(max_workers=args.workers) as pool:
            jobs={pool.submit(evaluate_case,c,scripts.get(c['id']),tutor,args.rollouts):c['id'] for c in selected}
            for future in as_completed(jobs):
                rows=future.result()
                records.extend(rows)
                for row in rows: log.write(json.dumps(row,ensure_ascii=False)+'\n')
                log.flush()
                print(jobs[future], '/'.join(r['trace'].get('response',{}).get('action','ERROR') for r in rows),flush=True)
    finally:
        records.sort(key=lambda r:(r['case_id'],r['mode'],r['step']))
        summary=write_report(out,records,manifest)
        manifest['finished_at']=datetime.now(timezone.utc).isoformat()
        manifest['complete']=len({r['case_id'] for r in records})==len(selected)
        (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
