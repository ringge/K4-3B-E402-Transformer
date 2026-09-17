# CP1 mining notes — Track A1 VLearn Tutor

## Kết luận

Pain point được chọn là: **khi học viên báo chưa hiểu hoặc yêu cầu giải thích lại, tutor hiếm khi chuyển sang một bước chẩn đoán rõ ràng trước khi tạo thêm nội dung**. Tutor thường giữ chiến lược `review_concept`; học viên phải tự chỉ ra misconception, kiến thức nền còn thiếu hoặc dạng giải thích họ cần.

Lát cắt tối ưu một quyết định trung tâm: **lỗ hổng học tập đã được xác định đủ rõ để giải thích tiếp chưa?** Nếu chưa, tutor hỏi đúng một câu chẩn đoán. Nếu đã rõ, tutor chỉ xử lý một lỗ hổng bằng cách giải thích khác với cách vừa thất bại và kiểm tra lại bằng một câu ngắn.

## Phương pháp mining

1. Population nguồn có 13.494 lượt. Dùng dữ liệu của mọi cohort và lọc `is_preset=False`, còn 10.427 lượt tự gõ. `cohort_hint` chỉ dùng để kiểm tra độ phủ, không phải điều kiện loại dữ liệu. Đơn vị đếm là một row/`turn_id`; số học viên duy nhất đếm theo `student`.
2. Tìm candidate bằng regex không phân biệt hoa thường: `(?:vẫn\s+)?(?:chưa|không)\s+(?:hiểu|nắm|rõ)|khó\s+hiểu|chưa\s+hình\s+dung`.
3. Quy tắc positive: câu hỏi thể hiện chính học viên chưa hiểu, chưa nắm, chưa rõ hoặc chưa hình dung nội dung đang học. Quy tắc negative: tín hiệu chỉ nằm trong đoạn slide được trích; học viên đang phê bình cách viết “không rõ ràng”; hoặc hỏi liệu nội dung có khó hiểu hay không thay vì báo mình chưa hiểu.
4. Đọc nguyên văn toàn bộ 153 `student_question` khớp regex; mở ngữ cảnh khi câu mơ hồ và với toàn bộ chuỗi được giữ. Loại 17 false positive, còn 136 lượt đã xác nhận. Các turn bị loại: `T01323`, `T02892`, `T03689`, `T03693`, `T03694`, `T03696`, `T03697`, `T03707`, `T03710`, `T03715`, `T03719`, `T03730`, `T04187`, `T10139`, `T11259`, `T12967`, `T13099`.
5. Theo data dictionary, ngày 30/07 là ngoại lệ: 2.579 lượt đến từ một hoạt động trên lớp. Ngày này đóng góp 52/136 (38,2%) lượt “chưa hiểu” đã xác nhận, nên nếu gộp thẳng vào mẫu chính thì một sự kiện đơn lẻ có thể chi phối kết quả. Vì vậy, tách 30/07 khỏi mẫu chính, còn 84 lượt; không xóa dữ liệu mà vẫn báo kết quả đủ 136 lượt như một kiểm tra độ bền.
6. So sánh `move_used`, `reply_len` và hành vi hỏi/kiểm tra hiểu với baseline câu tự gõ ở cùng phạm vi ngày.
7. Tìm candidate chuỗi bằng regex không phân biệt hoa thường: `vẫn\s+(?:chưa|không)|giải\s*thích\s*lại|chưa\s+rõ\s+lắm|dễ\s*hiểu\s+hơn|chưa\s+(?:biết\s+và\s+)?hình\s+dung`. Ghép với lượt trước của cùng `student`, cùng `course_id`, cách nhau không quá 30 phút; sau đó đọc tay để giữ chuỗi cùng chủ đề và loại chuỗi đổi chủ đề, vấn đề kỹ thuật hoặc chỉ chứa từ khóa ngẫu nhiên.
8. Mở toàn bộ turn trước–sau của các chuỗi được giữ để tránh suy luận từ một dòng cô lập.

## Các con số kiểm tra được

### Mẫu chính: mọi cohort, không gồm ngày 30/07

| Chỉ số | Tín hiệu “chưa hiểu” đã đọc tay | Toàn bộ câu tự gõ cùng phạm vi |
|---|---:|---:|
| Lượt | 84 | 8.267 |
| Học viên duy nhất | 58 | 1.212 |
| `review_concept` | 77/84 (91,7%) | 7.177/8.267 (86,8%) |
| `ask_probing_question` | 0/84 (0%) | 14/8.267 (0,17%) |
| `validate_understanding` | 0/84 (0%) | 20/8.267 (0,24%) |
| Reply trung vị | 1.320 ký tự | 1.046 ký tự |
| Reply ≥1.000 ký tự | 61/84 (72,6%) | 4.419/8.267 (53,5%) |
| Reply ≥1.500 ký tự | 28/84 (33,3%) | 1.825/8.267 (22,1%) |

Phát hiện quan trọng là **tutor không đổi khỏi chiến lược mặc định sau tín hiệu thất bại**, đồng thời câu trả lời dài hơn baseline: trung vị 1.320 so với 1.046 ký tự.

Mẫu chính gồm 51 lượt K3 và 33 lượt K4. Kiểm tra độ bền khi giữ cả ngày 30/07 cho kết quả cùng chiều: 136 lượt của 80 học viên (103 K3, 33 K4); 126/136 (92,6%) là `review_concept`, 2/136 là `ask_probing_question`, 0/136 là `validate_understanding`; reply trung vị 1.163 ký tự, so với 934 ký tự của toàn bộ 10.427 câu tự gõ.

Trong 20 chuỗi cùng chủ đề ngoài ngày 30/07 có yêu cầu giải thích lại/dễ hiểu hơn trong tối đa 30 phút, có 21 lượt yêu cầu tutor thích ứng:

- 16/21 lượt tiếp tục `review_concept`; 4/21 chuyển sang `give_example`; 1/21 là `give_direct_answer`.
- 0/21 dùng `ask_probing_question` hoặc `validate_understanding`.
- Reply trung vị 1.310 ký tự; 17/21 reply dài ít nhất 1.000 ký tự.

Danh sách 20 chuỗi được giữ để tái kiểm tra:

- K3: `T06222→T06233`, `T04863→T04864`, `T04885→T04886`, `T04435→T04439`, `T07500→T07501`, `T07023→T07024→T07026`, `T06960→T06965`, `T08379→T08382`, `T06488→T06489`, `T06890→T06893`.
- K4: `T11081→T11086→T11087`, `T10478→T10480`, `T10815→T10816`, `T11620→T11624`, `T10924→T10927→T10928`, `T10960→T10962`, `T13058→T13062`, `T12534→T12535→T12536→T12537`, `T12355→T12357`, `T12896→T12910`.

## Năm mẫu nguyên văn

Các câu dưới đây giữ nguyên toàn bộ `student_question`, gồm cả tiền tố ngữ cảnh. Phần “mở đầu reply” là trích nguyên văn; toàn bộ reply có thể tra lại bằng `turn_id` trong CSV.

### `T07024` — failure case, K3

> (Trang 1)  
> (Đang học phần “Prototype Interview” của buổi này)  
> tôi vẫn chưa hiểu

Mở đầu reply: “Để hiểu rõ hơn về vai trò của prototype, hãy hình dung bạn đang có một ý tưởng nhưng chưa biết nó thực sự hoạt động ra sao trong thực tế.” Tutor dùng `review_concept`, dài 1.263 ký tự, không probing/validate.

### `T07501` — failure case, K3

> (Trang 1)  
> (Đang học phần “1-day20-model-serving-inference-optimization” của buổi này)  
> vậy VLM được ứng dụng trong cái gì? tôi vẫn chưa rõ đối tượng hoặc use case chẳng hạn? bởi nó ko thể thay được CV, còn trong chatbot, thì nó chỉ đơn giản là trả lời 1 cách bình thường cho khách hàng, chứ không đám ứng được trong môi trường doanh nghiệp hay gì cả nhỉ? kể cả robot cũng ưu tiên CV hơn?

Mở đầu reply: “Bạn hoàn toàn đúng khi cho rằng VLM không thay thế được CV trong các tác vụ đòi hỏi sự chính xác về tọa độ hay hiệu năng real-time cực cao.” Tutor dùng `review_concept`, dài 3.112 ký tự, không probing/validate.

### `T06893` — counterexample, K3

> (Trang 1)  
> (Đang học phần “2-day18-production-rag” của buổi này)  
> chưa hiểu lắm, giải thích dễ hiểu hơn

Mở đầu reply: “Hãy tưởng tượng bạn có một cuốn sách.” Tutor đổi sang `give_example`, dài 997 ký tự. Đây là counterexample: tutor đã đổi representation nhưng vẫn chưa kiểm tra hiểu.

### `T10927` — failure case, K4

> (Đang học phần “day01-llm-foundation-1” của buổi này)  
> vẫn chưa hiểu MCP lắm

Mở đầu reply: “Chào [HV], để hiểu MCP (Model Context Protocol) một cách đơn giản nhất, em hãy hình dung như thế này:”. Tutor dùng `review_concept`, dài 1.353 ký tự, không probing/validate; lượt kế tiếp học viên phải yêu cầu ví dụ cụ thể.

### `T12535` — failure case, K4

> (Đang học phần “day02-object-detection-annotation” của buổi này)  
> là sao? tôi vẫn chưa hiểu, có thể giải thích đầu đuôi thế nào theo cách dễ hiểu được không? nguyên bản là gì? tực là cái này đang nói về cách 1 người dán nhãn xử lí công việc này theo 1 phương thức với 3 phần trên hay sao?

Mở đầu reply: “Chào [HV], để anh giải thích lại cho dễ hiểu nhé. Slide này [trang 8] mô tả **vị trí và vai trò của Object Detection trong một hệ thống xe tự lái hoàn chỉnh**, cụ thể là cách luồng dữ liệu di chuyển từ đầu đến cuối.” Tutor dùng `review_concept`, dài 1.799 ký tự; ở lượt sau học viên phải sửa lại ngữ cảnh slide.

## Chuỗi hội thoại minh họa

| Chuỗi turn | Quan sát |
|---|---|
| `T07023 → T07024 → T07026` | Học viên K3 hai lần liên tiếp nói “vẫn chưa hiểu” về prototype. Tutor trả hai lượt `review_concept` dài 1.263 và 1.027 ký tự mà không hỏi điểm phân biệt nào đang bị hiểu sai. |
| `T07500 → T07501` | Sau khi so sánh VLM với Computer Vision, học viên K3 vẫn chưa rõ đối tượng và use case của VLM. Tutor trả một lượt `review_concept` 3.112 ký tự thay vì chẩn đoán chính xác giả định nào về giá trị của VLM đang gây kẹt. |
| `T06890 → T06893` | Học viên K3 yêu cầu giải thích “late chunking” dễ hiểu hơn. Tutor đổi sang ví dụ (`give_example`, 997 ký tự), là counterexample cho thấy đổi representation có thể xảy ra dù chưa có bước chẩn đoán hoặc kiểm tra hiểu. |
| `T10901 → T10924 → T10927 → T10928` | Sau hai lượt giải thích MCP, học viên nói “vẫn chưa hiểu MCP lắm”. Tutor trả thêm 1.353 ký tự dưới dạng `review_concept`; học viên phải tự yêu cầu “cho ví dụ cụ thể”. |
| `T11616 → T11620 → T11624` | Học viên hỏi liên tiếp về guideline, ground truth và QC/rework rồi nói “vẫn chưa hình dung”. Tutor trả thêm 1.497 ký tự, không hỏi quan hệ nào trong quy trình đang bị hiểu sai. |
| `T12534 → T12535 → T12536 → T12537` | Học viên nói “vẫn chưa hiểu”; tutor giải thích 1.799 ký tự nhưng chọn nhầm slide. Học viên phải sửa “ý tôi là slide này nè” rồi tiếp tục hỏi. Đây là failure do chưa xác nhận ngữ cảnh trước khi giải thích. |
| `T11081 → T11086 → T11087` | Sau phần tóm tắt Task 3.2, học viên yêu cầu giải thích lại. Tutor trả 1.049 ký tự; lượt kế tiếp học viên tiếp tục yêu cầu giải thích lab. |
| `T13058 → T13062` | Học viên yêu cầu giải thích Context Engineering dễ hiểu hơn. Tutor vẫn mang nhãn `review_concept` nhưng đã đổi sang phép so sánh “bàn làm việc”; đây là ví dụ move label không phản ánh đầy đủ chất lượng thích ứng. |
| `T10815 → T10816` | Học viên tự mô tả giả thuyết sai và yêu cầu “chỉ phần lỗ hổng kiến thức”. Tutor xác định được khoảng trống giữa backpropagation và ground truth. Đây là counterexample cho thấy tutor có thể chẩn đoán khi học viên cung cấp cấu trúc rất rõ. |
| `T13295 → T13296 → T13299` | Từ câu mơ hồ “tôi ko hiểu”, tutor đoán chủ đề rồi giải thích 862 ký tự. Sau hai lượt, học viên tự tạo cách hiểu “cải lùi”; tutor mới xác nhận cách hiểu đó. |

## Điều dữ liệu chứng minh và chưa chứng minh

Dữ liệu chứng minh được:

- Tín hiệu “chưa hiểu” có thật trong câu học viên tự gõ.
- Tutor thường giữ `review_concept`, hiếm dùng move chẩn đoán hoặc kiểm tra hiểu.
- Các reply sau tín hiệu này thường dài hơn baseline.
- Có nhiều chuỗi thật trong đó học viên phải tiếp tục yêu cầu ví dụ, sửa ngữ cảnh hoặc diễn đạt lại điểm kẹt.

Dữ liệu chưa chứng minh được:

- Mọi reply dài đều tệ; `T13062` cho thấy một reply mang nhãn `review_concept` vẫn có thể đổi cách giải thích hiệu quả.
- Tutor không bao giờ chẩn đoán; `T10816` là counterexample rõ.
- Học viên “tiếp tục học khi chưa nắm bài”; CSV không nối hội thoại với kết quả quiz hoặc learning outcome.
- 136 lượt là toàn bộ nhu cầu chẩn đoán; bộ từ khóa bỏ sót các cách diễn đạt không chứa tín hiệu đã định nghĩa.
- Việc hỏi probing luôn tốt hơn trả lời ngay; khi học viên đã nêu misconception cụ thể, tutor có thể sửa trực tiếp mà không cần hỏi thêm.

## So sánh ba pain-point ứng viên

| Ứng viên | Reach / tần suất từ data | Giá trị nếu giải quyết | Độ mạnh bằng chứng | Build trong hackathon | Quyết định |
|---|---|---|---|---|---|
| Chẩn đoán trước khi giải thích lại | Ngoài 30/07: 84 lượt/58 học viên theo bộ tín hiệu chặt; 20 chuỗi hỏi lại cùng chủ đề | Tạo khác biệt sư phạm; giảm giải thích không trúng điểm kẹt | Trung bình: có chuỗi thật và counterexample; chưa có learning outcome | Cao: failure-signal detector + diagnosis gate + short check | **Chọn vì ưu tiên cải tiến sư phạm khác biệt** |
| Câu tự gõ không có căn cứ | Ngoài 30/07: 2.208 lượt; 675 học viên | Tăng khả năng kiểm chứng và giảm rủi ro học sai | Mạnh: field trực tiếp + nhiều turn ID | Cao: retrieval gate + citation/abstain | Không chọn làm pain chính; giữ citation làm guardrail |
| Một kiểu sư phạm cho hầu hết câu hỏi | Ngoài 30/07, `review_concept` chiếm 7.177/8.267 lượt tự gõ (86,8%) | Có thể cải thiện độ phù hợp của mọi reply | Yếu hơn: move label không phản ánh đầy đủ cách giải thích | Trung bình, dễ phình scope | Backlog |

Hướng được chọn có reach đo được thấp hơn pain citation nhưng tạo một quyết định AI đặc thù giáo dục hơn và có thể đánh giá rõ trên các chuỗi thất bại thật.

## JTBD và current workaround

- Job statement: **Xác định đúng điểm mình đang hiểu sai hoặc còn thiếu để tiếp tục học phần hiện tại.**
- Current workaround quan sát được: học viên yêu cầu “giải thích lại”, “dễ hiểu hơn”, tự đề nghị ví dụ, tự mô tả giả thuyết hoặc sửa ngữ cảnh cho tutor qua nhiều lượt.
- Job story: **Khi một lời giải thích vẫn chưa giúp tôi hiểu, tôi muốn tutor xác định đúng điểm kẹt và thử một cách giải thích khác, để tôi có thể diễn đạt lại ý cốt lõi trước khi học tiếp.**

## Lát cắt và ranh giới

- Trigger: một học viên tự gõ tín hiệu rõ như “chưa hiểu”, “vẫn chưa hiểu”, “giải thích lại”, sau một lượt giải thích.
- Một quyết định AI: lỗ hổng học tập đã đủ rõ để giải thích tiếp chưa?
- Chưa đủ rõ: hỏi đúng một câu phân biệt giữa 2–3 khả năng, ví dụ “Bạn đang vướng khái niệm X, quan hệ X–Y hay cách áp dụng vào code?”.
- Đủ rõ: nêu lỗ hổng dưới dạng giả thuyết, đổi representation so với lượt trước (ví dụ, sơ đồ bước, ví dụ phản chứng hoặc analogy), rồi hỏi một câu kiểm tra ngắn.
- Kết thúc lát cắt: học viên diễn đạt lại đúng ý cốt lõi hoặc tutor thừa nhận vẫn chưa đủ tín hiệu và chuyển sang tài liệu/TA phù hợp.
- Ngoài scope CP1: hồ sơ mastery dài hạn, chấm trình độ toàn khóa, tự thay đổi lộ trình học, hoặc dự đoán điểm số.

## Requirement layers và khoảng trống

| Layer | Trạng thái CP1 | Nội dung đã biết / còn thiếu |
|---|---|---|
| Business requirement | Một phần | Có baseline hành vi; chưa có KPI về số lượt hỏi lại hoặc learning outcome. |
| Stakeholder requirement | Một phần | Segment chính là học viên VLearn vừa báo chưa hiểu, không giới hạn cohort; chưa phỏng vấn để xác nhận mức khó chịu/hậu quả. |
| Functional requirement | Đủ cho lát cắt | Nhận diện failure signal, đánh giá độ rõ của gap, hỏi một câu chẩn đoán hoặc giải thích thích ứng, rồi kiểm tra ngắn. |
| Non-functional requirement | Thiếu | Chưa chốt độ dài tối đa, citation correctness, latency và tỷ lệ probing thừa chấp nhận được. |
| Transition requirement | Thiếu | Chưa chốt golden set, baseline prompt và cách so trước/sau. |

## Assumptions và câu hỏi mở

Assumptions:

- Một câu probing ngắn ít gây khó chịu hơn một reply dài nhưng không trúng điểm kẹt.
- Học viên sẵn sàng trả lời một câu kiểm tra hiểu thay vì chỉ nhận thêm nội dung.
- Các chuỗi trong cùng student/course và gần nhau về thời gian phản ánh cùng một phiên học; CSV không có `conversation_id` để xác nhận tuyệt đối.
- Học viên diễn đạt lại đúng ý cốt lõi là proxy phù hợp cho hiểu bài trong lát cắt, không phải bằng chứng mastery dài hạn.

Open questions cần trả lời trước khi chốt spec:

1. Ba willing users gần nhất đã làm gì khi lời giải thích đầu tiên chưa giúp họ hiểu, và họ khó chịu nhất ở độ dài, cách diễn đạt hay việc tutor không biết họ đang vướng đâu?
2. Bao nhiêu câu probing là chấp nhận được trước khi học viên cảm thấy tutor “hỏi ngược quá nhiều”? Đề xuất ban đầu: tối đa một câu cho lát cắt này.
3. Quality bar nên đo `gap identified`, `explanation changed`, `citation valid` và `check question passed` như thế nào?
4. Khi học viên không trả lời được câu kiểm tra lần hai, tutor nên thử thêm một representation hay chuyển TA/tài liệu nào?
5. Điền tên đội, phân công và ba willing users vào `canvas.md` trước khi nộp CP1.
