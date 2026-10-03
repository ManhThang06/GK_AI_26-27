import time
import heapq

class AgentAlgorithm2:
    ACTIONS = ("North", "South", "West", "East", "Wait")

    def __init__(self, heuristic=None, time_limit=1.0):
        self.heuristic = heuristic
        self.time_limit = time_limit

    def set_heuristic(self, heuristic):
        self.heuristic = heuristic

    def bfs_distance(self, start, target, walls, blocked):
        if start == target:
            return 0
        queue = [(start, 0)]
        explored = {start}
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]
        while queue:
            current, distance = queue.pop(0)
            for dr, dc in directions:
                next_pos = (current[0] + dr, current[1] + dc)
                if next_pos in explored:
                    continue
                if next_pos in walls:
                    continue
                if next_pos in blocked:
                    continue
                if next_pos == target:
                    return distance + 1
                explored.add(next_pos)
                queue.append((next_pos, distance + 1))
        return float("inf")
    
    def get_push_distance(self, agent_pos, boxes, problem, opponent):
        min_distance = (float("inf"), float("inf"))
        occupied_goals = set(boxes) & set(problem.goals)
        free_goals = set(problem.goals) - occupied_goals
        if not free_goals:
            return (0, 0)
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]
        for box in boxes:
            if box in occupied_goals:
                continue
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
                goal_distance = float("inf")
                for goal in free_goals:
                    if box_next in self.heuristic.maze_dist[goal]:
                        d = self.heuristic.maze_dist[goal][box_next]
                        if d < goal_distance:
                            goal_distance = d
                if goal_distance == float("inf"):
                    continue
                blocked = set(boxes)
                blocked.add(opponent)
                distance = self.bfs_distance(agent_pos, push_pos, problem.walls, blocked)
                if distance == float("inf"):
                    continue
                push_priority = (goal_distance, distance)
                min_distance = min(min_distance, push_priority)
        return min_distance
    
    def choose_action(self, state, problem):
        deadline = time.perf_counter() + self.time_limit
        if self.heuristic is None:
            return "Wait"
        start = (state.agent_b_pos, state.boxes)
        opponent = state.agent_a_pos
        current_h = self.heuristic.evaluate(state.boxes)
        start_push_distance = self.get_push_distance(state.agent_b_pos, state.boxes, problem, opponent)
        frontier = []
        count = 0
        heapq.heappush(frontier,(current_h, start_push_distance, count, state.agent_b_pos, state.boxes))
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
                next_push_distance = self.get_push_distance(next_agent, next_boxes, problem, opponent)
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