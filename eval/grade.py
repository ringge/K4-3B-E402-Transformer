"""Aggregate actual human review sheets; never turn automatic checks into quality scores."""
import argparse
import csv
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from codebase.config import ROOT

DIMENSIONS=['factuality','relevance','sensitivity']


def load_reviews(path):
    with Path(path).open() as f: rows=list(csv.DictReader(f))
    result={}
    for r in rows:
        key=(r['case_id'],r['mode'],int(r['step']))
        if key in result: raise ValueError('Duplicate review row: '+str(key))
        if any(r[d] not in {'pass','fail'} for d in DIMENSIONS):
            raise ValueError('All dimensions need pass/fail: '+str(key))
        if not r['reviewer'].strip() or not r['evidence_note'].strip():
            raise ValueError('Reviewer name and evidence note required: '+str(key))
        if r['critical_violation'] not in {'none','unsupported_material_claim','fabricated_citation','quiz_answer_leak','false_verified_understanding','injection_boundary_breach'}:
            raise ValueError('Use an explicit critical violation category or none: '+str(key))
        if r['branch_fits'] not in {'pass','fail','na'}:
            raise ValueError('branch_fits must be pass/fail/na: '+str(key))
        result[key]=r
    return result


def aggregate(run_dir,reviews):
    run_dir=Path(run_dir)
    records=[json.loads(s) for s in (run_dir/'outputs.jsonl').read_text().splitlines()]
    manifest=json.loads((run_dir/'manifest.json').read_text())
    case_snapshots={c['id']:c for c in map(json.loads,(run_dir/'cases.jsonl').read_text().splitlines())}
    required={(r['case_id'],r['mode'],r['step']) for r in records}
    if set(reviews)!=required: raise ValueError('Review rows must match exactly the actual outputs of this run.')
    for r in records:
        review=reviews[(r['case_id'],r['mode'],r['step'])]
        if r.get('branch_fit_review_required') and review['branch_fits']=='na':
            raise ValueError('Live scripted reply needs branch-fit review: '+r['case_id'])
    if not (run_dir/'quality-bar.json').exists():
        raise ValueError('This early exploratory run lacks a bar snapshot. Keep it as exploratory evidence; grade a new fully snapshotted run.')
    bar=json.loads((run_dir/'quality-bar.json').read_text())
    passed={}; live={}
    def row_pass(r):
        score=reviews[(r['case_id'],r['mode'],r['step'])]
        return r['auto']['pass'] and not r.get('remaining_steps_not_run',0) and all(score[d]=='pass' for d in DIMENSIONS) and score['critical_violation']=='none' and score['branch_fits']!='fail'
    for case_id in manifest['case_ids']:
        rows=[r for r in records if r['case_id']==case_id]
        rollout_rows=[r for r in rows if r['mode']=='rollout']
        needs_live=case_snapshots[case_id]['rollout_required']
        live[case_id]=bool(rollout_rows) and all(row_pass(r) for r in rollout_rows)
        passed[case_id]=bool(rows) and all(row_pass(r) for r in rows) and (not needs_live or live[case_id])
    # Cross-case conditions are evaluated explicitly, never inferred from aggregate scores.
    for pair,ids in {'clarity':['GS-001','GS-004'],'check_correctness':['GS-008','GS-009'],'support':['GS-011','GS-024']}.items():
        if not all(i in passed for i in ids): continue
        replay=[r for r in records if r['case_id'] in ids and r['mode']=='replay']
        if len(replay)!=2 or not all(reviews[(r['case_id'],'replay',r['step'])]['sensitivity']=='pass' and r['auto']['pass'] for r in replay):
            for i in ids: passed[i]=False
    critical=sum(r['critical_violation']!='none' for r in reviews.values())
    count=sum(passed.values());live_count=sum(live.values())
    complete=manifest.get('complete',False) and len(passed)==bar['case_count'] and manifest['rollouts_requested']
    bar_pass=complete and count>=bar['minimum_passes'] and live_count>=bar['minimum_live_passes'] and critical==0
    status='Hold' if critical else ('Ship for bounded demo' if bar_pass else 'Limited')
    if manifest['phase']!='scored':status='PROVISIONAL '+status+' (not a frozen scored run)'
    groups={}
    for attr in ['bucket','origin']:
        for case_id,c in case_snapshots.items():
            group=c['origin']['kind'] if attr=='origin' else c[attr]
            key=attr+':'+group
            groups.setdefault(key,{'passed':0,'total':0})
            groups[key]['total']+=1;groups[key]['passed']+=int(passed[case_id])
    return {'status':status,'quality_passes':count,'denominator':len(passed),'fraction':count/len(passed) if passed else 0,
            'live_passes':live_count,'live_required':bar['required_live_rollouts'],'critical_violations':critical,
            'complete':complete,'quality_bar_passed':bar_pass,'cases':passed,'groups':groups,
            'dimensions':{d:{'passed':sum(r[d]=='pass' for r in reviews.values()),'total':len(reviews)} for d in DIMENSIONS},
            'limitations':'Not evidence of learning gains; all scripted learner replies require coherence review.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run_dir',type=Path);parser.add_argument('--reviews',type=Path,required=True)
    args=parser.parse_args()
    try: result=aggregate(args.run_dir,load_reviews(args.reviews))
    except (ValueError,KeyError) as exc: raise SystemExit(str(exc))
    out=args.run_dir/'human-summary.json'
    if out.exists():raise SystemExit('human-summary.json exists; preserve it. Use a copied run folder for a separately labelled adjudication.')
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
