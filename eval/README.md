# Evaluation workspace

All cases, provenance, pilot outputs, run reports, and reviewer tooling are in **this repo's `eval/`**. The model uses only `data/d1-slide-hackathon.html` for lesson knowledge.

## What is ready versus pending

- `golden.json`: a formatted JSON array of **24 reviewable drafts**, 13 adapted from real chatlog chains, 23 with prior conversation; **not yet a human-reviewed frozen golden set**.
- `coverage.csv`: five-axis User Input Grid; 10 normal, 3 per each of four risk layers, 2 rare cases.
- `provenance.csv`: exact source turn IDs, short masked excerpts, explicit adaptation notes. Prior assistant fixtures are authored for controlled replay, not presented as original chatlog quotes.
- `rollout-scripts.json`: six actual conversation scripts using generated assistant responses as history. Fixed learner replies still need semantic branch-fit review.
- `source-manifest.json` / `source-quality.md`: exact source version, page inventory, and limitations.
- `pilot/` and `runs/`: actual attempted runs with immutable IDs, input/output traces and reports. Network/provider failures are retained.
- `rubric.md`, `quality-bar.json`: proposed evaluation definitions. They become an official frozen contract only after the required human review/calibration.
- Shared conditional rules are defined in `rubric.md`. The active-quiz answer restriction is repeated in quiz-related cases only (currently GS-018); it is not applicable to ordinary learning cases without an active quiz.
- `calibration/`: blank review templates and instructions. No invented reviewer names, ratings, or agreement.

The assignment requires humans to design/review coverage and case content. These agent-authored adaptations are a starting point for that work; independent human grading cannot be replaced by the assistant claiming it happened.

The current draft contract uses **optional comprehension checks**. Ordinary explanations, examples and misconception corrections expect `answer`; assessment fixtures and rollouts explicitly opt in. Help while a check is pending must return to teaching without grading or marking skip. Offline regression tests cover these transitions and rejected generator outputs. Free-text intent recognition still needs real-provider review, including paraphrases, negations, quoted requests and mixed answer/help turns. Historical pilot/run snapshots use their original contract; their scores do not measure this revision.

## Commands

For an individual replay in the UI, launch the Streamlit app and open **Replay tests** in its sidebar. Select a case, inspect its preloaded history/state and expectations, then click **Chạy replay**. The page uses this runner's replay function and keeps results separate from live chat. Download the result JSON for manual review; UI runs do not populate official run directories or satisfy required live rollouts. See [the app guide](../codebase/README.md#manual-replay-testing).

Run from the repo root after configuring the compatible API as in [codebase/README.md](../codebase/README.md).

```sh
# Offline source/case/schema/coverage validation
.venv/bin/python eval/run.py --validate-only

# First inspect 15 real outputs, before finalizing the rubric
.venv/bin/python eval/run.py --phase pilot --variant candidate --workers 2

# Full exploratory comparison; 24 replays + six live rollout scripts per variant
.venv/bin/python eval/run.py --phase exploratory --variant baseline --rollouts --workers 2
.venv/bin/python eval/run.py --phase exploratory --variant candidate --rollouts --workers 2
```

Each command creates a new run folder. `report.md` is the readable output; `outputs.jsonl` has every actual response, retrieved IDs, state transition, raw model output, usage, latency, retries and errors. `manifest.json`, `cases.jsonl`, and `prompt.txt` pin the exact configuration/input used. No API key is recorded. Reruns are separate artifacts, never overwrites or cherry-picked completions.

New runs also pin `route-prompt.txt` and its hash. Traces label routing, teaching and verification calls separately. The per-turn limit is one routing call plus two teaching/retry/verification calls; button intents bypass routing.

`--limit 1` is useful for a connection check; it is not a full evaluation. Five cases (GS-005/012/019/022/024) are excluded from pilot prompt tuning. Once the full suite is inspected and used for fixes, disclose that it is a regression suite rather than an unseen benchmark.

The automatic score checks action choices, schema validity, source identity/quote integrity, and state guards. **It is not factuality accuracy, a quality-bar pass, or evidence of improved learning.** Factuality/relevance/sensitivity need a person to read actual output against source and history. Provider errors remain failed cases in the denominator. A case with a required live rollout cannot pass final grading with replay alone.

## Human review, calibration, freeze, then official scoring

1. Read pilot outputs, label `dùng được` / `sửa được` / `không chấp nhận được`, and revise `error-taxonomy.md` with observed evidence. Review source/provenance and author/revise all 24 draft cases. Fill `case-review-template.csv` into a separate completed file.
2. Two reviewers independently fill the same **five** real-model output rows from a pilot's `review-template.csv`, saving separate files. Use `pass/fail` for each dimension, `none` or the named critical category, `pass/fail/na` for branch fit, and an evidence note plus actual reviewer name.
3. Compare without overwriting the original sheets:

```sh
.venv/bin/python eval/calibrate.py eval/pilot/RUN_ID \
  --a eval/calibration/reviewer-a.csv --b eval/calibration/reviewer-b.csv \
  --out eval/calibration/agreement-v1.json
```

At any disagreement among the five (≥20%), clarify the rubric and independently rescore; preserve earlier sheets/reports. Resolve pilot failures before freezing the official bar. The proposed threshold is **21/24 overall, ≥5/6 live rollouts, zero critical violations**.

4. Freeze with actual review evidence:

```sh
.venv/bin/python eval/freeze.py \
  --case-review eval/case-review-completed.csv \
  --calibration eval/calibration/agreement-v2.json
.venv/bin/python eval/run.py --phase scored --variant candidate --rollouts
```

`freeze.py` refuses missing review/calibration and refuses overwriting an existing freeze. Scored runs reject a modified contract or source. New regression cases belong in a separately versioned extension. Do not lower the bar after seeing results.

5. Fill all rows of that run's review sheet, independently grade difficult cases, reconcile transparently, and aggregate the adjudicated sheet:

```sh
.venv/bin/python eval/grade.py eval/runs/RUN_ID \
  --reviews eval/runs/RUN_ID/reviews-adjudicated.csv
```

This produces `human-summary.json`. Each complete conversation counts once, and every required turn/mode must pass all dimensions with no critical violation. For live scripts, fail `branch_fits` if the fixed learner reply does not answer the actual generated question; never silently substitute a reference assistant answer. Baseline is a controlled repeat-explanation prompt, not a recreation of production VLearn.

## Provenance maintenance

The runtime does not need the original CSV. To deliberately rebuild **drafts only**, while no freeze exists:

```sh
.venv/bin/python eval/build_cases.py --chatlog /path/to/course-pack/chatlog/tutor_turns.csv
```

This verifies same masked learner/course, chronology and ≤30-minute gaps. It does not prove actual session membership because the CSV has no conversation ID. Rebuilding overwrites draft files, so preserve any manual case revisions before using it.

Full source/chatlog data stays local and ignored. The app itself does not write real users' chats to disk. Evaluation uses supplied masked excerpts and synthetic/adapted fixtures; review saved model outputs before any public submission.
