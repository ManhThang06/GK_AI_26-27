import time
import heapq

class _GBFSAgent:
    agent_key = "A"
    ACTIONS = ("North", "South", "West", "East", "Wait")

    def __init__(self, heuristic=None, time_limit=1.0):
        self.heuristic = heuristic
        self.time_limit = time_limit
        self.target_box = None
        self.target_goal = None
        self.previous_boxes = None
        self.home_position = None

    def set_heuristic(self, heuristic):
        self.heuristic = heuristic

    def clear_target(self):
        self.target_box = None
        self.target_goal = None

    def select_target(self, agent_pos, boxes, problem, opponent, opponent_boxes):
        occupied_goals = set(boxes) & set(problem.goals)
        free_goals = set(problem.goals) - occupied_goals
        best_box = None
        best_goal = None
        best_priority = (float("inf"), float("inf"), float("inf"))

        for box in boxes:
            if box in occupied_goals:
                continue
            if box in opponent_boxes:
                continue

            for goal in free_goals:
                if box not in self.heuristic.maze_dist[goal]:
                    continue
                goal_distance = self.heuristic.maze_dist[goal][box]
                directions = [
                    (-1, 0),
                    (1, 0),
                    (0, -1),
                    (0, 1)
                ]
                best_agent_distance = float("inf")

                for dr, dc in directions:
                    push_pos = (box[0] - dr, box[1] - dc)
                    box_next = (box[0] + dr, box[1] + dc)

                    if push_pos in problem.walls:
                        continue
                    if push_pos in boxes:
                        continue
                    if push_pos == opponent:
                        continue
                    if box_next in problem.walls:
                        continue
                    if box_next in boxes:
                        continue
                    if box_next == opponent:
                        continue

                    blocked = set(boxes)
                    blocked.add(opponent)
                    agent_distance = self.bfs_distance(agent_pos, push_pos, problem.walls, blocked)
                    if agent_distance < best_agent_distance:
                        best_agent_distance = agent_distance

                if best_agent_distance == float("inf"):
                    continue
                home_distance = self.bfs_distance(self.home_position, box, problem.walls, set())
                priority = (best_agent_distance, goal_distance, home_distance)
                if priority < best_priority:
                    best_priority = priority
                    best_box = box
                    best_goal = goal
        self.target_box = best_box
        self.target_goal = best_goal

    def update_target_box(self, boxes):
        if self.target_box is None:
            self.previous_boxes = set(boxes)
            return
        if self.previous_boxes is None:
            self.previous_boxes = set(boxes)
            return

        old_boxes = set(self.previous_boxes)
        current_boxes = set(boxes)

        if self.target_box not in current_boxes:
            old_target = self.target_box
            new_positions = current_boxes - old_boxes

            possible_positions = {
                (old_target[0] - 1, old_target[1]),
                (old_target[0] + 1, old_target[1]),
                (old_target[0], old_target[1] - 1),
                (old_target[0], old_target[1] + 1)
            }

            moved_positions = new_positions & possible_positions

            if len(moved_positions) == 1:
                self.target_box = next(iter(moved_positions))
            else:
                self.clear_target()

        self.previous_boxes = current_boxes
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

    def can_continue_push(self, agent_pos, box_pos, boxes, problem, opponent):
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]

        for dr, dc in directions:
            push_pos = (box_pos[0] - dr, box_pos[1] - dc)
            next_box = (box_pos[0] + dr, box_pos[1] + dc)

            if push_pos in problem.walls:
                continue
            if push_pos in boxes:
                continue
            if push_pos == opponent:
                continue
            if next_box in problem.walls:
                continue
            if next_box in boxes:
                continue
            if next_box == opponent:
                continue
            blocked = set(boxes)
            blocked.add(opponent)
            distance = self.bfs_distance(agent_pos, push_pos, problem.walls, blocked)
            if distance != float("inf"):
                return True
        return False

    def get_push_distance(self, agent_pos, boxes, problem, opponent, target_box):
        min_distance = (float("inf"), float("inf"), float("inf"))
        occupied_goals = set(boxes) & set(problem.goals)
        free_goals = set(problem.goals) - occupied_goals
        if not free_goals:
            return (0, 0, 0)
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]

        for box in boxes:
            if box in occupied_goals:
                continue
            if target_box is not None:
                if box != target_box:
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

                after_boxes = set(boxes)
                after_boxes.remove(box)
                after_boxes.add(box_next)
                if box_next != self.target_goal:
                    if not self.can_continue_push(box, box_next, after_boxes, problem, opponent):
                        continue

                goal = self.target_goal
                if goal is None:
                    continue
                if goal not in free_goals:
                    continue
                if box_next not in self.heuristic.maze_dist[goal]:
                    continue
                goal_distance = self.heuristic.maze_dist[goal][box_next]

                if goal_distance == float("inf"):
                    continue
                blocked = set(boxes)
                blocked.add(opponent)
                distance = self.bfs_distance(agent_pos, push_pos, problem.walls, blocked)
                if distance == float("inf"):
                    continue
                if box not in self.heuristic.maze_dist[goal]:
                    continue

                before_distance = self.heuristic.maze_dist[goal][box]
                if goal_distance < before_distance:
                    progress = 0
                elif goal_distance == before_distance:
                    progress = 1
                else:
                    progress = 2
                push_priority = (progress, goal_distance, distance)
                min_distance = min(min_distance, push_priority)
        return min_distance
    
    def choose_action(self, state, problem):
        deadline = time.perf_counter() + self.time_limit
        if self.heuristic is None:
            return "Wait"
        if self.agent_key == "A":
            my_pos = state.agent_a_pos
            opponent = state.agent_b_pos
            opponent_key = "B"
        else:
            my_pos = state.agent_b_pos
            opponent = state.agent_a_pos
            opponent_key = "A"

        if self.home_position is None:
            self.home_position = my_pos

        box_owner = dict(state.box_owner)
        opponent_boxes = set()

        for box, owner in box_owner.items():
            if owner == opponent_key:
                opponent_boxes.add(box)

        self.update_target_box(state.boxes)

        if self.target_box in opponent_boxes:
            self.clear_target()

        if self.target_box is not None:
            if self.target_box not in state.boxes:
                self.clear_target()

        if self.target_box is not None:
            if self.target_box in problem.goals:
                self.clear_target()

        if self.target_goal is not None:
            if self.target_goal in state.boxes:
                if self.target_box != self.target_goal:
                    self.clear_target()
        if self.target_box is None or self.target_goal is None:
            self.select_target(my_pos, state.boxes, problem, opponent, opponent_boxes)
        start = (my_pos, state.boxes, self.target_box)
        current_h = self.heuristic.evaluate(state.boxes)
        frontier = []
        count = 0

        start_push_distance = self.get_push_distance(my_pos, state.boxes, problem, opponent, self.target_box)
        heapq.heappush(frontier, (current_h, start_push_distance, count, my_pos, state.boxes, self.target_box))
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
            h, push_distance, _, agent_pos, boxes, target_box = heapq.heappop(frontier)
            current = (agent_pos, boxes, target_box)
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
                next_target_box = target_box
                next_boxes = boxes
                if next_agent in boxes:
                    if action == "Wait":
                        continue
                    if target_box is not None:
                        if next_agent != target_box:
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
                    if next_agent == target_box:
                        next_target_box = next_box
                next_state = (next_agent, next_boxes, next_target_box)
                if next_state in explored:
                    continue
                if next_state in frontier_h:
                    continue
                next_h = self.heuristic.evaluate(next_boxes)
                next_push_distance = self.get_push_distance(next_agent, next_boxes, problem, opponent, next_target_box)
                parent[next_state] = current
                parent_action[next_state] = action
                count += 1
                frontier_h[next_state] = next_h
                heapq.heappush(frontier, (next_h, next_push_distance, count, next_agent, next_boxes, next_target_box))
        if best_state == start:
            return "Wait"
        node = best_state
        while parent[node] != start:
            node = parent[node]
        return parent_action[node]

class AgentA(_GBFSAgent):
    """Agent A - điều khiển agent_a_pos."""
    agent_key = "A"

class AgentB(_GBFSAgent):
    """Agent B - điều khiển agent_b_pos."""
    agent_key = "B"