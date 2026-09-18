"""Build an honest index of saved runs without regrading or overwriting them."""
from datetime import datetime,timezone
import json
from pathlib import Path

EVAL=Path(__file__).resolve().parent


def main():
    summaries=[]
    for parent in ['pilot','runs']:
        for path in sorted((EVAL/parent).glob('*/summary.json')):
            s=json.loads(path.read_text());s['_path']=str(path.parent.relative_to(EVAL));summaries.append(s)
    lines=['# Actual evaluation results','',
           'These are **exploratory runs and automatic structural checks**, not human factuality scores or a frozen quality-bar result. Every earlier error and failed run is retained. The latest run is reported even if a previous one had a higher count.','',
           '| Run (UTC) | Phase / prompt | Structural conversation passes | Error outputs | Report |',
           '|---|---|---:|---:|---|']
    for s in sorted(summaries,key=lambda s:s['run_id']):
        lines.append(f'| `{s["run_id"]}` | {s["phase"]} / {s["variant"]} | {s["automatic_structural_passes"]}/{s["automatic_structural_denominator"]} | {s["provider_or_validation_errors"]} | [outputs]({s["_path"]}/report.md) |')
    lines += ['', '## Current comparison', '']
    for variant in ['baseline','candidate']:
        matches=[s for s in summaries if s['phase']=='exploratory' and s['variant']==variant]
        if matches:
            s=max(matches,key=lambda s:s['run_id'])
            lines.append(f'- Latest **{variant}**: **{s["automatic_structural_passes"]}/{s["automatic_structural_denominator"]} automatic passes**, [full report]({s["_path"]}/report.md). Human quality grading is pending.')
    lines += ['', 'The proposed quality bar is 21/24 conversations, ≥5/6 live rollouts, and zero critical violations, judged with Factuality/Relevance/Sensitivity. Automatic checks alone cannot establish that bar. No `freeze.json` or completed independent human grading is claimed.',
              '', '## Evidence and limitations','',
              '- 24 case drafts; 13 explicitly adapted from verified real chatlog chains; 23 with prior conversation; six live rollout scripts. Human coverage/case review remains pending.',
              '- Real pilot analysis and fixes: [error taxonomy](error-taxonomy.md). The full suite has been inspected for fixes and is now an exposed regression suite, not an unseen benchmark.',
              '- Latest remaining issues and their implications: [failure analysis](failure-analysis.md). The latest candidate has four automatic case failures and does not reach the proposed 21/24 minimum before semantic grading.',
              '- Run `7d57e0` contained false-positive understanding checks. A separate focused verifier was added afterward; original critical failures remain visible. LLM agreement still does not prove learning.',
              '- Case/rubric revisions occurred before any official freeze; compare variants with matching contract hashes. Older runs are not silently rescored.',
              '- Two independent people must score five common pilot outputs, revise ambiguous criteria, review final case content and freeze the bar before official scored runs. Use [the evaluation instructions](README.md).',
              '- No external-user validation, production deployment or checkpoint submission was performed.']
    lines += ['', '## Engineering verification','',
              'Focused tests cover source extraction/retrieval, citation rejection, pending-check/correction state, skip/quiz boundaries, the two-call budget, understanding verification, UI reruns/session isolation, and evaluation counting. See `verification.json` for the actual latest test result. Test doubles are never reported as real model outcomes.',
              '',f'Index generated: {datetime.now(timezone.utc).isoformat()}.']
    (EVAL/'results.md').write_text('\n'.join(lines)+'\n')
    print('Updated eval/results.md from',len(summaries),'retained run summaries.')


if __name__=='__main__':main()
