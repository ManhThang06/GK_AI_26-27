_MOVE = {
    "North": (-1, 0),
    "South": (1, 0),
    "West": (0, -1),
    "East": (0, 1),
    "Wait": (0, 0),
}

class TwoAgentState:
    def __init__(self, agent_a_pos, agent_b_pos, boxes,
                 score_a, score_b, steps_left, box_owner=None):
        self.agent_a_pos = agent_a_pos
        self.agent_b_pos = agent_b_pos
        self.boxes = frozenset(boxes)
        self.score_a = score_a
        self.score_b = score_b
        self.steps_left = steps_left

        if box_owner is None:
            owner = {box: None for box in boxes}
        elif isinstance(box_owner, dict):
            owner = dict(box_owner)
        else:
            owner = dict(box_owner)

        self.box_owner = frozenset(owner.items())

    def __eq__(self, other):
        return (
            isinstance(other, TwoAgentState)
            and self.agent_a_pos == other.agent_a_pos
            and self.agent_b_pos == other.agent_b_pos
            and self.boxes == other.boxes
            and self.score_a == other.score_a
            and self.score_b == other.score_b
            and self.steps_left == other.steps_left
            and self.box_owner == other.box_owner
        )

    def __hash__(self):
        return hash((
            self.agent_a_pos, self.agent_b_pos, self.boxes,
            self.score_a, self.score_b, self.steps_left, self.box_owner
        ))


class TwoAgentProblem:
    def __init__(self, map_data, initial_a, initial_b, n_steps):
        self.walls = set(map_data.walls)
        self.goals = set(map_data.goals)
        self.initial_state = TwoAgentState(
            initial_a, initial_b, map_data.initial_boxes,
            0, 0, n_steps, None
        )

    def is_terminal(self, state):
        return state.steps_left <= 0

    def _intent(self, agent_pos, action, boxes):
        dr, dc = _MOVE.get(action, (0, 0))
        next_pos = (agent_pos[0] + dr, agent_pos[1] + dc)

        if next_pos in self.walls:
            return agent_pos, None, None

        if next_pos in boxes:
            if action == "Wait":
                return agent_pos, None, None
            box_to = (next_pos[0] + dr, next_pos[1] + dc)
            return next_pos, next_pos, box_to

        return next_pos, None, None

    def transition_model(self, state, action_a, action_b):
        if self.is_terminal(state):
            return state

        old_boxes = set(state.boxes)

        next_a, a_from, a_to = self._intent(
            state.agent_a_pos, action_a, old_boxes
        )
        next_b, b_from, b_to = self._intent(
            state.agent_b_pos, action_b, old_boxes
        )

        valid_a = True
        valid_b = True

        if a_from is not None:
            if a_to in self.walls or a_to in old_boxes:
                valid_a = False

        if b_from is not None:
            if b_to in self.walls or b_to in old_boxes:
                valid_b = False

        if next_a == state.agent_b_pos and next_b == state.agent_a_pos:
            valid_a = False
            valid_b = False

        if next_a == next_b and (
            next_a != state.agent_a_pos or next_b != state.agent_b_pos
        ):
            valid_a = False
            valid_b = False

        if valid_a and a_from is not None and a_to == next_b:
            valid_a = False
        if valid_b and b_from is not None and b_to == next_a:
            valid_b = False

        if valid_a and valid_b and a_from is not None and b_from is not None:
            if a_from == b_from or a_to == b_to:
                valid_a = False
                valid_b = False

        if not valid_a:
            next_a = state.agent_a_pos
            a_from = a_to = None

        if not valid_b:
            next_b = state.agent_b_pos
            b_from = b_to = None

        if next_a == next_b:
            next_a = state.agent_a_pos
            next_b = state.agent_b_pos
            a_from = a_to = None
            b_from = b_to = None

        new_boxes = set(old_boxes)
        owners = dict(state.box_owner)

        if a_from is not None:
            new_boxes.remove(a_from)
            new_boxes.add(a_to)
            owners.pop(a_from, None)
            owners[a_to] = "A"

        if b_from is not None:
            new_boxes.remove(b_from)
            new_boxes.add(b_to)
            owners.pop(b_from, None)
            owners[b_to] = "B"

        score_a = sum(
            1 for box in new_boxes
            if box in self.goals and owners.get(box) == "A"
        )
        score_b = sum(
            1 for box in new_boxes
            if box in self.goals and owners.get(box) == "B"
        )

        return TwoAgentState(
            next_a, next_b, new_boxes,
            score_a, score_b, state.steps_left - 1, owners
        )
