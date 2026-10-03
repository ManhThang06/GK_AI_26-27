"""
core/two_agent.py
Trạng thái và luật chơi cho chế độ 2 Agent cạnh tranh.
  - TwoAgentState  : (agent_a_pos, agent_b_pos, boxes, score_a, score_b, steps_left, box_owner)
  - TwoAgentProblem: transition_model xử lý đầy đủ 7 trường hợp va chạm
"""


class TwoAgentState:
    __slots__ = ("agent_a_pos", "agent_b_pos", "boxes",
                 "score_a", "score_b", "steps_left", "box_owner")

    def __init__(self, agent_a_pos, agent_b_pos, boxes,
                 score_a, score_b, steps_left, box_owner=None):
        self.agent_a_pos = agent_a_pos
        self.agent_b_pos = agent_b_pos
        self.boxes = frozenset(boxes)
        self.score_a = score_a
        self.score_b = score_b
        self.steps_left = steps_left

        if box_owner is None:
            self.box_owner = frozenset({pos: None for pos in boxes}.items())
        elif isinstance(box_owner, dict):
            self.box_owner = frozenset(box_owner.items())
        else:
            self.box_owner = frozenset(box_owner)

    def __eq__(self, other):
        return (self.agent_a_pos == other.agent_a_pos and
                self.agent_b_pos == other.agent_b_pos and
                self.boxes == other.boxes and
                self.score_a == other.score_a and
                self.score_b == other.score_b and
                self.steps_left == other.steps_left)

    def __hash__(self):
        return hash((self.agent_a_pos, self.agent_b_pos, self.boxes,
                     self.score_a, self.score_b, self.steps_left))


_MOVE = {
    "North": (-1, 0),
    "South": (1,  0),
    "East":  (0,  1),
    "West":  (0, -1),
    "Wait":  (0,  0),
}


class TwoAgentProblem:
    def __init__(self, map_parser, pos_a: tuple, pos_b: tuple, n_steps: int):
        self.walls = map_parser.walls
        self.goals = map_parser.goals
        self.initial_state = TwoAgentState(
            agent_a_pos=pos_a,
            agent_b_pos=pos_b,
            boxes=map_parser.initial_boxes,
            score_a=0,
            score_b=0,
            steps_left=n_steps,
        )

    def is_terminal(self, state: TwoAgentState) -> bool:
        return (all(b in self.goals for b in state.boxes)
                or state.steps_left <= 0)

    def transition_model(self, state: TwoAgentState,
                         action_a: str, action_b: str) -> TwoAgentState:
        if self.is_terminal(state):
            return state

        # 1. Tính vị trí dự kiến
        dr_a, dc_a = _MOVE[action_a]
        dr_b, dc_b = _MOVE[action_b]
        next_a = (state.agent_a_pos[0] + dr_a, state.agent_a_pos[1] + dc_a)
        next_b = (state.agent_b_pos[0] + dr_b, state.agent_b_pos[1] + dc_b)

        # 2. Xử lý va chạm agent-agent
        # Đi xuyên qua nhau → cả hai đứng im
        if (next_a == state.agent_b_pos and next_b == state.agent_a_pos):
            next_a = state.agent_a_pos
            next_b = state.agent_b_pos
        # Cùng nhảy vào một ô → cả hai đứng im
        elif (next_a == next_b
              and action_a != "Wait" and action_b != "Wait"):
            next_a = state.agent_a_pos
            next_b = state.agent_b_pos

        new_boxes = set(state.boxes)
        owners = dict(state.box_owner)

        # 3. Xử lý Agent A di chuyển / đẩy thùng
        if next_a in self.walls:
            next_a = state.agent_a_pos
        elif next_a in new_boxes:
            box_next = (next_a[0] + dr_a, next_a[1] + dc_a)
            if (box_next in self.walls
                    or box_next in new_boxes
                    or box_next == next_b):
                next_a = state.agent_a_pos   # không đẩy được
            else:
                new_boxes.remove(next_a)
                new_boxes.add(box_next)
                owners.pop(next_a, None)
                owners[box_next] = "A"

        # 4. Xử lý Agent B di chuyển / đẩy thùng
        if next_b in self.walls:
            next_b = state.agent_b_pos
        elif next_b in new_boxes:
            box_next = (next_b[0] + dr_b, next_b[1] + dc_b)
            if (box_next in self.walls
                    or box_next in new_boxes
                    or box_next == next_a):
                next_b = state.agent_b_pos   # không đẩy được
            else:
                new_boxes.remove(next_b)
                new_boxes.add(box_next)
                owners.pop(next_b, None)
                owners[box_next] = "B"

        # 5. Tính lại điểm số
        score_a = sum(
            1 for box in new_boxes
            if box in self.goals and owners.get(box) == "A"
        )
        score_b = sum(
            1 for box in new_boxes
            if box in self.goals and owners.get(box) == "B"
        )

        return TwoAgentState(
            agent_a_pos=next_a,
            agent_b_pos=next_b,
            boxes=new_boxes,
            score_a=score_a,
            score_b=score_b,
            steps_left=state.steps_left - 1,
            box_owner=owners,
        )
