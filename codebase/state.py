"""Tutor response schema and conversation state.

Each tutor response selects exactly one predefined action:

* answer: Answer a clear question without adding an understanding check.
* diagnose: Ask a focused question to identify the learner's difficulty.
* explain_and_check: Explain, then ask a learner-requested understanding check.
* repair_and_check: Correct a wrong answer in an opted-in check, then check again.
* feedback: Respond to the learner's answer to a pending check.
* correct_context: Update or clarify the topic or page.
* skip: Skip the check without confirming understanding.
* abstain: Decline an answer when evidence or scope is insufficient.
* fallback: Stop an unsuccessful teaching attempt and offer next steps.
* quiz_redirect: Redirect an active-quiz answer request without revealing it.
* social: Handle greetings or social exchanges.

Action defines the complete set of valid values. The prompts describe when to
choose each action; runtime validation and state transitions enforce additional
constraints. An evaluation case's allowed_actions is a subset of acceptable
outcomes, not a sequence or a case-specific instruction sent to the model.
Matching that subset alone does not establish semantic quality.
"""

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

Action = Literal['answer', 'diagnose', 'explain_and_check', 'repair_and_check', 'feedback',
                 'correct_context', 'skip', 'abstain', 'fallback', 'quiz_redirect', 'social']


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Claim(StrictModel):
    claim: str = Field(min_length=1)
    block_id: str
    quote: str = Field(min_length=1)


class Check(StrictModel):
    question: str = Field(min_length=1)
    expected_concepts: list[str] = Field(min_length=1)


class TutorResponse(StrictModel):
    action: Action
    evidence_status: Literal['supported', 'partial', 'unsupported', 'ambiguous', 'not_needed']
    reply: str = Field(min_length=1, max_length=4000)
    source_ids: list[str]
    claims: list[Claim]
    gap_hypothesis: str | None
    check: Check | None
    check_assessment: Literal['correct', 'incorrect', 'unclear', 'not_applicable']
    corrected_page: int | None = Field(ge=1, le=29)
    representation: str | None
    reason_code: str

    def visible_text(self):
        return self.reply + ('\n\n' + self.check.question if self.check else '')


class Message(StrictModel):
    role: Literal['user', 'assistant']
    content: str
    source_ids: list[str] = Field(default_factory=list)
    action: str | None = None


class TutorState(StrictModel):
    messages: list[Message] = Field(default_factory=list)
    active_page: int | None = Field(default=10, ge=1, le=29)
    topic: str = ''
    hypothesized_gap: str | None = None
    last_explanation: str = ''
    representation_used: str | None = None
    diagnostic_count: int = Field(default=0, ge=0)
    repair_count: int = Field(default=0, ge=0)
    pending_check: Check | None = None
    check_result: Literal['unverified', 'correct', 'incorrect', 'skipped'] = 'unverified'
    quiz_status: bool = False
    attempt_id: str = Field(default_factory=lambda: uuid4().hex)

    def correct_context(self, page):
        self.active_page = page
        self.pending_check = None
        self.check_result = 'unverified'
        self.hypothesized_gap = None
        self.last_explanation = ''
        self.representation_used = None
        self.topic = ''
