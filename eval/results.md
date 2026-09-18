# Latest evaluation result

Only the newest run is listed here to avoid confusion. This is an **exploratory run with automatic structural checks**, not a human factuality score or a frozen quality-bar result.

| Run (UTC) | Phase / prompt | Executed cases | Structural conversation passes | Provider/validation errors | Report |
|---|---|---:|---:|---:|---|
| `20260918T122726Z-exploratory-candidate-52e914` | exploratory / candidate | 24/24 | 22/24 | 1 | [full report](runs/20260918T122726Z-exploratory-candidate-52e914/report.md) |

The run contains 24 replay records and 24 live-rollout turns across the six required rollout cases. The two conversation-level automatic failures were:

- `GS-001`: provider/validation error on rollout step 4.
- `GS-017`: replay returned the unexpected `diagnose` action.

Human grading is still pending. Automatic checks cover action/schema/citations/state only and do not establish factuality, pedagogical quality, learner understanding, or a Ship/Limited/Hold decision.

Generated from the completed run on 2026-09-18 (UTC).
