# AI SPEC — VLearn Tutor: tìm đúng chỗ vướng

Track A · Path A1 · Nhóm K4-3B-E402-Transformer. **Prototype đã triển khai; spec và quality bar chưa khoá chính thức vì còn thiếu review/calibration độc lập của hai người.** Số liệu thực nằm trong [eval/](eval/README.md); xem [results.md](eval/results.md) để phân biệt structural checks với chấm chất lượng.

## §1. User & Job

- Job executor: học viên VLearn vừa nhận lời giải thích nhưng vẫn chưa hiểu.
- JTBD: xác định đúng chỗ mình còn thiếu/hiểu sai để tiếp tục học phần hiện tại.
- Pain: sau khi báo chưa hiểu, học viên thường phải tự tìm và mô tả lỗ hổng, hoặc tiếp tục điều khiển tutor qua nhiều lượt giải thích dài.
- Evidence: [canvas](canvas.md), [mining notes](cp1-mining-notes.md). Mining loại câu preset và false positive; tách hoạt động lớp ngày 30/07 để tránh chi phối. Mẫu chính 84 lượt/58 học viên; 77/84 tiếp tục `review_concept`, không có probing/validate theo nhãn đã phân tích.
- Chuỗi tiêu biểu: `T07023→T07024→T07026`, `T10924→T10927→T10928`, `T12534→T12535→T12536→T12537`; counterexample `T10815→T10816` cho thấy gap cụ thể có thể được sửa trực tiếp. Năm trích dẫn nguyên văn và phương pháp đếm nằm trong mining notes.
- Workaround: hỏi lại, yêu cầu ví dụ, sửa ngữ cảnh, tự diễn đạt giả thuyết sai. Dữ liệu chưa chứng minh ảnh hưởng lên điểm quiz hoặc mastery dài hạn.

## §2. Impact và quyết định chọn

| Ứng viên | Evidence/phạm vi | Quyết định |
|---|---|---|
| Chẩn đoán sau lời giải thích thất bại | 84 lượt/58 học viên; có chuỗi hỏi lại cùng chủ đề | Chọn: quyết định hỏi hay giảng trực tiếp đo được trong hội thoại. |
| Câu tự gõ không có căn cứ | Mining ghi 2.208 lượt/675 học viên ngoài 30/07 | Giữ citation/abstention làm guardrail. |
| Thay đổi mọi kiểu sư phạm | `review_concept` chiếm 7.177/8.267 lượt tự gõ trong mẫu chính | Backlog: phạm vi rộng; move label không đại diện đầy đủ chất lượng. |

## §3. Giải pháp tham chiếu

- Baseline quan sát: tutor VLearn trong data pack; không có toàn bộ production prompt/hạ tầng.
- Baseline thực nghiệm: prompt giải thích lại, dùng cùng model/nguồn/core với candidate. Đây là controlled prompt baseline, không phải đo lại production VLearn.
- CP2: [mockup](codebase/checkpoint2_mockup.html) với phản hồi scripted. Bản Streamlit thay quyết định/diễn đạt ở lõi bằng API thật.
- Nghiên cứu hai sản phẩm bên ngoài theo template: **chưa hoàn thành**; không dùng kiểm thử kỹ thuật để thay mục này.

## §4. Thiết kế và automation

**Lát cắt:** học viên báo chưa hiểu sau một lời giải thích → AI xác định gap đã rõ chưa → hỏi một câu chẩn đoán hoặc giải thích mục tiêu → kiểm tra ý vừa học hoặc fallback hữu ích.

Conditional automation: AI chọn move và viết câu trả lời; code giữ giới hạn nguồn, state, retry và quiz. Một check đúng chỉ chứng minh câu trả lời cho ý vừa kiểm tra. Không tự kết luận hiểu từ “ok/hiểu rồi”, hoặc skip.

Thật: free-text UI, API call, local source retrieval, conversation state, citations, correction, skip, bounded retry và eval runner. Scripted: boundary messages, synthetic/adapted replay histories và learner inputs trong live rollout; không trình bày chúng như lời học viên thật.

Nguồn duy nhất: `data/d1-slide-hackathon.html`, 29 trang. Chatlog dùng cho evidence/eval, không làm kho tri thức. Chỉ dạy kiến thức được đoạn nguồn hỗ trợ; câu ngoài phạm vi được nói rõ giới hạn, đề nghị chủ đề có nguồn hoặc soạn câu hỏi TA. Partial support phải phân định rõ. Mâu thuẫn trong nguồn không bị tự sửa bằng trí nhớ model.

Kiến trúc: Streamlit → `Tutor.step` → retrieval theo trang/từ khóa → LLM chọn move + JSON có claim/block/quote → validation → cập nhật state → UI. Eval gọi chính `Tutor.step`. Không có web browsing hay thực thi code học viên.

Giới hạn: ≤2 diagnostic và ≤1 repair mỗi attempt; lỗi API/JSON có tối đa 1 retry. Khi có pending check, model không được bỏ qua nó bằng một `explain_and_check` mới để né repair budget. Sửa ngữ cảnh bỏ kết quả cũ nhưng không reset budget. Restart do học viên chọn tạo attempt mới.

Trước khi hiển thị check đúng, một lượt xác minh hẹp phải đồng ý và trích đúng lời học viên. Lượt này dùng ngân sách call thứ hai đã có; bất đồng/lỗi/hết budget thì fallback chưa xác minh. Đây là guard giảm false positive, không phải chứng minh học viên đã hiểu lâu dài.

Non-goals: login/VLearn integration, hồ sơ mastery dài hạn, thay đổi lộ trình, internet knowledge, arbitrary uploads, gửi tin TA thật, production deployment.

### §4b. HAX/PAIR áp dụng

| Nguyên tắc | Áp dụng |
|---|---|
| G1 — làm rõ khả năng | UI ghi nguồn Day 1, có thể sai; cấu hình thiếu không giả vờ chat hoạt động. |
| G9 — hỗ trợ sửa | Đổi trang/chủ đề cập nhật lesson panel, xoá pending check/kết quả cũ. |
| G10 — bất định | Hỏi chẩn đoán khi gap mơ hồ; thiếu nguồn abstain/partial; hết budget fallback. |
| G11 — căn cứ | Citation mở nguồn; claim gắn block/quote; nguồn có vấn đề được cảnh báo. |
| G12 — tương tác gần | Giữ lời giải thích thất bại, gap, representation, pending check và recent messages. |
| PAIR — user control | Skip, restart, TA draft; không ép tiếp tục check. |

## §5. Bốn lớp chỗ khó và rủi ro

| Lớp | Tình huống | Hành vi mong muốn | Case |
|---|---|---|---|
| ① Nguồn | Chủ đề có nhắc nhưng thiếu công thức | Nêu giới hạn; không bổ sung từ trí nhớ | GS-011 |
| ① Nguồn | Lời trước cite sai trang/token sai | Đính chính claim và citation bằng page 13 | GS-012 |
| ① Nguồn | RAG có, late chunking không có | Trả phần supported, không giảng thuật toán thiếu | GS-013 |
| ② Mơ hồ | Không history/referent | Xin ý/trang | GS-014 |
| ② Mơ hồ | Đoạn chọn cắt cụt | Xin câu đầy đủ, không đoán từ retrieval | GS-015 |
| ② Mơ hồ | Hai lần vẫn không rõ gap | Dừng probing; fallback có bước tiếp | GS-016 |
| ③ Phạm vi | Thời tiết, ngoài bài | Nói không có nguồn | GS-017 |
| ③ Thẩm quyền | Xin đáp án quiz | Không đáp án/hint tương đương; redirect | GS-018 |
| ③ Injection | Yêu cầu bịa nguồn | Giữ biên nguồn/quyền hạn | GS-019 |
| ④ Giáo dục | Tự báo hiểu rồi | Không đánh dấu correct từ self-report | GS-020 |
| ④ Giáo dục | Bỏ qua check | skipped/unverified, không mastery | GS-021 |
| ④ Giáo dục | Biến tỷ lệ token ví dụ thành định luật | Sửa misconception và check | GS-022 |

GS-023 kiểm tra nguồn trang 18 có bất nhất số bước. GS-024 kiểm tra “không hiểu” chỉ nằm trong lời trích. Cite đúng vẫn có thể dạy sai; xem [source-quality](eval/source-quality.md). Không có guarantee chống mọi injection/hallucination.

## §6. Bốn đường trải nghiệm

- Happy: câu hỏi → giải thích → chưa hiểu → diagnostic → learner chỉ gap → targeted explanation/check → đánh giá câu trả lời cụ thể.
- Low-confidence: thiếu referent → xin trang/đoạn; hết budget → fallback, không ép guess.
- Failure/no evidence: partial/abstain, nguồn đọc được và TA draft; lỗi API giữ state, hiện retry, không giả câu trả lời AI.
- Correction: cập nhật trang/chủ đề, bỏ check/kết quả trước, tái xét input theo nguồn mới.
- Quiz: explicit flag/request được chặn đáp án; undisclosed quiz không thể biết chắc nếu chưa tích hợp VLearn.
- Citation: ID/quote kiểm bằng code; entailment và pedagogical fit cần chấm tay.

## §7. Đánh giá và quality bar

Ba chiều: Factuality, Relevance, Sensitivity. Định nghĩa kiểm chứng được trong [rubric](eval/rubric.md).

Bộ 24 **draft**: 10 normal + 3 mỗi lớp rủi ro + 2 rare. 13 case adapted từ chain thật, ghi rõ thay đổi; 23 case có history. Sáu case có thêm live rollout dùng output thật làm lịch sử. Cả hội thoại tính một case. Gold/reference không vào prompt tutor.

**Bar đề xuất, chưa freeze:** ≥21/24 và ≥5/6 live rollout, không critical violation. Critical gồm claim/nguồn bịa, lộ đáp án quiz, xác nhận hiểu sai, hoặc injection phá biên. Lỗi API giữ nguyên mẫu số. Automatic structural checks không được báo thành factuality accuracy hoặc quality-bar pass.

Pilot, taxonomy và mọi lượt exploratory được lưu trong [eval](eval/README.md). [Results index](eval/results.md) ghi từng run/version, không chọn completion đẹp nhất. Chỉnh rubric trước freeze có changelog, không sửa kết quả cũ. Toàn bộ bộ đã được inspect để sửa lỗi nên là regression suite, không còn held-out.

Còn thiếu: con người review/author final cases, hai người chấm độc lập cùng 5 output, làm rõ định nghĩa, rồi dùng `eval/freeze.py` khoá trước scored run chính thức. Agent review không giả làm human calibration. Không tuyên bố cải thiện điểm học tập/mastery từ kết quả này.

## §8. Phân công và deliverables

- Trần Kim Phương: evidence/source, code/provider/core/UI.
- Nguyễn Minh Thái: coverage/provenance, golden review, rubric, đo và video.
- Trần Gia Thành: flow/spec, chấm độc lập với Thái, demo/validation.
- Willing users theo canvas: Bùi Hải Nam, Nguyễn Minh Quyền. **Chưa thực hiện validation**, chưa có quote feedback của họ.
- AI-assisted implementation/initial drafts: Codex. Không gán công việc review chưa diễn ra cho thành viên nhóm.
- Hướng dẫn: [codebase/README.md](codebase/README.md). Outputs mới ở repo này; chưa commit, publish hay nộp checkpoint tự động.

## §9. Changelog

| Thời điểm | Thay đổi | Evidence |
|---|---|---|
| 18/09/2026 | Core, Streamlit, 24 draft cases | Approved plan, canvas, Day 1 source |
| 18/09/2026 | Normalize host URL với `/v1` | Pilot HTTP 404; giữ run gốc |
| 18/09/2026 | Focused probe, không đoán referent, không offer ngoài nguồn | Pilot GS-003/015/011 |
| 18/09/2026 | Flag page 15 B006, giữ source gốc để review | Pilot GS-011 |
| 18/09/2026 | Partial/correction allowlist trước freeze | GS-013/012; giữ snapshot cũ |
| 18/09/2026 | Retry feedback; chặn thay pending check để né counter | Exploratory GS-009 |
| 18/09/2026 | Verifier hẹp trước khi đánh dấu check correct | Run 7d57e0 GS-009/010 có false-positive praise; giữ lỗi làm evidence |

Spec còn các mục chờ người thật ở trên; chưa đủ điều kiện gọi là submission hoàn chỉnh.
