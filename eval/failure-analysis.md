# Latest full regression — remaining failures

Candidate: [20260918T075456Z-exploratory-candidate-5a022e](runs/20260918T075456Z-exploratory-candidate-5a022e/report.md).
Baseline: [20260918T075048Z-exploratory-baseline-020ae4](runs/20260918T075048Z-exploratory-baseline-020ae4/report.md).

Both variants used matching contract hashes and the final shared core, running sequentially with two case workers. **20/24 candidate versus 13/24 baseline automatic structural passes.** These checks are not semantic accuracy or an official scored evaluation. With four case failures, the latest candidate does not reach the proposed minimum 21/24 even before human grading.

| Case | Actual observed failure | Implication / next improvement |
|---|---|---|
| GS-002 replay | “ko hiểu lắm…” received another explanation/check instead of a focused diagnosis. | Informal confusion does not consistently trigger the desired pedagogical decision. Improve decision examples, then rerun the complete frozen suite once humans freeze it. |
| GS-012 replay | First output attempted an inconsistent page change; retry contained too many questions. Both were rejected, so the app showed a recoverable error. | Source/correction schema compliance remains brittle. A more concise correction schema or provider with stronger structured-output compliance may help. Do not bypass evidence validation. |
| GS-009 live step 4 | After a repair, the tutor labelled a repeated wrong statement “unclear” and continued feedback rather than the expected bounded fallback. It did **not** mark understanding correct. | Semantic check classification and stopping behavior still need refinement. This is not the earlier false-positive praise; the original critical failures are retained in older runs. |
| GS-016 live step 4 | After two unsuccessful diagnostic questions, tutor tried another explanation/check instead of acknowledging that the gap was still unknown and falling back. | The probe counter caps new diagnostic questions, but the model can still choose an unhelpful explanation. A stricter explicit “gap identified” gate is a candidate follow-up, subject to pilot/human review. |

The latest candidate made 51 provider calls for replay and rollouts, including bounded retries and understanding verification. Model-backed turn latency median was approximately **3.85 s**, maximum **48.59 s**, in this run; these are observed local-run values, not performance guarantees. One output ended in a provider/validation error (GS-012).

Other outputs still require claim-by-claim human Factuality/Relevance/Sensitivity grading and live branch-fit review. No statement that the remaining 20 cases are semantically correct, no claim of zero critical failures across all outputs, and no learning-outcome claim is made here.

## Delivered verification

- 39 offline engineering tests passed, including session isolation, rerun duplication, source/citation validation, state limits, pending-check behavior, independent understanding verification and evaluation aggregation. These tests use explicit doubles where appropriate; they do not fabricate model results.
- Repository document links resolve, Git whitespace checks pass, and scanning the generated text artifacts found no configured API-key value.

Pending course requirements: human review/authorship of final cases, two independent reviewers on five shared pilot outputs, rubric calibration, official freeze and scored run, and optional willing-user validation. See [README](README.md) for concrete commands/templates.
