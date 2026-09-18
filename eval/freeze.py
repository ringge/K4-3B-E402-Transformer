"""Freeze the contract only with actual case review and calibration evidence."""
import argparse
import csv
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from codebase.config import ROOT,Settings
from codebase.knowledge import Knowledge
from eval.run import CONTRACT,digest,read_cases


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case-review',type=Path,required=True);p.add_argument('--calibration',type=Path,required=True)
    args=p.parse_args();out=ROOT/'eval/freeze.json'
    if out.exists():raise SystemExit('Already frozen; refusing to overwrite.')
    calibration=json.loads(args.calibration.read_text())
    if not calibration.get('ready_to_freeze') or calibration.get('cases')!=5:raise SystemExit('Calibration is incomplete or definitions still disagree.')
    for path,checksum in calibration['review_files'].items():
        if digest(path)!=checksum:raise SystemExit('A calibration review sheet changed.')
    pilot=Path(calibration['pilot_dir'])
    if digest(pilot/'outputs.jsonl')!=calibration['pilot_outputs_sha256']:raise SystemExit('Pilot outputs changed.')
    with args.case_review.open() as f: reviews=list(csv.DictReader(f))
    cases=read_cases()
    if len(reviews)!=24 or {r['case_id'] for r in reviews}!={c['id'] for c in cases}:raise SystemExit('Review all 24 unique cases.')
    if any(r['approved']!='yes' or not r['reviewer'].strip() or not r['notes'].strip() for r in reviews):raise SystemExit('Every case needs a human review, approval and notes about source/provenance/behavior.')
    bar=json.loads((ROOT/'eval/quality-bar.json').read_text())
    bar['status']='frozen';bar['version']='v1'
    (ROOT/'eval/quality-bar.json').write_text(json.dumps(bar,ensure_ascii=False,indent=2)+'\n')
    record={'timestamp':datetime.now(timezone.utc).isoformat(),'files':{p:digest(ROOT/p) for p in CONTRACT},
            'source_sha256':Knowledge(Settings.from_env().source_path).sha256,
            'calibration_sha256':digest(args.calibration),'case_review_sha256':digest(args.case_review),
            'reviewers':sorted({r['reviewer'] for r in reviews})}
    out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('Frozen eval contract:',out)


if __name__=='__main__':main()
