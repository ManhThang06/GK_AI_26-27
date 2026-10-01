import time
import heapq

class AgentAlgorithm2:
    ACTIONS = ("North", "South", "West", "East", "Wait")

    def __init__(self, heuristic=None, time_limit=1.0):
        self.heuristic = heuristic
        self.time_limit = time_limit

    def set_heuristic(self, heuristic):
        self.heuristic = heuristic

    def choose_action(self, state, problem):
        deadline = time.perf_counter() + self.time_limit
        best_action = "Wait"
        if self.heuristic is None:
            return best_action
        current_h = self.heuristic.evaluate(state.boxes)

        start = (state.agent_b_pos, state.boxes)
        opponent = state.agent_a_pos
        frontier = []
        count = 0
        heapq.heappush(frontier,(current_h, count, state.agent_b_pos, state.boxes))
        frontier_h = {
            start: current_h
        }
        explored = set()
        parent = {
            start: None
        }
        parent_action = {
            start: None
        }

        directions = {
            "North": (-1, 0),
            "South": (1, 0),
            "West": (0, -1),
            "East": (0, 1),
            "Wait": (0, 0)
        }

        while frontier:
            if time.perf_counter() >= deadline:
                return best_action
            h, _, agent_pos, boxes = heapq.heappop(frontier)
            current = (agent_pos, boxes)
            if current in explored:
                continue
            frontier_h.pop(current, None)
            if h < current_h:
                node = current
                while parent[node] != start:
                    node = parent[node]
                best_action = parent_action[node]
                return best_action
            explored.add(current)

            for action in self.ACTIONS:
                if time.perf_counter() >= deadline:
                    return best_action
                dr, dc = directions[action]

                next_agent = (agent_pos[0] + dr, agent_pos[1] + dc)
                if next_agent == opponent:
                    continue
                if next_agent in problem.walls:
                    continue
                next_boxes = boxes
                if next_agent in boxes:
                    if action == "Wait":
                        continue
                    next_box = (next_agent[0] + dr, next_agent[1] + dc)
                    if (next_box in problem.walls or next_box in boxes or next_box == opponent):
                        continue
                    new_boxes = set(boxes)
                    new_boxes.remove(next_agent)
                    new_boxes.add(next_box)
                    next_boxes = frozenset(new_boxes)
                
                next_state = (next_agent, next_boxes)
                if next_state in explored:
                    continue
                if next_state in frontier_h:
                    continue
                next_h = self.heuristic.evaluate(next_boxes)
                parent[next_state] = current
                parent_action[next_state] = action
                count += 1
                frontier_h[next_state] = next_h
                heapq.heappush(frontier, (next_h, count, next_agent, next_boxes))
        return best_action