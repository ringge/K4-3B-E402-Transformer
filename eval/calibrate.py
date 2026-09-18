"""Compare five independently graded outputs; preserve original review sheets."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from eval.grade import run_dimensions,load_reviews
from eval.run import digest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('pilot_dir',type=Path);p.add_argument('--a',type=Path,required=True);p.add_argument('--b',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();dimensions=run_dimensions(args.pilot_dir)
    a=load_reviews(args.a,dimensions);b=load_reviews(args.b,dimensions)
    actual={(r['case_id'],r['mode'],r['step']) for r in map(json.loads,(args.pilot_dir/'outputs.jsonl').read_text().splitlines()) if r['trace'].get('status')=='ok' and r['trace'].get('attempts')}
    if len(a)!=5 or set(a)!=set(b) or not set(a)<=actual:
        raise SystemExit('Both reviewers must independently score the same five real-model pilot outputs.')
    names_a={r['reviewer'].strip() for r in a.values()};names_b={r['reviewer'].strip() for r in b.values()}
    if len(names_a)!=1 or len(names_b)!=1 or names_a & names_b:
        raise SystemExit('Two distinct reviewer names required, one per sheet.')
    different=[{'case_id':key[0],'dimensions':[d for d in dimensions if a[key][d]!=b[key][d]],
                'critical_disagreement':a[key]['critical_violation']!=b[key]['critical_violation']}
               for key in a if any(a[key][d]!=b[key][d] for d in dimensions) or a[key]['critical_violation']!=b[key]['critical_violation']]
    result={'timestamp':datetime.now(timezone.utc).isoformat(),'pilot_dir':str(args.pilot_dir.resolve()),
            'pilot_outputs_sha256':digest(args.pilot_dir/'outputs.jsonl'),
            'reviewers':list(names_a|names_b),'review_files':{str(args.a.resolve()):digest(args.a),str(args.b.resolve()):digest(args.b)},
            'cases':5,'disagreement_count':len(different),'disagreement_fraction':len(different)/5,
            'disagreements':different,'ready_to_freeze':len(different)==0,
            'note':'At any disagreement (≥20%), clarify rubric and independently rescore; retain previous report.'}
    if args.out.exists():raise SystemExit('Output exists; choose a new calibration version.')
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
