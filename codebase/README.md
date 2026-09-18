# VLearn Day 1 tutor — real AI prototype

The Streamlit app and evaluation runner use the same grounded, stateful tutor. The existing `checkpoint2_mockup.html` remains a scripted CP2 artifact.

## Run locally

Python **3.12+** is required by the locked dependencies (developed/tested with Python 3.13). From this repository root:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r codebase/requirements.txt
cp .env.example .env
# Edit .env locally; never commit credentials.
.venv/bin/python -m streamlit run codebase/app.py
```

Keep the supplied HTML at `data/d1-slide-hackathon.html`. It is already available locally and is intentionally ignored by Git under the assignment's data-sharing rules. A fresh checkout needs this source from the course pack; its checksum and page inventory are in `eval/source-manifest.json`. Startup fails clearly if the 29-page source is absent.

This implementation accepts the user's existing configuration:

```dotenv
OPENAI_API_KEY=your-local-key
OPENAI_BASE_URL=https://your-compatible-server.example/v1
OPENAI_MODEL=your-model-id
```

`TUTOR_API_KEY`, `TUTOR_BASE_URL`, and `TUTOR_MODEL`, if nonempty, override these aliases. Host-only compatible URLs automatically receive `/v1`; a custom path is preserved. Do not append `/chat/completions` yourself. Configuration is reread from `.env`; secrets never enter model prompts or logs.

The three `OPENAI_*` variables above are sufficient for the default compatible provider. Optional overrides can be added to `.env` when needed:

- `TUTOR_RESPONSE_FORMAT`: `json_object` (default), `json_schema` for providers that support strict structured output, or `none` for prompt-only JSON with local validation.
- `TUTOR_TOKEN_PARAMETER`: `max_completion_tokens` (default), or `max_tokens` for compatible providers that require it.
- `TUTOR_TEMPERATURE`: omitted unless configured.
- `TUTOR_TIMEOUT_SECONDS`: defaults to `45`.
- `TUTOR_MAX_OUTPUT_TOKENS`: defaults to `2200`.
- `TUTOR_SOURCE`: defaults to `data/d1-slide-hackathon.html`.
- `TUTOR_PROVIDER`: defaults to `compatible`. For native Gemini, use `gemini`, set `TUTOR_MODEL` and `GEMINI_API_KEY` (or `TUTOR_API_KEY`), and clear `OPENAI_BASE_URL` to use the native endpoint. For local Ollama, use `ollama`, set `TUTOR_MODEL`, and clear `OPENAI_BASE_URL` to use `http://localhost:11434/v1`; no key is needed. A nonempty `TUTOR_BASE_URL` overrides the endpoint in either case.

The configured compatible provider is the primary integration; native Gemini and local Ollama adapters require their own live verification.

## Try the canvas slice

1. Select page 10 and ask “LLM khác chatbot thế nào?”.
2. Say “Không hiểu.” The tutor should ask one focused diagnostic question.
3. Say “Mình tưởng LLM chính là chatbot.” It should explain the specific distinction differently, without adding a test.
4. Click **Tự kiểm tra** or ask “Hỏi mình một câu để kiểm tra mức hiểu.” Only this opt-in starts a check. Answer it, or say “Mình chưa hiểu” / request an example to return to teaching. Returning to help clears the pending check without grading or marking it skipped. A later check needs fresh opt-in. Only a correct answer to a pending check may mark that one concept verified; “Ok hiểu rồi” is not proof.
5. Try “Ý mình là trang 13 nói token.” The app should update the lesson selection and discard the old check.
6. Ask about MCP or detailed late chunking; the tutor should disclose the limits of Day 1. Open the citation expanders to inspect support.

The learner can skip, restart, correct context, or prepare an unsent TA question. Checks are optional; ordinary help does not repeatedly display an unverified status. Only an explicit skip request marks a check skipped. Two diagnostic questions and one repair are allowed per attempt; returning to help does not reset those budgets. A provider error preserves state and offers retry; it never becomes a fake tutor answer.

## Architecture and limits

### Manual replay testing

Open **Replay tests** in the app sidebar. Selecting a golden case previews its saved history, initial state, input, and expected behavior. Click **Chạy replay** to run that input through the same replay function as the CLI evaluator. Every click starts from the original case state; rerendering the page does not rerun the model. Some boundary cases are handled by the tutor's existing deterministic guards.

The response, sources, structural checks, and trace appear below the case. Review semantic quality yourself against the displayed expectations, and use **Tải kết quả JSON** to save the latest result. Results stay in this session unless downloaded; this page does not create an official scored run. Cases requiring live rollouts still need those separate runs.

The **app** sidebar entry remains the live chat. Replay results and state are separate from the live conversation; switching pages preserves the live chat, lesson selection, and quiz setting.

### Components

- `knowledge.py`: exact page/block IDs, source checksum, local lexical retrieval with selected-page context and topic aliases. No web or vector database.
- `turns.py`: one independent semantic routing call for free text distinguishes help, check answers, explicit opt-in, and skipping using recent history and a verbatim learner quote. Trusted UI buttons bypass routing. Malformed routing fails without changing the conversation. Classification can still be wrong; it requires live regression review, not only unit tests.
- `tutor.py`: the router supplies check permission; the response generator cannot grant itself permission or choose skip. Help requests clear the pending check before generation, without grading. Schema/evidence/state validation runs before display. The app validates source identity and literal quotations; human evaluation must still judge claim entailment and whether reply text follows the teaching policy.
- Before showing a correct understanding-check result, a separate focused model assessment must agree and quote the learner's actual answer. It uses the existing second-call budget; disagreement, malformed verification, or an exhausted budget produces an unverified fallback. This reduces false positives but is not a proof of learning.
- `state.py`: pending check, correction, counters, and understanding state. No persistent student profile.
- `model_client.py`: HTTP provider adapter; secrets stay in server-side headers. Free-text turns use at most three calls: one routing call plus the existing two-call teaching/retry/verification budget. Buttons bypass routing, so use at most two; explicit skip and active-quiz guards can use zero. Routing adds latency/cost and has no automatic retry.
- `app.py`: free-text Vietnamese chat, lesson/source panel, citation expanders, clear missing-configuration state. Conversation and developer trace stay only in the Streamlit session.
- `pages/1_Replay_tests.py`: isolated manual replay page, using the CLI replay function with saved case history/state. Expected behaviors are displayed for review and never sent to the tutor.
- `../eval/`: draft cases with provenance, real pilot/exploratory traces, review sheets, calibration, freeze, and scoring tools. Replay runs supply the case history/state/input; grading criteria are never loaded into the tutor prompt.

Explicit active-quiz requests and the “Tôi đang làm quiz” control trigger a safe redirect. Undisclosed quizzes cannot be reliably detected without VLearn integration. Prompt-based defenses are not a guarantee against all injections or hallucinations. The prototype does not establish durable learning gains or current real-world model prices.

The source has limitations (see `eval/source-quality.md`). All extracted claims remain scoped to the supplied lesson; suspected errors need TA review. Human-authored final golden cases and two independent human graders are still required by the course guide; agent-generated drafts are labelled accordingly.

## Verification

```sh
.venv/bin/python -m pytest
.venv/bin/python eval/run.py --validate-only
```

Unit/UI tests use explicit test doubles and are engineering checks, not model evaluation. Live evaluation commands and the current results index are documented in [eval/README.md](../eval/README.md).

Implementation references: [Streamlit chat](https://docs.streamlit.io/develop/api-reference/chat/st.chat_input), [session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state), [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest), [OpenAI-compatible JSON output format](https://developers.openai.com/api/docs/guides/structured-outputs), [Gemini JSON output](https://ai.google.dev/gemini-api/docs/structured-output).
