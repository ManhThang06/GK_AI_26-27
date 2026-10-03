# Hướng Dẫn Tích Hợp Dự Án Sokoban Hoàn Chỉnh

Tài liệu này cung cấp cái nhìn tổng quan về kiến trúc dự án và chức năng của từng thư mục để Claude (hoặc các AI/Lập trình viên khác) hiểu cách kết nối các module lại thành một trò chơi Sokoban hoàn chỉnh.

## 1. Thư mục `M2` (Core Algorithms & Heuristics)
Thư mục này chịu trách nhiệm cho trí tuệ nhân tạo (AI) cơ bản của trò chơi (Chế độ 1 người chơi).
- Chứa các thuật toán tìm kiếm đường đi cốt lõi như **UCS (Uniform Cost Search)** và **A* (A-Star)**.
- Chứa logic của hàm **Heuristic** được sử dụng để tối ưu hóa tìm kiếm (có thể là tính toán khoảng cách Manhattan, Deadlock detection, hoặc các bài toán khoảng cách BFS tới mục tiêu).

## 2. Thư mục `M3` (User Interface & Experiments)
Thư mục này chịu trách nhiệm cho Giao diện người dùng (UI) và Môi trường thử nghiệm.
- **Thư mục con `gui/`**: Chứa toàn bộ code giao diện (thường được viết bằng Pygame). Cụ thể bao gồm:
  - Giao diện **Màn hình chính** (Main Menu).
  - Giao diện **Màn hình chọn chế độ chơi** (Mode Selection).
- **Code thực nghiệm (Experimental Code)**: Dùng để chạy thử và đánh giá hiệu năng. Nó đo lường và so sánh **độ phức tạp thời gian** (Time Complexity) và **độ phức tạp không gian** (Space Complexity / Memory Usage) của hai thuật toán UCS và A* đã được định nghĩa bên trong thư mục `M2`.

## 3. Thư mục `M4` (Two-Agent Competitive Mode)
Thư mục này chịu trách nhiệm cho logic và thuật toán của **Chế độ chơi 2 Người/Agent (Đối kháng/Cạnh tranh)**.
- Chứa các thuật toán điều khiển (Agent Algorithms) được thiết kế đặc thù cho môi trường đa tác tử (multi-agent). Chẳng hạn như thuật toán GBFS (Greedy Best-First Search) kết hợp BFS tránh vật cản.
- Xử lý các quy tắc va chạm, tranh giành hộp, đẩy hộp và hệ thống tính điểm thi đấu giữa 2 agent trên cùng một bản đồ.

---

## 4. Yêu Cầu Cụ Thể Để Tích Hợp Thành Trò Chơi Hoàn Chỉnh 

Để kết nối tất cả các thành phần trên thành một trò chơi thống nhất, người lập trình/AI cần thực hiện theo các chỉ dẫn sau:

### 4.1. Thiết lập Cấu trúc Thư mục Mới
- Tạo một thư mục chính là **`Sokoban`** nằm tại thư mục gốc của dự án.
- Bên trong thư mục `Sokoban`, tạo hai thư mục con để lưu trữ map:
  - **`map1Agent`**: Dành cho chế độ 1 người chơi (bỏ các file `map.txt` vào đây).
  - **`map2Agent`**: Dành cho chế độ 2 người chơi đối kháng (bỏ các file `map.txt` vào đây).

### 4.2. Luồng Chạy Của Game (Game Flow)
- **Điểm bắt đầu (Start):** Trò chơi sẽ bắt đầu từ **Màn hình chọn chế độ chơi** (sử dụng UI từ thư mục `M3`).
- **Tái sử dụng UI:** Tạm thời sẽ **giữ nguyên** các thiết kế và mã nguồn UI hiện có.

### 4.3. Tích hợp Các Chế Độ Chơi

**A. Chế độ 1 Agent (Single Player)**
- **Giao diện:** Giữ nguyên code UI của màn hình chơi 1 Agent từ thư mục `M3`.
- **Bản đồ (Maps):** Lấy dữ liệu map từ thư mục `Sokoban/map1Agent`.
- **Thuật toán cốt lõi:** Lấy các thuật toán **UCS**, **A*** và **Heuristic** từ thư mục **`M2`**.

**B. Chế độ 2 Agent (Competitive)**
- **Thiết lập Game:** Khi người dùng chọn chế độ 2 Agent, hệ thống phải yêu cầu người chơi **nhập vào số bước (steps)** với điều kiện `steps >= 1`. Số bước này sẽ được áp dụng trực tiếp làm tham số cấu hình cho màn chơi đa tác tử.
- **Bản đồ (Maps):** Lấy dữ liệu map từ thư mục `Sokoban/map2Agent`.
- **Thuật toán cốt lõi:** Kế thừa toàn bộ mã nguồn thuật toán điều khiển của 2 Agent từ thư mục **`M4`**.
