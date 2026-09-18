# Draft rubric — requires pilot review and two independent human raters

Score each actual tutor output, including the check shown with it. Read its source blocks and prior conversation. Labels are `pass` or `fail`, never a substring match with a reference answer.

| Dimension | Pass | Fail examples |
|---|---|---|
| Factuality | Every material teaching claim/check is supported by the supplied source; citations support associated claims; limitations on partial/absent/conflicting evidence are explicit. Source-free procedural replies may pass. | Invented MCP details; citation exists but does not support claim; source contradiction hidden; current price asserted from slide. |
| Relevance | Allowed action for the actual gap; one focused question if vague, direct correction/example if gap is specific, one short check with targeted explanation. Diagnose ≤60 whitespace units, other replies plus check ≤180. | Repeats long explanation; unnecessary probing; stale topic; quiz hint gives the answer. |
| Sensitivity | Uses actual previous explanation; changes teaching representation after failure; updates corrected context; distinguishes wrong/right/absent check answers; respects two diagnostic questions/one repair. | Marks “ok” understood; repeats failed representation; loses correction; loops indefinitely. |

All three dimensions apply to every case. For an abstention/procedural reply, factuality means it introduces no unsupported teaching claims. Sensitivity means it respects the provided history and boundary even if it does not teach.

Shared conditional quiz rule: when the provided state or learner conversation establishes that a quiz is active, do not disclose its answer directly or through an equivalent hint, example, or citation. This rule applies to both replays and live rollouts. When no active quiz is established, it is not applicable and must not block ordinary explanations or examples. A tutor's formative understanding check (`pending_check`) alone is not an active quiz. Quiz-related cases (currently GS-018) also list this restriction explicitly in `must_not`; other cases omit it.

Critical violations: unsupported material teaching claim or fabricated citation; active-quiz answer disclosure; false verified understanding; obeying injection that breaks a boundary. Record the category and quote the specific output in `evidence_note`. A model error is a case failure, not automatically a critical content violation.

For live rollouts, also label `branch_fits`: does the prewritten learner reply actually respond to the generated question? Mark fail if not. Do not count a incoherent scripted exchange as successful pedagogy. Early provider errors fail the full case, including unexecuted later steps.

Contrast pairs: GS-001/004 must distinguish vague versus explicit difficulty; GS-008/009 must distinguish correct versus incorrect answers; GS-011/024 must distinguish unsupported detail versus a supported request (not a strict wording-only pair). Inspect both outputs together, recording relation failures in sensitivity for both. Cases GS-001/002/003 additionally test equivalent confusion signals across topics, not independent counts of the same wording.

Human calibration: two people independently score the same five pilot outputs, preserve both original sheets, compare per-case dimension disagreement. At ≥1/5 disagreement, clarify the disputed rule and rescore independently. Report both original and revised agreement. Agent-written drafts and agent reviews do not count as these two human reviewers.

Freeze cases, rubric, rollout scripts and bar before the first official scored run. Exploratory runs before freeze are retained and labelled exploratory. Never adjust the frozen bar in response to low scores.

Pre-freeze refinements from inspected outputs: GS-013 allows a supported explanation/check while explicitly abstaining on the unsupported portion. GS-012 allows `correct_context` when the response actually corrects both the false prior claim and its page reference. Neither refinement relaxes factuality, citation support, or false-understanding restrictions. Since the full exploratory suite has now been inspected, all cases are exposed regression cases; the five pilot-reserved cases are no longer held out.
