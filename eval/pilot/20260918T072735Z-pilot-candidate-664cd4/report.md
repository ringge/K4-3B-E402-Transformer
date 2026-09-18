# Evaluation run 20260918T072735Z-pilot-candidate-664cd4

Phase: **pilot** · Prompt: **candidate**

Automatic structural checks: **14/15 conversation cases**.
**Quality score and Ship/Limited/Hold decision: pending human grading.**
An automatic pass does not establish semantic grounding or good pedagogy. All errors remain in the denominator.

## GS-001 · replay · step 1

**Input:** Không hiểu.

**Actual output:**

Mình chưa rõ bạn đang vướng ở chỗ nào. Bạn thấy khó ở ý "LLM là nền chung" hay ở ý "chatbot chỉ là lớp áo bên ngoài"?

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["diagnose"], "must": ["Hỏi một câu phân biệt gap: model/sản phẩm hoặc một model/nhiều ứng dụng", "Không giải thích lại ngay"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P010

## GS-002 · replay · step 1

**Input:** ko hiểu lắm, giải thích dễ hiểu hơn

**Actual output:**

Mình chưa rõ bạn đang vướng ở đâu trên trang 13 về token. Bạn thấy khó ở chỗ nào: (a) vì sao model cắt chữ thành mảnh thay vì đọc từ, hay (b) vì sao tiếng Việt tốn nhiều token hơn?

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["diagnose"], "must": ["Nhận tín hiệu chưa hiểu dù viết tắt", "Hỏi một câu dựa vào token/từ"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P013, D1-P018, D1-P016, D1-P014

## GS-003 · replay · step 1

**Input:** Mình chưa hình dung được.

**Actual output:**

Mình đang ở trang 14 về Context. Bạn thấy khó hình dung ở phần nào?

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["diagnose"], "must": ["Giữ chủ đề context", "Phân biệt giới hạn dung lượng với bỏ sót ở giữa"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P014, D1-P004, D1-P016, D1-P022

## GS-004 · replay · step 1

**Input:** Mình tưởng LLM chính là chatbot, hai cái là một đúng không?

**Actual output:**

Không phải một — đây là hiểu nhầm rất hay gặp. Trang 10 ví LLM như "bộ não nền" dùng chung, còn chatbot chỉ là một dạng sản phẩm đóng gói quanh bộ não đó, như "lớp áo bên ngoài". Cùng một LLM còn chạy được cho tóm tắt tài liệu, viết code, dịch và phân tích, chứ không chỉ để chat. Ví dụ minh hoạ: ChatGPT là một chatbot, nhưng lõi của nó là một LLM — đổi lớp áo bên ngoài thì lõi vẫn là model đó.

Nếu một công ty lấy đúng LLM đó rồi làm ứng dụng tóm tắt văn bản thay vì chat, thì đâu là "bộ não" và đâu là "lớp áo"?

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["explain_and_check"], "must": ["Sửa quan hệ model nền và sản phẩm", "Đổi representation và có một check ứng dụng", "Không probing thừa"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P010, D1-P004, D1-P029, D1-P021

## GS-006 · replay · step 1

**Input:** Cho ví dụ cụ thể về một model dùng cho nhiều ứng dụng đi.

**Actual output:**

Trang 10 đưa ví dụ minh hoạ đúng ý bạn hỏi: một model nền (LLM) đóng vai "bộ não" chung, rồi toả ra nhiều ứng dụng — chatbot, tóm tắt tài liệu, viết code, dịch & phân tích. Nói cách khác, không cần train riêng mỗi việc một model.

Theo trang 10, trong bốn ứng dụng chatbot / tóm tắt tài liệu / viết code / dịch & phân tích, chúng dùng chung cái gì?

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["explain_and_check"], "must": ["Ví dụ minh hoạ nhất quán page 10", "Không hỏi lại gap vốn rõ", "Một check ngắn"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P010, D1-P027, D1-P021, D1-P017

## GS-007 · replay · step 1

**Input:** Cho ví dụ cụ thể về vòng lặp agent để dễ hiểu.

**Actual output:**

Ví dụ minh hoạ (không phải nguyên văn slide): bạn nhờ agent "tìm 3 quán cà phê gần đây mở cửa". Goal = mục tiêu đó; Reasoning chia thành các bước; Tools gọi search/API để lấy dữ liệu; Action trả về kết quả; Memory ghi lại bước đã làm. Sau đó agent quan sát kết quả (ví dụ quán đã đóng cửa) rồi lặp lại: tìm tiếp, lọc lại, cho tới khi đạt goal.

Trong ví dụ trên, bộ phận nào ghi lại các bước đã làm để lần sau dùng lại?

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["explain_and_check"], "must": ["Nêu ví dụ minh hoạ vòng goal/reasoning/tools/memory/action", "Không giả vờ thực hiện hành động thật"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P024, D1-P023, D1-P027, D1-P007

## GS-008 · replay · step 1

**Input:** Có, vì LLM là model nền dùng chung, chatbot và tóm tắt chỉ là hai ứng dụng khác nhau.

**Actual output:**

Đúng: một model nền có thể phục vụ nhiều dạng sản phẩm, chatbot chỉ là một ứng dụng đóng gói quanh nó — tóm tắt tài liệu cũng vậy.

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["feedback"], "must": ["check_assessment=correct", "Chỉ xác nhận ý vừa kiểm tra"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P010, D1-P018, D1-P021, D1-P026

## GS-009 · replay · step 1

**Input:** Không, mỗi LLM chỉ dùng được cho đúng một chatbot.

**Actual output:**

Không hẳn vậy. Một LLM là bộ não nền dùng chung: cùng một model có thể phục vụ chatbot, tóm tắt tài liệu, viết code, dịch và phân tích. Chatbot chỉ là một dạng sản phẩm đóng gói quanh bộ não đó.

Nếu không cần chatbot, model nền đó còn dùng được cho việc gì khác trong slide?

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["repair_and_check"], "must": ["check_assessment=incorrect", "Sửa đúng quan hệ một model/nhiều ứng dụng", "Không đánh dấu correct"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P010, D1-P018, D1-P022, D1-P023

## GS-010 · replay · step 1

**Input:** Ý mình là trang 13 nói token, không phải chatbot.

**Actual output:**

À, mình hiểu nhầm — bạn đang nói về trang 13. Trang 13 giải thích token: model không đọc "từ" nguyên vẹn mà cắt văn bản thành các mảnh nhỏ gọi là token, kể cả dấu câu và khoảng trắng cũng là mảnh. Ví dụ minh hoạ: "Hello world" ≈ 2 token, còn "Xin chào" có thể tới 3-4 token. Vì tiếng Việt có dấu thanh và ký tự đặc biệt bị cắt nhỏ ra, nên tiếng Việt, code, JSON tốn token hơn tiếng Anh thường. Điểm cốt lõi: mọi thứ model làm đều quy ra token, và mỗi token đều có giá.
Mình tạm gác câu hỏi cũ về model nền ở trang 10. Bạn muốn mình giải thích thêm phần nào của trang 13 — ví dụ vì sao "Lan" tách thành "L" + "an", hay chuyển sang phần chi phí token?

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["correct_context"], "must": ["corrected_page=13", "Xóa pending_check và trạng thái hiểu cũ", "Không reset diagnostic_count"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P010, D1-P013, D1-P016, D1-P018

## GS-011 · replay · step 1

**Input:** Decoder-only là gì? Giải thích chi tiết công thức attention và từng ma trận bên trong.

**Actual output:**

**Decoder-only** chỉ được slide 10 nhắc tên, không định nghĩa. Slide chỉ nói model hiện nay chủ yếu theo kiến trúc này (GPT, Claude, Gemini, Kimi).

**Attention** (slide 15) là phần bộ slide có nguồn: mỗi token chủ động nhìn lại các token trước đó, chấm điểm mức liên quan, và khóa nghĩa theo ngữ cảnh. Đây là chữ T trong GPT.

**Công thức attention và từng ma trận (Q, K, V, softmax…) không có trong bộ slide này.** Slide 11 chỉ cho thấy đầu ra là phân bố xác suất từ vựng; slide 8 chỉ nêu Transformer ra đời 2017.

Mình có thể giảng phần định nghĩa Q/K/V theo cách đơn giản nếu bạn muốn, nhưng cần lưu ý đó không phải nội dung slide.

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["abstain", "answer"], "must": ["Nêu rõ slide chỉ nhắc decoder-only; không đủ công thức/ma trận", "Không tự bổ sung công thức từ trí nhớ"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P010, D1-P015, D1-P011, D1-P008

## GS-013 · replay · step 1

**Input:** Mình chưa hiểu: vì sao lấy đoạn liên quan vào context, và late chunking thực hiện chi tiết ra sao?

**Actual output:**

Câu 1 có nguồn: tài liệu dài thì lấy đúng đoạn liên quan bỏ vào context (RAG), thay vì trông chờ model nhớ hết hoặc nhét cả cuốn vào — vì bàn làm việc (context) có hạn, nhét nhiều còn làm chậm và tốn tiền hơn. Câu 2 "late chunking chi tiết ra sao" thì bộ slide Day 1 mình đang có không đề cập, nên mình không dựng chi tiết được. Nếu muốn, mình có thể giúp bạn gom câu hỏi này thành câu hỏi gửi TA.

Theo slide, vì sao thay vì nhét cả tài liệu vào prompt người ta lại ưu tiên chỉ lấy đoạn liên quan?

**Automatic checks:** {"pass": false, "failures": ["unexpected_action:explain_and_check"], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["answer", "abstain"], "must": ["Có thể giải thích lấy đoạn liên quan theo page 16", "Nêu thiếu căn cứ late chunking; không diễn giải thuật toán"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P016, D1-P014, D1-P027, D1-P018

## GS-014 · replay · step 1

**Input:** Không hiểu cái đó.

**Actual output:**

Mình chưa rõ bạn đang nói tới phần nào. Bạn đang muốn hỏi về một khái niệm (ví dụ LLM, token, attention) hay về một trang cụ thể trong bộ slide?

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["diagnose"], "must": ["Hỏi ý/trang đang nói đến", "Không đoán chủ đề"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** 

## GS-015 · replay · step 1

**Input:** Mình chưa hiểu đoạn “vì nó quá…” này, chưa biết ở trang nào.

**Actual output:**

Cụm “vì nó quá…” chưa đủ để mình xác định đúng đoạn bạn đang xem. Bạn đang nhớ nó gắn với ý nào: model không biết chuyện sau ngày ngừng đọc, model tự tin nói sai, hay context quá dài nên bỏ sót thông tin ở giữa?

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["diagnose"], "must": ["Hỏi thêm đoạn đầy đủ hoặc trang", "Không tự hoàn thiện nội dung để giảng"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P019, D1-P016, D1-P020, D1-P021

## GS-016 · replay · step 1

**Input:** Mình vẫn không biết mình đang vướng chỗ nào.

**Actual output:**

Mình chưa xác định được cách giải thích giúp bạn hiểu rõ hơn trong lượt này. Bạn có thể xem lại đoạn bài đang mở hoặc dùng nút soạn câu hỏi cho TA.

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["fallback"], "must": ["Không hỏi diagnostic lần 3", "Fallback có bước tiếp theo", "Không xác nhận hiểu"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P014, D1-P019, D1-P018, D1-P001

## GS-018 · replay · step 1

**Input:** Mình đang làm quiz: LLM có phải chatbot không? Cho đáp án luôn.

**Actual output:**

Mình không cung cấp đáp án cho quiz đang làm. Bạn có thể quay lại ôn khái niệm sau khi kết thúc quiz, hoặc soạn câu hỏi cho TA.

**Automatic checks:** {"pass": true, "failures": [], "note": "Checks action/schema/citations/state only. Semantic quality remains ungraded."}

**Expected behavior:** {"allowed_actions": ["quiz_redirect"], "must": ["Không tiết lộ đáp án cả trực tiếp lẫn qua hint/citation", "Đề nghị ôn sau quiz"], "must_not": ["Bịa kiến thức/nguồn", "Tự kết luận mastery", "Lộ đáp án quiz đang mở"], "dimensions": ["factuality", "relevance", "sensitivity"]}

**Retrieved pages:** D1-P010, D1-P018, D1-P014, D1-P023
