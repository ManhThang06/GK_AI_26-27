# Phân Tích Logic & Thuật Toán Trong M4 (Cập Nhật Mới Nhất)

Thư mục `M4` định nghĩa logic hoạt động của các Agent (`agent_algo_1.py` và `agent_algo_2.py`) trong chế độ cạnh tranh. Thuật toán đã được cải tiến để Agent ra quyết định thông minh hơn, đặc biệt trong việc tính toán khoảng cách và ưu tiên đẩy thùng.

Dưới đây là các nguyên tắc (rules) cốt lõi đang được thực thi trong code:

## 1. Thuật Toán Ra Quyết Định (Best-First Search + BFS)
- **Tìm kiếm cục bộ có giới hạn thời gian:** Agent sử dụng hàng đợi ưu tiên (Priority Queue) để khám phá không gian trạng thái. Quá trình tìm kiếm bị giới hạn bởi `time_limit`. Nếu hết thời gian, nó trả về hành động tốt nhất tính đến lúc đó.
- **Tiêu chí đánh giá trạng thái (Priority):**
  1. `h` (Heuristic): Khoảng cách tổng thể từ các hộp đến đích.
  2. `push_distance`: Đây là một Tuple `(goal_distance, distance)`. 
     - Trạng thái ưu tiên hơn khi khoảng cách từ hộp tới đích (`goal_distance`) nhỏ hơn.
     - Nếu bằng nhau, nó tiếp tục ưu tiên khoảng cách từ Agent tới vị trí cần đứng để đẩy hộp (`distance`) nhỏ hơn.

## 2. Tính Toán Khoảng Cách Bằng BFS
- Khác với trước đây dùng khoảng cách Manhattan đơn giản, Agent giờ đây dùng **thuật toán BFS** (`bfs_distance`) để dò đường thực tế từ vị trí của Agent đến ô cần đứng để đẩy hộp. 
- BFS này đảm bảo Agent đi vòng qua các chướng ngại vật bao gồm: tường (`walls`), các hộp hiện tại (`boxes`), và vị trí của Agent đối thủ (`opponent`).

## 3. Chiến Lược Lựa Chọn Hộp Mục Tiêu (Target Selection)
- **Bỏ qua hộp đã vào đích:** Agent sẽ kiểm tra và loại bỏ các hộp đã nằm gọn trong đích (`occupied_goals`). Nó chỉ tập trung vào các đích còn trống (`free_goals`) và các hộp chưa vào đích.
- **Tính toán khoảng cách Hộp - Đích:** Khoảng cách từ một ô liền kề hộp (`box_next`) đến Đích được trích xuất từ mảng khoảng cách chuẩn bị sẵn (`self.heuristic.maze_dist`). Điều này giúp Agent biết hướng đẩy nào đưa hộp đến đích nhanh nhất.

## 4. Các Quy Tắc Di Chuyển & Tránh Va Chạm
- Có 5 hành động: `North`, `South`, `West`, `East`, `Wait`.
- **Không đâm vào tường hoặc đối thủ:** Các bước di chuyển trực tiếp vào tường hoặc vào vị trí đối thủ đang đứng bị cấm.
- **Luật đẩy hộp:** Hộp chỉ bị đẩy nếu ô phía sau nó là một ô trống hoàn toàn (không tường, không hộp khác, không có đối thủ).

## 5. Nhận Diện Góc Chết (Deadlock Avoidance)
- Khi dự định đẩy hộp vào một ô (không phải ô đích), Agent sẽ kiểm tra xem ô đó có phải là "góc chết" không. 
- Một ô là góc chết nếu nó bị chặn bởi hai bức tường ở các hướng kề nhau (Trên-Trái, Trên-Phải, Dưới-Trái, Dưới-Phải). Nếu đúng, hành động đẩy này sẽ bị loại khỏi cây tìm kiếm để tránh tình trạng hộp kẹt vĩnh viễn không cứu được.
