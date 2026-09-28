class State:
    def __init__(self, agent_pos, boxes):
        self.agent_pos = agent_pos
        # Ép kiểu thành frozenset để loại bỏ các trạng thái trùng lặp hình học[cite: 10, 11]
        self.boxes = frozenset(boxes) 
    # __eq__ và __hash__ bắt buộc phải có để các thuật toán UCS/A*
    # có thể lưu State vào biến 'explored set' nhằm kiểm tra trạng thái đã đi qua.
    def __eq__(self, other):
        return self.agent_pos == other.agent_pos and self.boxes == other.boxes
    def __hash__(self):
        return hash((self.agent_pos, self.boxes))