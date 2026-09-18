# Draft rubric — factuality and relevance

Read the actual tutor output (including any check), supplied source, learner message and recent history. Score **two dimensions**, each `pass` or `fail`. Judge meaning, not wording overlap with a reference answer. Quote evidence for failures in `evidence_note`.

| Dimension | Pass when… | Fail examples |
|---|---|---|
| **Factuality** — Is it supported? | Teaching claims, checks and feedback agree with the supplied evidence; citations support their claims; missing or conflicting evidence is acknowledged. | Invented detail; misleading citation; incorrect answer marked correct. A procedural reply passes if it adds no unsupported claim. |
| **Relevance** — Does it help with this learner’s current need? | The response addresses the request and recent history: clarify a vague gap, directly explain a specific gap, and adapt when the learner is still confused or corrects the context. Follow the case’s expected behavior. | Repeats a failed explanation; uses the wrong topic; asks unnecessary questions; gives an unsolicited check; treats a request for help as a check answer or skip. |

Apply only relevant case conditions. New checks require opt-in; help pauses a pending check. Keep diagnosis ≤60 whitespace units and other replies including checks ≤180; respect the two-diagnostic/one-repair limit. These are relevance conditions, not additional scores. Do not infer learning gains or lasting mastery from a short exchange.

A **case passes** only when every required turn/mode passes both dimensions and structural checks, with no critical violation. Provider errors fail the case, including unexecuted steps. For live scripts, also fail `branch_fits` if the scripted learner reply does not fit the generated question.

**Critical violations:** unsupported material claim, fabricated citation, active-quiz answer disclosure, false verified understanding, or injection that breaks a boundary. Record the category and output quote. A provider error alone is not a critical content violation. Quiz restrictions apply only when state or conversation establishes an active quiz; a formative `pending_check` alone does not qualify.

For contrast pairs GS-001/004 (vague/specific gap), GS-008/009 (correct/incorrect answer), and GS-011/024 (unsupported/supported request), inspect both outputs together and record a failure to distinguish them under relevance for both.

Calibration, freeze rules and revision history are in [README](README.md). This is a pre-freeze draft; historical runs retain their original rubric and scores.
