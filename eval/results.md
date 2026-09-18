# Actual evaluation results

These are **exploratory runs and automatic structural checks**, not human factuality scores or a frozen quality-bar result. Every earlier error and failed run is retained. The latest run is reported even if a previous one had a higher count.

| Run (UTC) | Phase / prompt | Structural conversation passes | Error outputs | Report |
|---|---|---:|---:|---|
| `20260918T072226Z-pilot-candidate-167925` | pilot / candidate | 1/15 | 14 | [outputs](pilot/20260918T072226Z-pilot-candidate-167925/report.md) |
| `20260918T072240Z-pilot-candidate-402731` | pilot / candidate | 1/15 | 14 | [outputs](pilot/20260918T072240Z-pilot-candidate-402731/report.md) |
| `20260918T072533Z-pilot-candidate-b5e2d6` | pilot / candidate | 1/1 | 0 | [outputs](pilot/20260918T072533Z-pilot-candidate-b5e2d6/report.md) |
| `20260918T072735Z-pilot-candidate-664cd4` | pilot / candidate | 14/15 | 0 | [outputs](pilot/20260918T072735Z-pilot-candidate-664cd4/report.md) |
| `20260918T073243Z-exploratory-candidate-aad103` | exploratory / candidate | 19/24 | 3 | [outputs](runs/20260918T073243Z-exploratory-candidate-aad103/report.md) |
| `20260918T073245Z-exploratory-baseline-e9ebf7` | exploratory / baseline | 11/24 | 3 | [outputs](runs/20260918T073245Z-exploratory-baseline-e9ebf7/report.md) |
| `20260918T073717Z-exploratory-baseline-fbb944` | exploratory / baseline | 13/24 | 1 | [outputs](runs/20260918T073717Z-exploratory-baseline-fbb944/report.md) |
| `20260918T073717Z-exploratory-candidate-650ac1` | exploratory / candidate | 22/24 | 2 | [outputs](runs/20260918T073717Z-exploratory-candidate-650ac1/report.md) |
| `20260918T074352Z-exploratory-baseline-46b991` | exploratory / baseline | 13/24 | 2 | [outputs](runs/20260918T074352Z-exploratory-baseline-46b991/report.md) |
| `20260918T074354Z-exploratory-candidate-7d57e0` | exploratory / candidate | 18/24 | 4 | [outputs](runs/20260918T074354Z-exploratory-candidate-7d57e0/report.md) |
| `20260918T075048Z-exploratory-baseline-020ae4` | exploratory / baseline | 13/24 | 3 | [outputs](runs/20260918T075048Z-exploratory-baseline-020ae4/report.md) |
| `20260918T075456Z-exploratory-candidate-5a022e` | exploratory / candidate | 20/24 | 1 | [outputs](runs/20260918T075456Z-exploratory-candidate-5a022e/report.md) |

## Current comparison

- Latest **baseline**: **13/24 automatic passes**, [full report](runs/20260918T075048Z-exploratory-baseline-020ae4/report.md). Human quality grading is pending.
- Latest **candidate**: **20/24 automatic passes**, [full report](runs/20260918T075456Z-exploratory-candidate-5a022e/report.md). Human quality grading is pending.

The proposed quality bar is ≥80% of conversations passing (at least 20/24), with zero critical violations across the evaluation, judged with Factuality/Relevance. Live rollout results are reported separately without a separate pass quota. Saved runs retain their original contract. Automatic checks alone cannot establish that bar. No `freeze.json` or completed independent human grading is claimed.

## Evidence and limitations

- 24 case drafts; 13 explicitly adapted from verified real chatlog chains; 23 with prior conversation; six live rollout scripts. Human coverage/case review remains pending.
- Real pilot analysis and fixes: [error taxonomy](error-taxonomy.md). The full suite has been inspected for fixes and is now an exposed regression suite, not an unseen benchmark.
- Latest remaining issues and their implications: [failure analysis](failure-analysis.md). The full comparison candidate had four automatic case failures (20/24); it fell below its saved 21/24 threshold. The revised 80% bar requires a new run and human grading.
- Run `7d57e0` contained false-positive understanding checks. A separate focused verifier was added afterward; original critical failures remain visible. LLM agreement still does not prove learning.
- Case/rubric revisions occurred before any official freeze; compare variants with matching contract hashes. Older runs are not silently rescored.
- Two independent people must score five common pilot outputs, revise ambiguous criteria, review final case content and freeze the bar before official scored runs. Use [the evaluation instructions](README.md).
- No external-user validation, production deployment or checkpoint submission was performed.

## Engineering verification

Focused tests cover source extraction/retrieval, citation rejection, pending-check/correction state, skip/quiz boundaries, the two-call budget, understanding verification, UI reruns/session isolation, and evaluation counting. See `verification.json` for the actual latest test result. Test doubles are never reported as real model outcomes.

Index generated: 2026-09-18T07:59:06.597356+00:00.
