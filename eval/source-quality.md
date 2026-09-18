# Day 1 source inventory and limitations

Canonical runtime file: `data/d1-slide-hackathon.html` in this repo. It was byte-identical to the assignment copy when implementation began. `source-manifest.json` records the exact SHA-256 and all 29 page IDs/anchors; extraction retains stable block IDs, lists, captions and table rows.

- **Page 10:** directly supports LLM as underlying model and chatbot as a product, with several applications of one model. Decoder-only is mentioned; detailed architecture/matrix formulas are not supplied.
- **Page 13:** token counts/rates are examples for the named tokenizer, not a universal token-to-word conversion. Exact counts depend on tokenizer and text.
- **Pages 14–16:** support bounded context and selecting relevant material. Mentioning retrieval does not supply a late-chunking algorithm.
- **Page 15, block B006:** wording about attention and “the T in GPT” is flagged as potentially misleading. It remains visible in the original source viewer, but is excluded from model evidence and valid claim blocks pending TA review. The tutor must acknowledge the source issue rather than reuse this wording as a definition.
- **Page 18:** introduction says three steps, later text enumerates a fourth. The tutor should acknowledge that inconsistency rather than select one authoritative count.
- **Pages 23–24:** support agent tools and workflow at a conceptual level. They do not provide an MCP explanation or permission to execute real actions.
- **Pages 25–27:** figures/model names are slide content, with illustrative and time-sensitive claims. Do not claim current pricing or availability.
- **Image references:** some are missing or decorative. Alt text/captions are retained and labelled descriptions from HTML, not verified visual evidence. No reconstruction of unseen graphics.
- **Truth versus source fidelity:** a citation is not proof of real-world truth. Source errors/oversimplifications require TA review; runtime scope must remain explicit. The suite is a grounding/teaching regression set for this supplied deck, not a general scientific fact benchmark.

Automatic checks verify IDs, supplied evidence membership and exact quoted text. Human reviewers still need to judge whether the passage supports the claim, analogy and understanding check.
