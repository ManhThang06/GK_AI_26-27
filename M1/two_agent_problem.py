from two_agent_state import TwoAgentState

class TwoAgentProblem:
    def __init__(self, map_data, initial_a, initial_b, n_steps):
        self.walls = map_data.walls
        self.goals = map_data.goals
        self.initial_state = TwoAgentState(
            agent_a_pos=initial_a,
            agent_b_pos=initial_b,
            boxes=map_data.initial_boxes,
            score_a=0,
            score_b=0,
            steps_left=n_steps,
            box_owner=None
        )

    def is_terminal(self, state):
        return state.steps_left <= 0

    def utility(self, state):
        return (state.score_a, state.score_b)

    def get_next_pos(self, current_pos, action):
        # Viết if-elif tường minh thay vì dùng dictionary .get()
        row, col = current_pos
        if action == 'North': return (row, col - 1)
        elif action == 'South': return (row, col + 1)
        elif action == 'East': return (row + 1, col)
        elif action == 'West': return (row - 1, col)
        return (row, col) # action = 'Wait' thì trả về chỗ cũ

    def transition_model(self, state, action_a, action_b):
        if self.is_terminal(state):
            return state

        # 1. TÍNH NHÁP TỌA ĐỘ TIẾP THEO
        next_a = self.get_next_pos(state.agent_a_pos, action_a)
        next_b = self.get_next_pos(state.agent_b_pos, action_b)

        # 2. KIỂM TRA VA CHẠM GIỮA 2 AGENT
        # Lỗi 1: Đi xuyên qua nhau (đổi chỗ)
        if next_a == state.agent_b_pos and next_b == state.agent_a_pos:
            next_a = state.agent_a_pos
            next_b = state.agent_b_pos
        
        # Lỗi 2: Cùng nhảy vào một ô trống
        elif next_a == next_b and action_a != 'Wait' and action_b != 'Wait':
            next_a = state.agent_a_pos
            next_b = state.agent_b_pos

        # Chuẩn bị biến để tính toán dời hộp
        new_boxes = set(state.boxes)
        new_box_owner = dict(state.box_owner)
        score_a = state.score_a
        score_b = state.score_b

        # 3. XỬ LÝ AGENT A
        if next_a in self.walls:
            next_a = state.agent_a_pos # Đụng tường thì đứng im
        elif next_a in new_boxes:
            # Vị trí mới của hộp = Vị trí dự kiến của A + Vector hướng đi
            box_next_r = next_a[0] + (next_a[0] - state.agent_a_pos[0])
            box_next_c = next_a[1] + (next_a[1] - state.agent_a_pos[1])
            box_next = (box_next_r, box_next_c)

            # Hộp đụng tường, đụng hộp khác, hoặc đụng thằng B đang đứng/định đi tới
            if box_next in self.walls or box_next in new_boxes or box_next == next_b:
                next_a = state.agent_a_pos
            else:
                new_boxes.remove(next_a)
                new_boxes.add(box_next)
                new_box_owner.pop(next_a, None) # Xóa thông tin hộp ở vị trí cũ
                new_box_owner[box_next] = 'A'
                if box_next in self.goals:
                    score_a += 1

        # 4. XỬ LÝ AGENT B (Code lặp lại logic của A)
        if next_b in self.walls:
            next_b = state.agent_b_pos
        elif next_b in new_boxes:
            box_next_r = next_b[0] + (next_b[0] - state.agent_b_pos[0])
            box_next_c = next_b[1] + (next_b[1] - state.agent_b_pos[1])
            box_next = (box_next_r, box_next_c)

            # Chú ý: So sánh với next_a xem có đụng thằng A không
            if box_next in self.walls or box_next in new_boxes or box_next == next_a:
                next_b = state.agent_b_pos
            else:
                new_boxes.remove(next_b)
                new_boxes.add(box_next)
                new_box_owner.pop(next_b, None) # Xóa thông tin hộp ở vị trí cũ
                new_box_owner[box_next] = 'B'
                if box_next in self.goals:
                    score_b += 1
        return TwoAgentState(
            agent_a_pos=next_a,
            agent_b_pos=next_b,
            boxes=new_boxes,
            score_a=score_a,
            score_b=score_b,
            steps_left=state.steps_left - 1,
            box_owner=new_box_owner
        )
    