class State:
    def __init__(self, agent_pos, box_positions):
        self.agent_pos = agent_pos
        self.box_positions = frozenset(box_positions)

    def __eq__(self, other):
        return (self.agent_pos == other.agent_pos and
                self.box_positions == other.box_positions)

    def __hash__(self):
        return hash((self.agent_pos, self.box_positions))


class SokobanProblem:
    ACTIONS = {
        'North': (-1, 0),
        'South': (1, 0),
        'East':  (0, 1),
        'West':  (0, -1),
    }

    def __init__(self, map_path):
        self.walls, self.goals, agent, boxes = self._parse_map(map_path)
        self.initial_state = State(agent, boxes)

    def _parse_map(self, map_path):
        walls, goals, boxes = set(), set(), set()
        agent = None
        with open(map_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for r, line in enumerate(lines):
            line = line.rstrip('\n')
            for c, ch in enumerate(line):
                pos = (r, c)
                if ch == '%':
                    walls.add(pos)
                elif ch == 'A':
                    agent = pos
                elif ch == 'B':
                    boxes.add(pos)
                elif ch == 'D':
                    goals.add(pos)
                elif ch == 'C':
                    boxes.add(pos)
                    goals.add(pos)
        return walls, goals, agent, boxes

    def actions(self, state):
        valid = []
        for action, (dr, dc) in self.ACTIONS.items():
            new_agent = (state.agent_pos[0] + dr, state.agent_pos[1] + dc)
            if new_agent in self.walls:
                continue
            if new_agent in state.box_positions:
                new_box = (new_agent[0] + dr, new_agent[1] + dc)
                if new_box in self.walls or new_box in state.box_positions:
                    continue
            valid.append(action)
        return valid

    def result(self, state, action):
        dr, dc = self.ACTIONS[action]
        new_agent = (state.agent_pos[0] + dr, state.agent_pos[1] + dc)
        new_boxes = set(state.box_positions)
        if new_agent in state.box_positions:
            new_box = (new_agent[0] + dr, new_agent[1] + dc)
            new_boxes.remove(new_agent)
            new_boxes.add(new_box)
        return State(new_agent, new_boxes)

    def goal_test(self, state):
        return state.box_positions == frozenset(self.goals)

    def step_cost(self, state, action):
        return 1