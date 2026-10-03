## 1. Luật Chơi Chung (Sokoban Cơ Bản)
- **Mục tiêu:** Đẩy tất cả các hộp vào đúng vị trí đích (Goals).
- **Hành động (Actions):** Agent có thể đi theo 4 hướng: Lên (North), Xuống (South), Phải (East), Trái (West). Riêng trong chế độ 2 người có thêm hành động Đứng yên (Wait).
- **Di chuyển:** Agent không thể đi xuyên qua tường (Walls).
- **Đẩy hộp:** 
  - Agent chỉ có thể đẩy hộp tiến về phía trước mặt.
  - Hộp chỉ có thể bị đẩy nếu ô tiếp theo của hộp là ô trống (không phải là tường và không chứa hộp khác).
- **Chi phí (Path-cost):** Mỗi bước đi hoặc đẩy hộp tính là 1 bước.

## 2. Luật Chơi Đặc Thù (Two Agent Competitive - `two_agent_problem.py`)
Trong chế độ 2 agent (A và B) cùng tham gia đẩy hộp trên một bản đồ, áp dụng thêm các luật sau:

- **Va chạm giữa 2 Agent:**
  - Hai agent không thể đi xuyên qua nhau (đổi vị trí cho nhau). Nếu cố tình đổi chỗ, cả hai sẽ đứng yên ở vị trí cũ.
  - Hai agent không thể cùng lúc nhảy vào một ô trống. Nếu cả hai có cùng vị trí tiếp theo, cả hai sẽ đứng im.

- **Luật chiếm hữu và Đẩy hộp (Box Ownership):**
  - Nếu Agent A hoặc Agent B đẩy thành công một hộp sang ô mới, Agent đó sẽ trở thành "chủ sở hữu" (owner) của hộp đó.
  - Một hộp không thể bị đẩy nếu phía sau nó là tường, một hộp khác, hoặc là Agent còn lại đang đứng/sắp di chuyển tới đó.

- **Điểm số (Utility / Score):**
  - Điểm số được tính dựa trên số lượng hộp đã được đưa vào đích.
  - Điểm sẽ cộng cho Agent nào là "chủ sở hữu" (người đẩy cuối cùng) của chiếc hộp khi nó nằm trong đích.

- **Điều kiện kết thúc game (Terminal State):**
  - Trò chơi kết thúc khi **TẤT CẢ** các hộp đã nằm trong vị trí đích.
  - HOẶC khi hết số lượt đi cho phép (`steps_left <= 0`).
