class TwoAgentState:
    def __init__(self, agent_a_pos, agent_b_pos, boxes, score_a, score_b, steps_left, box_owner=None):
        self.agent_a_pos = agent_a_pos
        self.agent_b_pos = agent_b_pos
        self.boxes = frozenset(boxes) # Giữ nguyên kiểu frozenset để so sánh trạng thái
        self.score_a = score_a        # Số hộp Agent A đã hoàn thành
        self.score_b = score_b        # Số hộp Agent B đã hoàn thành
        self.steps_left = steps_left  # Số bước còn lại (n)
        if box_owner is None:
            box_owner_dict = {pos: None for pos in boxes}
            self.box_owner = frozenset(box_owner_dict.items())
        elif isinstance(box_owner, dict):
            self.box_owner = frozenset(box_owner.items())
        else:
            self.box_owner = frozenset(box_owner)
    def __eq__(self, other):
        # Bắt buộc cập nhật để so sánh toàn bộ các yếu tố mới
        return (self.agent_a_pos == other.agent_a_pos and
                self.agent_b_pos == other.agent_b_pos and
                self.boxes == other.boxes and
                self.score_a == other.score_a and
                self.score_b == other.score_b and
                self.steps_left == other.steps_left)
    def __hash__(self):
        return hash((self.agent_a_pos, self.agent_b_pos, self.boxes, 
                     self.score_a, self.score_b, self.steps_left, self.box_owner))