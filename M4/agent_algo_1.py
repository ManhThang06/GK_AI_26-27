import time
import heapq

class AgentAlgorithm1:
    ACTIONS = ("North", "South", "West", "East", "Wait")

    def __init__(self, heuristic=None, time_limit=1.0):
        self.heuristic = heuristic
        self.time_limit = time_limit

    def set_heuristic(self, heuristic):
        self.heuristic = heuristic

    def get_push_distance(self, agent_pos, boxes, problem):
        min_distance = float("inf")
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]
        for box in boxes:
            br, bc = box
            for dr, dc in directions:
                push_pos = (br - dr, bc - dc)
                box_next = (br + dr, bc + dc)
                if push_pos in problem.walls:
                    continue
                if push_pos in boxes:
                    continue
                if box_next in problem.walls:
                    continue
                if box_next in boxes:
                    continue
                distance = (abs(agent_pos[0] - push_pos[0]) + abs(agent_pos[1] - push_pos[1]))
                min_distance = min(min_distance, distance)
        return min_distance
    
    def choose_action(self, state, problem):
        deadline = time.perf_counter() + self.time_limit
        if self.heuristic is None:
            return "Wait"
        start = (state.agent_a_pos, state.boxes)
        opponent = state.agent_b_pos
        current_h = self.heuristic.evaluate(state.boxes)
        frontier = []
        count = 0
        start_push_distance = self.get_push_distance(state.agent_a_pos, state.boxes, problem)
        heapq.heappush(frontier, (current_h, start_push_distance, count, state.agent_a_pos, state.boxes))
        frontier_h = {start: current_h}
        explored = set()
        parent = {start: None}
        parent_action = {start: None}
        directions = {
            "North": (-1, 0),
            "South": (1, 0),
            "West": (0, -1),
            "East": (0, 1),
            "Wait": (0, 0)
        }
        best_state = start
        best_h = current_h
        best_push_distance = start_push_distance
        while frontier:
            if time.perf_counter() >= deadline:
                break
            h, push_distance, _, agent_pos, boxes = heapq.heappop(frontier)
            current = (agent_pos, boxes)
            if current in explored:
                continue
            frontier_h.pop(current, None)
            explored.add(current)
            if (
                h < best_h
                or (
                    h == best_h
                    and push_distance < best_push_distance
                )
            ):
                best_h = h
                best_push_distance = push_distance
                best_state = current
            if all(box in problem.goals for box in boxes):
                best_state = current
                break
            for action in self.ACTIONS:
                if time.perf_counter() >= deadline:
                    break
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
                    if next_box not in problem.goals:
                        r, c = next_box
                        up = (r - 1, c) in problem.walls
                        down = (r + 1, c) in problem.walls
                        left = (r, c - 1) in problem.walls
                        right = (r, c + 1) in problem.walls
                        if ((up and left) or (up and right) or (down and left) or (down and right)):
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
                next_push_distance = self.get_push_distance(next_agent, next_boxes, problem)
                parent[next_state] = current
                parent_action[next_state] = action
                count += 1
                frontier_h[next_state] = next_h
                heapq.heappush(frontier, (next_h, next_push_distance, count, next_agent, next_boxes))
        if best_state == start:
            return "Wait"
        node = best_state
        while parent[node] != start:
            node = parent[node]
        return parent_action[node]