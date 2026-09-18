# AI SPEC — VLearn Tutor: chẩn đoán chỗ vướng trước khi giải thích lại · Nhóm Transformer · Zone C1
Hướng: [ x ] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [ x ] Tối ưu tính năng có sẵn  [ ] Tính năng mới

## §1. User & Job

- Job executor: học viên VLearn vừa nhận lời giải thích nhưng vẫn chưa hiểu.
- JTBD: xác định đúng chỗ mình còn thiếu/hiểu sai để tiếp tục học phần hiện tại.
- Pain: sau khi báo chưa hiểu, học viên thường phải tự tìm và mô tả lỗ hổng, hoặc tiếp tục điều khiển tutor qua nhiều lượt giải thích dài.
- Evidence: [canvas](canvas.md), [mining notes](cp1-mining-notes.md). Mining loại câu preset và false positive; tách hoạt động lớp ngày 30/07 để tránh chi phối. Mẫu chính 84 lượt/58 học viên; 77/84 tiếp tục `review_concept`, không có probing/validate theo nhãn đã phân tích.
- Chuỗi tiêu biểu: `T07023→T07024→T07026`, `T10924→T10927→T10928`, `T12534→T12535→T12536→T12537`; counterexample `T10815→T10816` cho thấy gap cụ thể có thể được sửa trực tiếp. Năm trích dẫn nguyên văn và phương pháp đếm nằm trong mining notes.
- Workaround: Người dùng đang phải hỏi lại, yêu cầu ví dụ

## §2. Impact & quyết định chọn

| Ứng viên | Bao nhiêu người/lượt | Tín hiệu/cost quan sát được | Khả thi trong hackathon | Quyết định |
|---|---|---|---|---|
| Không đổi chiến lược khi học viên vẫn chưa hiểu | Phân tích ban đầu: 127 lượt/76 học viên; K4: 30 lượt/21 học viên **[1]** | Ban đầu: 117/127 là `review_concept` **[1]**; 11 lượt follow-up K4 trong các chuỗi đã giữ có 0 probing/validate theo nhãn và reply trung vị 1.353 ký tự | Cao: detector + policy + comprehension check | **Chọn** |
| Trả lời không có nguồn truy vết | Ban đầu: 3.552/10.427 lượt tự gõ theo rule bảo thủ **[1]** | Độ phủ lớn; có nguy cơ học sai hoặc giảm niềm tin, chưa đo hậu quả thực tế | Cao | Loại vì trùng sát ví dụ có sẵn trong đề; khó chứng minh discovery độc lập. Giữ citation/abstention làm guardrail. |
| Không tuân thủ yêu cầu “ngắn gọn” | 85 lượt/41 học viên ở phân tích ban đầu **[1]** | Ban đầu: reply trung vị 892 ký tự; 58/85 vượt 500 ký tự **[1]** | Rất cao | Đưa vào backlog; “ngắn” còn phụ thuộc loại câu hỏi |
| Không đáp ứng nhu cầu ôn tập cá nhân | 191 lượt/95 học viên cho bốn câu lặp | 188/191 thuộc K3; cần thêm progress/quiz data để xác nhận nhu cầu chưa được đáp ứng | Trung bình | Loại vì phụ thuộc dữ liệu ngoài chatlog |

Hướng "Không đổi chiến lược khi học viên vẫn chưa hiểu" được chọn vì có pattern lặp ở cả K3 và K4, có failure cụ thể để cải thiện, và quyết định trung tâm đủ nhỏ để build/đo trong thời gian sự kiện.

**[1] Trạng thái evidence:** Kiểm tra lại CSV xác nhận mẫu đã đọc tay là **136 lượt/80 học viên**, gồm K4 **33 lượt/22 học viên**, với **126/136** `review_concept`. Tách hoạt động lớp ngày 30/07 còn **84 lượt/58 học viên**, **77/84** `review_concept`, **0/84** probing/validate — đây là mẫu chính dùng ở §1.

## §3. Giải pháp tương tự đã nghiên cứu

Nghiên cứu tài liệu và demo chính thức, đối chiếu ngày 18/09/2026; chưa có thử nghiệm trực tiếp trên tài khoản của hai sản phẩm. “Đáng học”, “đáng né” và “mình khác gì” là phân tích thiết kế của nhóm, không phải kết quả đo so sánh hiệu quả học tập. Hai sản phẩm được chọn vì đại diện cho hai yêu cầu của lát cắt: dẫn dắt người học tìm gap và trả lời có căn cứ truy vết được.

### §3a. ChatGPT — OpenAI

Tham chiếu [hướng dẫn sử dụng ChatGPT của OpenAI](https://learn.chatgpt.com/docs/use-chatgpt). Phân tích tập trung vào flow Chat dùng để hỏi và làm rõ kiến thức qua hội thoại; không đánh đồng flow này với mọi chế độ học tập hay cấu hình tùy chỉnh của ChatGPT. Ví dụ yêu cầu học tập trong bảng là cách nhóm áp dụng flow tài liệu mô tả, chưa phải transcript thử nghiệm trực tiếp.

| Câu hỏi | Phân tích và quyết định cho nhóm |
|---|---|
| Flow của họ? | Người dùng mở Chat → nhập câu hỏi hoặc đưa ngữ cảnh/tài liệu → nhận giải thích → review, bổ sung thông tin hoặc yêu cầu sửa hướng trả lời.|
| Điều đáng học? | Hội thoại tự nhiên, cho phép bổ sung ngữ cảnh và yêu cầu điều chỉnh cụ thể; tài liệu OpenAI cũng khuyến khích kiểm tra claim và đối chiếu nguồn gốc. Áp dụng: giữ free-text, lịch sử gần, nút “Mình chưa hiểu”/“Cho ví dụ” và citation để học viên kiểm tra lời giải thích. |
| Điều đáng né? | Tình huống cần tránh: sau một lời giải thích, học viên chỉ nói “Mình chưa hiểu vấn đề”, tutor giải thích thẳng một lần nữa mà không hỏi để xác định chỗ vướng. Khi đó, tutor đang tự chọn nguyên nhân: thiếu định nghĩa, hiểu sai quan hệ hay chưa biết áp dụng; đổi câu chữ hoặc thêm ví dụ có thể vẫn không trúng gap. Học viên phải tiếp tục hỏi lại hoặc tự chẩn đoán cho tutor. Áp dụng: nếu gap còn mơ hồ, hỏi một câu phân biệt 2–3 khả năng trước khi giải thích; gap rõ thì trả lời trực tiếp. Đây là rủi ro cần kiểm thử trên ChatGPT, chưa có transcript đối chứng để kết luận hành vi luôn xảy ra. |
| Mình khác gì? | Prototype chuyên biệt cho học viên VLearn vừa báo chưa hiểu, cố định nguồn Day 1 và quyết định hỏi chẩn đoán hay giải thích đúng một gap. Core giữ pending check, tối đa 2 diagnostic/1 repair mỗi attempt và quiz guard; citation gắn block/quote được code kiểm. Khác biệt là các quy tắc được triển khai cho lát cắt này; không khẳng định ChatGPT không thể làm tương tự khi được cấu hình, hay nhóm có hiệu quả học tập cao hơn. |

### §3b. NotebookLM / Gemini Notebook — Google

Google hiện gọi sản phẩm là Gemini Notebook, trước đây là NotebookLM, theo [trang sản phẩm chính thức](https://workspace.google.com/intl/en_ca/products/gemini-notebook/). Phân tích tập trung vào chat trên nguồn đã chọn và chế độ Learning Guide trong [hướng dẫn sử dụng chat](https://support.google.com/gemininotebook/answer/16179559?hl=en), không bao quát các tính năng agentic khác.

| Câu hỏi | Phân tích và quyết định cho nhóm |
|---|---|
| Flow của họ? | Tạo/mở notebook → thêm và chọn nguồn → cấu hình Learning Guide, độ dài phản hồi → hỏi về tài liệu → đọc câu trả lời, mở citation để xem đoạn gốc trong ngữ cảnh. |
| Điều đáng học? | Đặt nguồn cạnh câu trả lời, cho người học tự kiểm tra căn cứ và điều chỉnh cách phản hồi. Áp dụng: panel bài học theo trang, citation mở lại nguồn; mỗi claim quan trọng phải gắn block và quote. |
| Điều đáng né? | Tình huống cần tránh: học viên nói “Mình chưa hiểu vấn đề”, tutor tiếp tục giải thích/tóm tắt tài liệu có citation mà chưa hỏi học viên vướng ở ý nào. Câu trả lời có thể đúng nguồn nhưng vẫn không giải quyết được misconception; citation xác minh căn cứ kiến thức, không xác định nguyên nhân học viên chưa hiểu. Áp dụng: giữ grounding, thêm bước chẩn đoán khi gap mơ hồ rồi giải thích đúng gap và kiểm tra lại. Đây là rủi ro cần kiểm thử trên NotebookLM/Gemini Notebook, chưa có transcript đối chứng để kết luận Learning Guide luôn bỏ qua việc hỏi lại. |
| Mình khác gì? | Nguồn được cố định ở 29 trang Day 1, không để người dùng thêm nguồn tùy ý. Flow thiết kế quanh gap, cách giải thích trước, pending check và giới hạn retry; kết thúc bằng đánh giá câu trả lời cho một ý hoặc fallback chưa xác minh. Khác biệt là phạm vi và quy tắc prototype, chưa có bằng chứng nhóm tốt hơn Learning Guide. |

**Vấn đề chung cần đối chiếu:** “Chưa hiểu” là tín hiệu lời giải thích trước chưa giúp được người học, chưa phải mô tả đủ rõ của gap. Nếu tutor chuyển ngay từ tín hiệu này sang một lời giải thích mới, bước xác định nguyên nhân bị bỏ qua: nội dung nhiều hơn nhưng có thể vẫn lệch chỗ vướng. Với ChatGPT, cần kiểm tra xem phản hồi có làm rõ gap hay chỉ diễn đạt lại; với NotebookLM/Gemini Notebook, cần kiểm tra cả độ trúng gap bên cạnh độ đúng nguồn. Chưa có thử nghiệm trực tiếp để gán lỗi này cho mọi phản hồi của hai sản phẩm; evidence hiện có cho hành vi giải thích tiếp nằm ở tutor VLearn trong mining notes.

**Ví dụ kiểm thử đề xuất — chưa phải hội thoại đã chạy:** sau lời giải thích về context window, học viên nói “Mình chưa hiểu vấn đề”. Phản hồi cần tránh là giảng lại cả context window ngay. Phản hồi mong muốn là “Bạn đang vướng ở giới hạn lượng nội dung model nhìn thấy, hay vì sao nội dung ở giữa dễ bị bỏ sót?”; sau câu trả lời của học viên mới giải thích đúng ý đó và đặt một check ngắn. Nếu học viên đã nói “Mình tưởng context window là trí nhớ vĩnh viễn”, gap đã rõ và có thể giải thích trực tiếp, không cần hỏi lại máy móc.

**Quyết định rút ra:** kết hợp hỏi chẩn đoán có mục tiêu với câu trả lời truy vết về bài học; tránh hỏi thừa, giảng lại toàn bài và xác nhận hiểu từ lời tự báo. Evidence `T10815→T10816` hỗ trợ nhánh gap rõ; `T12534→T12535→T12536→T12537` cho thấy cần cho học viên sửa ngữ cảnh trước khi giảng tiếp ([mining notes](cp1-mining-notes.md)).

**Baseline nội bộ để đánh giá:** tutor VLearn trong data pack là baseline quan sát, không có toàn bộ production prompt/hạ tầng. Baseline thực nghiệm là prompt giải thích lại dùng cùng model/nguồn/core với candidate, không phải đo lại production VLearn. [Mockup CP2](codebase/checkpoint2_mockup.html) có phản hồi scripted; bản Streamlit dùng API thật ở quyết định/diễn đạt lõi.

## §4. Thiết kế và automation

**Lát cắt một câu:** Học viên VLearn vừa báo “vẫn chưa hiểu” sau một lời giải thích cần tìm đúng chỗ vướng, AI quyết định gap đã đủ rõ để giải thích tiếp hay cần một câu chẩn đoán, để học viên nhận giải thích đúng một gap và trả lời một câu kiểm tra ý vừa học hoặc nhận bước tiếp theo khi chưa thể xác minh.

**Quy tắc quyết định:** gap mơ hồ nhưng có ngữ cảnh thì hỏi một câu ngắn phân biệt 2–3 khả năng; thiếu ngữ cảnh thì xin trang/đoạn thay vì đoán. Gap đã rõ thì giải thích trực tiếp bằng cách biểu đạt khác lượt trước, không bắt buộc hỏi thêm. Không đủ nguồn thì trả phần có căn cứ và nói rõ phần thiếu, hoặc abstain. Câu hỏi kiến thức đầu tiên rõ và có nguồn vẫn được trả lời ngắn, không tự kích hoạt chẩn đoán khi chưa có tín hiệu thất bại. Đây là policy trong [prompt candidate](codebase/prompts/tutor.md); mức tuân thủ cần chấm theo §7.

**Mức automation: conditional automation.** AI tự chọn move và viết câu trả lời trong biên nguồn; code kiểm schema/citation và giữ state, ngân sách retry, quiz guard. Học viên giữ quyền chọn/sửa trang, mô tả lại gap, bỏ qua check, restart và tự mang bản nháp đến TA. Quyết định “đã đủ căn cứ để giảng” là định tính của model qua `evidence_status` và state, không có ngưỡng confidence xác suất đã được calibration.

**Lý do theo cost-of-error:**

| Quyết định sai | Chi phí/hậu quả | Cách giới hạn automation |
|---|---|---|
| Đoán sai gap rồi giảng tiếp | Tốn thêm lượt đọc/hỏi lại, có thể củng cố misconception; chưa đo được ảnh hưởng lên learning outcome. | Gap mơ hồ phải làm rõ; mỗi lượt chỉ xử lý một gap, cho phép sửa ngữ cảnh. |
| Hỏi thêm khi gap đã rõ | Thêm một lượt tương tác và chờ API; học viên có thể nản vì tutor hỏi vòng. | Cho phép giải thích trực tiếp; tối đa 2 diagnostic mỗi attempt, mỗi lượt tối đa một câu hỏi. |
| Báo hiểu đúng khi học viên trả lời sai hoặc chỉ nói “ok” | Tạo sự tự tin sai để học viên tiếp tục học. Đây là lỗi có chi phí cao hơn việc giữ trạng thái chưa xác minh. | Chỉ đánh giá khi có pending check và câu trả lời thực; cần lượt xác minh hẹp đồng ý trước khi hiển thị đúng. Một check đúng không được suy thành mastery. |
| Bịa nguồn/giảng ngoài bài hoặc lộ đáp án quiz | Học sai và làm mất tính toàn vẹn của đánh giá. | Giới hạn nguồn, kiểm ID/quote, abstain/partial và quiz redirect. Citation đúng hình thức chưa bảo đảm claim được nguồn hỗ trợ; vẫn cần chấm tay. |

Không chọn automate toàn bộ việc kết luận hiểu bài vì chi phí xác nhận sai cao và thiếu dữ liệu mastery; cũng không yêu cầu TA duyệt từng phản hồi vì lát cắt cần trợ giúp ngay. Bản nháp TA là fallback do học viên chủ động sử dụng. Giả định một câu chẩn đoán giúp giảm giảng lệch vẫn cần validation, chưa được coi là kết quả đã chứng minh.

**Mức prototype: Working, chạy localhost.** Thật: free-text UI, API call, local source retrieval, conversation state, citations, correction, skip, bounded retry và eval runner. 

Nguồn kho tri thức duy nhất: `data/d1-slide-hackathon.html`, 29 trang, chỉ nằm ở local, không commit public. Chatlog dùng cho evidence/eval, không làm kho tri thức. Chỉ dạy kiến thức được đoạn nguồn hỗ trợ; câu ngoài phạm vi được nói rõ giới hạn, đề nghị chủ đề có nguồn hoặc soạn câu hỏi TA. Partial support phải phân định rõ. Mâu thuẫn trong nguồn không bị tự sửa bằng trí nhớ model.

Kiến trúc: Streamlit → `Tutor.step` → retrieval theo trang/từ khóa → LLM chọn move + JSON có claim/block/quote → validation → cập nhật state → UI. Eval gọi chính `Tutor.step`. Không có web browsing hay thực thi code học viên.

Trước khi hiển thị check đúng, một lượt xác minh hẹp phải đồng ý và trích đúng lời học viên. Lượt này dùng ngân sách call thứ hai đã có; bất đồng/lỗi/hết budget thì fallback chưa xác minh. Đây là guard giảm false positive, không phải chứng minh học viên đã hiểu lâu dài.

**Non-goals — không build trong lát cắt này:**

1. Login và tích hợp VLearn production: học viên chọn trang và trạng thái quiz trong UI cục bộ; không tự biết bài/quiz chưa khai báo.
2. Hồ sơ mastery dài hạn, chấm trình độ toàn khóa hoặc dự đoán điểm: state chỉ ở phiên và kết quả chỉ cho ý vừa kiểm tra.
3. Tự thay đổi lộ trình học hoặc tạo khóa học hoàn chỉnh: chỉ giúp tháo một gap trong bài hiện tại.
4. Kiến thức internet và upload tùy ý: dùng duy nhất nguồn Day 1; không browsing hay thực thi code học viên.
5. Làm thay quiz đang mở hoặc đưa hint tương đương đáp án: redirect về ôn khái niệm sau quiz.
6. Gửi tin TA thật hoặc triển khai production: chỉ tạo bản nháp chưa gửi; chưa có handoff tích hợp hay hạ tầng vận hành production.

### §4b. HAX/PAIR áp dụng

Đối chiếu mã/nghĩa theo [Microsoft HAX Design Library](https://www.microsoft.com/en-us/haxtoolkit/library/), cùng hai chương PAIR [Explainability + Trust](https://pair.withgoogle.com/chapter/explainability-trust/) và [Feedback + Control](https://pair.withgoogle.com/chapter/feedback-controls/). Tên nguyên tắc dưới đây được diễn giải bằng tiếng Việt. Bảng chỉ ra cơ chế hiện có và cách review; không khẳng định tất cả kịch bản đã đạt.

| Nguyên tắc HAX/PAIR | Áp cụ thể vào prototype | Cách kiểm chứng / giới hạn |
|---|---|---|
| HAX G1 — công bố khả năng và phạm vi | Onboarding/sidebar ghi chỉ dựa slide Day 1, 29 trang; quiz control nói rõ không cung cấp đáp án. | Mở app, kiểm onboarding và hỏi ngoài bài. Không ngụ ý tutor truy cập được tài khoản VLearn. |
| HAX G2 — giúp người dùng hiểu giới hạn chất lượng | UI cảnh báo AI có thể sai; thông báo check đúng chỉ cho ý vừa kiểm tra. | Đọc thông báo khi check đúng và khi thiếu cấu hình. Chưa công bố accuracy đã calibration. |
| HAX G8 — cho phép bỏ qua trợ giúp không mong muốn | Nút “Bỏ qua kiểm tra” khi có pending check; state chuyển skipped. | Bỏ qua check phải hiện chưa xác nhận mức hiểu, không báo correct; tham chiếu GS-021. |
| HAX G9 — cho phép sửa sai thuận tiện | Chọn lại trang hoặc nhắn sửa ngữ cảnh; cập nhật lesson panel, bỏ pending check/kết quả/gap cũ. | Thử “Ý mình là trang 13 nói token”; lượt sau phải dùng ngữ cảnh mới. Không reset budget chỉ vì sửa trang. |
| HAX G10 — thu hẹp trợ giúp khi mục tiêu chưa rõ | Hỏi chẩn đoán có mục tiêu; xin trang/đoạn khi thiếu referent; hết budget chuyển fallback. | Replay GS-014/015/016; không đoán chủ đề từ top retrieval. Policy do model thực hiện, cần chấm nội dung. |
| HAX G12 — giữ ngữ cảnh tương tác gần | `TutorState` giữ lời giải thích trước, giả thuyết gap, representation, pending check và history; lượt tiếp dùng history gần. | Chạy chuỗi chưa hiểu → nêu misconception → giải thích/check; review xem có đổi cách giảng thay vì lặp lại. Chỉ nhớ trong phiên. |
| PAIR Explainability + Trust — minh bạch căn cứ để người học điều chỉnh độ tin | Panel bài và citation mở trang; claim gắn block/quote, nguồn có cảnh báo được hiển thị. | Mở citation và đối chiếu claim trong ngữ cảnh; ID/quote do code kiểm, entailment vẫn cần chấm tay. Citation là căn cứ kiến thức, không phải giải thích toàn bộ quyết định của model. |
| PAIR Feedback + Control — cân bằng tự động hóa với quyền điều khiển | Học viên sửa context, skip, restart hoặc tự dùng bản nháp TA; UI báo lịch sử chỉ ở phiên và nháp chưa gửi. | Skip không suy thành hiểu đúng; restart tạo attempt mới; không có hành vi gửi TA tự động. Feedback chỉ ảnh hưởng phiên, không tự train/cá nhân hóa model dài hạn. |

Bằng chứng triển khai: [UI](codebase/app.py), [state](codebase/state.py), [core tutor](codebase/tutor.py), [policy](codebase/prompts/tutor.md). Bộ case và tiêu chí review nằm ở [eval/](eval/README.md); kiểm thử kỹ thuật không thay cho chấm chất lượng hay validation người dùng.

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

## §6. Bốn đường trải nghiệm

- Happy: câu hỏi → giải thích → chưa hiểu → diagnostic → learner chỉ gap → targeted explanation/check → đánh giá câu trả lời cụ thể.
- Low-confidence: thiếu referent → xin trang/đoạn; hết budget → fallback, không ép guess.
- Failure/no evidence: partial/abstain, nguồn đọc được và TA draft; lỗi API giữ state, hiện retry, không giả câu trả lời AI.
- Correction: cập nhật trang/chủ đề, bỏ check/kết quả trước, tái xét input theo nguồn mới.
- Quiz: explicit flag/request được chặn đáp án; undisclosed quiz không thể biết chắc nếu chưa tích hợp VLearn.
- Citation: ID/quote kiểm bằng code; entailment và pedagogical fit cần chấm tay.

## §7. Đánh giá và quality bar

Hai chiều: Factuality (đúng căn cứ) và Relevance (đúng nhu cầu và ngữ cảnh hội thoại). Định nghĩa kiểm chứng được trong [rubric](eval/rubric.md).

Bộ 24 **draft**: 10 normal + 3 mỗi lớp rủi ro + 2 rare. 13 case adapted từ chain thật, ghi rõ thay đổi; 23 case có history. Sáu case có thêm live rollout dùng output thật làm lịch sử; kết quả được báo cáo riêng, không có ngưỡng pass riêng cho live rollout. Cả hội thoại tính một case. Gold/reference không vào prompt tutor.

**Bar đề xuất:** ≥80% case pass (ít nhất 20/24), không có critical violation trên toàn bộ bộ đánh giá. Critical gồm claim/nguồn bịa, lộ đáp án quiz, xác nhận hiểu sai, hoặc injection phá biên.

## §8. Phân công và deliverables

- Trần Kim Phương: evidence mining, điều phối tiến độ, review spec, làm prototype chạy localhost.
- Nguyễn Minh Thái: golden case, rubric, PDF slides.
- Trần Gia Thành: Thiết kế luồng hoạt động, dựng mockup sơ đồ luồng và quay video màn hình mockup, chỉnh sửa specs
- Willing users theo canvas: Bùi Hải Nam, Nguyễn Minh Quyền.

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
| 18/09/2026 | Hoàn thiện §3–§4; chọn ChatGPT và NotebookLM/Gemini Notebook làm hai sản phẩm tham chiếu; chốt lát cắt, non-goals, conditional automation và 8 nguyên tắc HAX/PAIR | Tài liệu chính thức dẫn tại §3/§4b, đối chiếu UI/core/prompt hiện có và mining notes. Đây là desk research, chưa phải thử nghiệm đối chứng trực tiếp, đo hiệu quả học tập hoặc validation người dùng. |
| 18/09/2026 | Làm rõ rủi ro “chưa hiểu → giải thích thẳng, không chẩn đoán” ở cả hai giải pháp tham chiếu; bổ sung ví dụ kiểm thử và điều kiện gap rõ không cần hỏi thêm | Yêu cầu cập nhật của nhóm; evidence VLearn trong mining notes. Ví dụ đối chiếu ChatGPT/NotebookLM chưa chạy, không ghi thành kết quả quan sát. |

Spec còn các mục chờ người thật ở trên; chưa đủ điều kiện gọi là submission hoàn chỉnh.
