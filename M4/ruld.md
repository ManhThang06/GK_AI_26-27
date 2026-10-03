# Phân Tích Logic & Thuật Toán Trong M4 (Agent Algorithms)

Thư mục `M4` chứa các thuật toán ra quyết định cho các Agent (`agent_algo_1.py` đại diện cho Agent A và `agent_algo_2.py` đại diện cho Agent B) trong chế độ đối kháng. Cả hai thuật toán có cấu trúc giống nhau, tập trung vào việc tìm kiếm đường đi tối ưu theo thời gian thực để đẩy hộp về đích.

Dưới đây là các nguyên tắc (rules) cốt lõi được lập trình cho Agent:

## 1. Thuật Toán Tìm Kiếm & Lựa Chọn Hướng Đi (Best-First Search)
- **Hàng đợi ưu tiên (Priority Queue):** Agent sử dụng thuật toán tìm kiếm cục bộ (giống Best-First Search) kết hợp với hàng đợi ưu tiên để tìm kiếm bước đi tiếp theo. 
- **Tiêu chí ưu tiên:** Hai yếu tố để đánh giá một hướng đi là:
  1. `h` (Heuristic): Ưu tiên những trạng thái (state) có giá trị Heuristic thấp nhất (gần đích nhất).
  2. `push_distance`: Khoảng cách Manhattan từ vị trí hiện tại của Agent đến vị trí có thể đẩy được hộp. Nếu hai trạng thái có Heuristic bằng nhau, ưu tiên hướng đi có `push_distance` nhỏ hơn.
- **Giới hạn thời gian (Time Limit):** Việc tìm kiếm bị giới hạn thời gian (deadline). Nếu quá thời gian phân bổ (`time_limit`), Agent sẽ lập tức kết thúc tìm kiếm và trả về hành động tốt nhất mà nó tìm được đến thời điểm đó. Nếu không có kết quả, trả về `Wait`.

## 2. Các Tập Lệnh Hành Động
Tại mỗi bước, Agent xem xét 5 hành động:
- Di chuyển: `North` (Lên), `South` (Xuống), `West` (Trái), `East` (Phải).
- Chờ: `Wait` (Đứng im).

## 3. Quy Tắc Tránh Va Chạm
- **Va chạm tường:** Agent không bao giờ đi vào ô tường (`problem.walls`).
- **Va chạm đối thủ:** Khi dự đoán bước đi, nếu ô tiếp theo có sự xuất hiện của đối thủ (`opponent`), Agent sẽ bỏ qua ô đó. Đồng thời, không đẩy hộp về phía đối thủ đang đứng.
- **Va chạm hộp:** Không thể đẩy một hộp nếu ngay phía sau hộp đó là tường, một hộp khác, hoặc đối thủ.

## 4. Xử Lý Bế Tắc (Deadlock Avoidance)
Đây là một logic cực kỳ quan trọng giúp Agent thông minh hơn:
- Khi Agent dự tính đẩy một hộp vào một ô trống, nó sẽ kiểm tra xem ô trống đó có phải là **Đích (Goal)** không.
- Nếu **KHÔNG** phải là đích, nó tiếp tục kiểm tra xung quanh ô đó.
- Nếu ô đó là một **góc chết** (ví dụ: bị chặn bởi tường ở cả hai phía: Trên-Trái, Trên-Phải, Dưới-Trái, hoặc Dưới-Phải), hành động đẩy này sẽ bị loại bỏ ngay lập tức. Điều này giúp ngăn Agent đẩy hộp vào góc tường, nơi không bao giờ lấy ra được nữa.
