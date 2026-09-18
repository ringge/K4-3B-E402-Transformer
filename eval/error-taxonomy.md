# Observed pilot errors — agent analysis, human calibration pending

Evidence: `pilot/20260918T072735Z-pilot-candidate-664cd4/outputs.jsonl`. This was a real 15-case pilot against the configured compatible model; 14 model-backed cases plus the deterministic quiz boundary. Automatic action/schema checks passed 14/15 before the rubric refinement below. These are not final quality scores.

| Error | Trigger → observed behavior → consequence | Evidence | Change |
|---|---|---|---|
| GENERIC_PROBE | Vague confusion on known topic → asks “Bạn thấy khó hình dung ở phần nào?” without distinguishing candidate gaps → learner must still diagnose themselves. | GS-003 | Require a focused contrast between at least two plausible difficulties when topic is known. |
| GUESSED_REFERENT | Incomplete quote, no page → offers guessed topics instead of asking for complete passage/page → can steer learner to the wrong context. | GS-015 | Missing referent requires actual context request; retrieval candidates cannot substitute for it. |
| OFFERS_OUT_OF_SCOPE_TEACHING | Unsupported architecture detail → says it can explain Q/K/V outside the slide if requested → invites source-boundary breach on next turn. | GS-011 | No offer to teach unsupported knowledge even with a disclaimer; offer TA or supported topic. |
| SOURCE_WORDING_PROPAGATION | Related retrieval → repeats a potentially misleading page-15 statement about attention and the letter T → a correct quote can still teach an incorrect/ambiguous concept. | GS-011, page 15 B006 | Flag that block in source-quality log and exclude it as teaching evidence pending TA review. |
| CITATION_WITHOUT_CLAIM | Procedural diagnosis → model adds source IDs without supported claims → cannot determine what the citation backs. | GS-001/002 first attempts | Runtime rejected and retried; prompt now explicitly requests empty evidence fields for procedural-only replies. |
| INCONSISTENT_CHECK_ASSESSMENT | Incorrect check answer → repair action without incorrect assessment → inconsistent state transition. | GS-009 first attempt | Validator rejected and retried; second response was consistent. Preserve both attempts. |
| RUBRIC_TOO_NARROW | Mixed supported/unsupported question → tutor appropriately teaches supported part, discloses missing detail and adds a check → draft action list rejected a useful output. | GS-013 | Before freeze, allow explain_and_check alongside answer/abstain for this mixed request. Original run remains unchanged. |

Earlier infrastructure failures remain in `pilot/`: `167925` was sandbox connection failure; `402731` was HTTP 404 from the host-only base URL. The adapter now normalizes host-only compatible URLs to `/v1`. `b5e2d6` was a one-case connection smoke check, not a full scored suite.

## Rough output labels from the actual pilot

These labels are **Codex's preliminary review**, not independent human ratings or a frozen evaluation result.

| Case | Rough label | Reason |
|---|---|---|
| GS-001 | dùng được | Focused distinction between “nền chung” and chatbot wrapper; first invalid citation attempt was corrected before display. |
| GS-002 | dùng được | Focused token-versus-language difficulty choices; no long re-explanation. |
| GS-003 | sửa được | Generic diagnostic question leaves gap discovery to learner. |
| GS-004 | sửa được | Directly addresses gap, but introduces a named-product example beyond the page-10 evidence; use generic illustration. |
| GS-006 | dùng được | Concrete supported applications and small check. |
| GS-007 | dùng được | Labelled hypothetical agent workflow and memory check. |
| GS-008 | dùng được | Confirms the specific supplied check answer, not general mastery. |
| GS-009 | dùng được | Repairs misconception with source and another check after rejecting an inconsistent first attempt. |
| GS-010 | sửa được | Correct context and state, but long and repeats source simplifications; keep correction concise. |
| GS-011 | không chấp nhận được | Source limitation stated, yet offers unsupported teaching and propagates flagged source wording. |
| GS-013 | dùng được | Clear partial grounding; draft action allowlist needed refinement. |
| GS-014 | dùng được | Requests topic/page without asserting a referent. |
| GS-015 | sửa được | Guesses context for truncated excerpt. |
| GS-016 | dùng được | Stops within budget and gives a concrete next step. |
| GS-018 | dùng được | Quiz boundary preserves no-answer rule; deterministic guard, not a model-generated response. |

The named-product example and long correction are additional items for human grading and the next full regression run. A “dùng được” rough label does not replace claim-by-claim human evaluation.

## Additional errors from full exploratory regressions

- `REPAIR_BUDGET_BYPASS`: candidate run `650ac1`, GS-009 rollout step 3 replaced a pending check using `explain_and_check`, so the repair counter did not advance. The controller now rejects a fresh answer/explanation while a check is pending; the tutor must assess it, correct context or take a fallback.
- `FALSE_POSITIVE_CHECK`: run `7d57e0`, GS-009 rollout step 3 and GS-010 rollout step 2 praised a wrong learner statement as correct. This is a **critical failure observed by Codex**, not a completed independent human grade. A focused second assessment now must agree and quote the learner's answer before verification; any disagreement/error/exhausted two-call budget keeps understanding unverified. Preserve these failures; do not report the earlier run as passing the quality bar.
- `OVERSTRICT_QUESTION_PUNCTUATION`: a single check written as a yes/no stem plus “Vì sao?” was rejected merely for two question marks. Validation now permits that form within one check object, while rejecting an extra question in the reply or multiple separate checks. Human reviewers still judge whether it is one cognitive task.
- `PROVIDER_LOAD`: several later runs had timeouts while baseline, candidate and browser calls overlapped. Final comparison uses sequential variants and at most two concurrent cases. Timeouts are kept in each run's denominator.
- `SOURCE_QUOTE_DRIFT`: occasional model quotations differ from the source and are rejected, sometimes after both attempts. The displayed result remains a recoverable error; this is a remaining usability/formatting limitation, not grounds to weaken evidence validation.
