# Review skill

## Tính tổng quát

Không mô tả cụ thể tool_calling name, agent name, path tuyệt đối. Thay vào đó dùng các từ mô tả tổng quát để agent hiểu nên sử dụng thành phần có chức năng tương tự có trong harness của nó.

Ví dụ: 

- "sử dụng `read_file` để đọc tài liệu" -&gt; **NG** vs. "sử dụng tool có khả năng đọc nội dung tài liệu" -&gt; **OK**
- "C:\Users\ADMINagent\skills\abc" -&gt; **NG** vs. "~/.agent/skills/abc" -&gt; **OK**

## Tính nhất quán

Từ ngữ được dùng trong skill không nên mâu thuẫn với nhau. Ví dụ: step 1 yêu cầu chỉ được đọc file trong phạm vi A nhưng qua step 3 lại yêu cầu truy cập phạm vi B.

Văn phạm nên nhất quán, rõ ràng - tránh dùng 1 thuật ngữ để mô tả 1 thuật ngữ.

## Mô tả SKILL (metadata)

Metadata này cần ngắn gọn để tối ưu lượng token đăng ký trong mỗi session làm việc của agent. Tuân theo 2-3 tiêu chí sau:

- 1 câu bắt đầu bằng động từ mô tả SKILL dùng để làm gì.
- 1 câu trả lời câu hỏi "When" - khi nào nên dùng skill này.
- Optional: 1 câu bắt đầu với "Do not" - nó với agent không nên sử dụng skill trong những trường hợp nào. Ví dụ: về mặt ngữ nghĩa nó gần giống với metadata nhưng workflow của skill không phù hợp với trường hợp đó.

## Nội dung SKILL

- Nội dung được viết bằng tiếng Anh (English), chỉ dùng ngôn ngữ khác khi được user chỉ định trực tiếp.

## References folder

Chỉ chứa các file như format, template, documents,... những nội dung để agent đọc/tái sử dụng lại hoặc để agent tham khảo, cố định nội dung cho output.

## Scripts folder

Ghi cụ thể cá reusable script vào thư mục `script/` của skill và đề cập khi nào nên sử dụng vào `SKILL.md`

- script có thể là python, sh, ps, javascript - miễn là môi trường cài đặt skill phù hợp.
- Các cấu hình có thể thay đổi đều nên đặt là input params, tránh hardcode giá trị.
- Comment docstring, cách sử dụng đầy đủ vào script.

