import time
import heapq

class AgentAlgorithm2:
    ACTIONS = ("North", "South", "West", "East", "Wait")

    def __init__(self, heuristic=None, time_limit=1.0):
        self.heuristic = heuristic
        self.time_limit = time_limit
        self.target_box = None
        self.target_goal = None
        self.previous_boxes = None
        self.home_position = None
        self.steal_goal = None
        self.steal_box = None
        self.my_completed_goals = set()
        self.previous_score = 0
        self.lost_goal = None
        self.bad_pairs = set()
        self.bad_pairs_boxes = None
        self.plan_timeout = False
        self.target_from_opponent = False
        self.yield_to_opponent = True
        self.yield_count = 0
        self.max_yield = 1
        self.turn = 0
        self.wait_streak = 0
        self.max_wait = 4
        self.steal_blacklist = {}
        self.lost_steal_count = 0
        self.last_pos = None
        self.last_action = None
        self.stuck_count = 0
        self.max_stuck = 2
        self.box_blacklist = {}

    def set_heuristic(self, heuristic):
        self.heuristic = heuristic

    def clear_target(self):
        self.target_box = None
        self.target_goal = None
        self.target_from_opponent = False

    def next_cell(self, pos, action):
        moves = {
            "North": (-1, 0),
            "South": (1, 0),
            "West": (0, -1),
            "East": (0, 1),
            "Wait": (0, 0)
        }
        dr, dc = moves[action]
        return (pos[0] + dr, pos[1] + dc)

    def is_corner_deadlock(self, pos, problem):
        r, c = pos
        up = (r - 1, c) in problem.walls
        down = (r + 1, c) in problem.walls
        left = (r, c - 1) in problem.walls
        right = (r, c + 1) in problem.walls
        return (up and left) or (up and right) or (down and left) or (down and right)

    def select_target(self, agent_pos, boxes, problem, opponent, opponent_boxes, allow_opponent_boxes=False):
        self.target_from_opponent = False
        occupied_goals = set(boxes) & set(problem.goals)
        free_goals = set(problem.goals) - occupied_goals
        best_box = None
        best_goal = None
        best_priority = (float("inf"), float("inf"), float("inf"))

        for box in boxes:
            if box in occupied_goals:
                continue
            if box in opponent_boxes and not allow_opponent_boxes:
                continue
            if self.box_blacklist.get(box, -1) > self.turn:
                continue

            for goal in free_goals:
                if (box, goal) in self.bad_pairs:
                    continue
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
                total_distance = best_agent_distance + goal_distance
                priority = (total_distance, goal_distance, home_distance)
                if priority < best_priority:
                    best_priority = priority
                    best_box = box
                    best_goal = goal
        self.target_box = best_box
        self.target_goal = best_goal

    def choose_goal_for_box(self, box, boxes, problem):
        occupied_goals = set(boxes) & set(problem.goals)
        best_goal = None
        best_distance = float("inf")

        for goal in problem.goals:
            if goal in occupied_goals:
                continue
            if (box, goal) in self.bad_pairs:
                continue
            if box not in self.heuristic.maze_dist[goal]:
                continue
            goal_distance = self.heuristic.maze_dist[goal][box]
            if goal_distance < best_distance:
                best_distance = goal_distance
                best_goal = goal

        if best_goal is None:
            self.clear_target()
        else:
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

    def bfs_first_action(self, start, target, walls, blocked, deadline):
        if start == target:
            return "Wait"

        directions = [
            ("North", -1, 0), ("South", 1, 0),
            ("West", 0, -1), ("East", 0, 1)
        ]
        queue = [(start, None)]
        explored = {start}

        while queue:
            if time.perf_counter() >= deadline:
                return None

            current, first = queue.pop(0)

            for action, dr, dc in directions:
                next_pos = (current[0] + dr, current[1] + dc)

                if next_pos in explored:
                    continue
                if next_pos in walls:
                    continue
                if next_pos in blocked:
                    continue

                first_action = action if first is None else first

                if next_pos == target:
                    return first_action

                explored.add(next_pos)
                queue.append((next_pos, first_action))

        return None

    def plan_box_to_goal(self, agent_start, box, goal, other_boxes, problem, opponent, deadline, forbidden_first=None):
        if box == goal:
            return ("Wait", 0)
        if goal not in self.heuristic.maze_dist:
            return None
        goal_map = self.heuristic.maze_dist[goal]
        if box not in goal_map:
            return None

        directions = [
            ("North", -1, 0), ("South", 1, 0),
            ("West", 0, -1), ("East", 0, 1)
        ]

        start = (agent_start, box)
        count = 0
        frontier = [(goal_map[box], 0, count, agent_start, box, None)]
        best_cost = {start: 0}

        while frontier:
            if time.perf_counter() >= deadline:
                self.plan_timeout = True
                return None

            f, cost, _, agent_pos, box_pos, first_action = heapq.heappop(frontier)

            if cost > best_cost.get((agent_pos, box_pos), float("inf")):
                continue

            if box_pos == goal:
                return (first_action, cost)

            for action, dr, dc in directions:
                next_agent = (agent_pos[0] + dr, agent_pos[1] + dc)
                next_box = box_pos

                if next_agent in problem.walls or next_agent in other_boxes:
                    continue
                if next_agent == opponent:
                    continue
                if cost == 0 and forbidden_first is not None:
                    if next_agent in forbidden_first:
                        continue

                if next_agent == box_pos:
                    pushed_box = (box_pos[0] + dr, box_pos[1] + dc)

                    if pushed_box in problem.walls:
                        continue
                    if pushed_box in other_boxes:
                        continue
                    if pushed_box == opponent:
                        continue
                    if pushed_box not in goal_map:
                        continue
                    if pushed_box != goal and self.is_corner_deadlock(pushed_box, problem):
                        continue

                    next_box = pushed_box

                next_state = (next_agent, next_box)
                next_cost = cost + 1

                if next_cost >= best_cost.get(next_state, float("inf")):
                    continue

                best_cost[next_state] = next_cost
                next_first = action if first_action is None else first_action

                count += 1
                heapq.heappush(
                    frontier,
                    (next_cost + goal_map[next_box], next_cost, count, next_agent, next_box, next_first)
                )

        return None

    def plan_stolen_box_to_goal(self, state, problem, box, goal, deadline):
        agent_start = state.agent_b_pos
        opponent = state.agent_a_pos
        other_boxes = set(state.boxes)
        other_boxes.discard(box)

        result = self.plan_box_to_goal(
            agent_start, box, goal, other_boxes, problem, opponent, deadline
        )

        if result is None:
            result = self.plan_box_to_goal(
                agent_start, box, goal, other_boxes, problem, None, deadline
            )
            if result is None:
                return None
            if self.next_cell(agent_start, result[0]) == opponent:
                return "Wait"

        return result[0]

    def can_finish_steal(self, state, problem, goal, push_action, dr, dc, deadline):
        agent_pos = state.agent_b_pos
        opponent = state.agent_a_pos

        push_pos = (goal[0] - dr, goal[1] - dc)
        box_out = (goal[0] + dr, goal[1] + dc)

        if push_pos in problem.walls or push_pos in state.boxes:
            return None
        if box_out in problem.walls or box_out in state.boxes:
            return None

        blocked = set(state.boxes)
        blocked.add(opponent)

        first_action = self.bfs_first_action(
            agent_pos, push_pos, problem.walls, blocked, deadline
        )
        if first_action is None:
            blocked = set(state.boxes)
            first_action = self.bfs_first_action(
                agent_pos, push_pos, problem.walls, blocked, deadline
            )
            if first_action is None:
                return None

        class TempState:
            pass

        temp = TempState()
        temp.agent_b_pos = goal
        temp.agent_a_pos = opponent

        new_boxes = set(state.boxes)
        new_boxes.remove(goal)
        new_boxes.add(box_out)
        temp.boxes = frozenset(new_boxes)

        return_action = self.plan_stolen_box_to_goal(
            temp, problem, box_out, goal, deadline
        )

        if return_action is None:
            return None

        distance = self.bfs_distance(
            agent_pos, push_pos, problem.walls, blocked
        )

        if push_pos == opponent or box_out == opponent:
            distance += 100

        return (distance, push_pos, push_action, first_action)

    def choose_steal_action(self, state, problem, deadline, preferred_goals=None):
        agent_pos = state.agent_b_pos
        opponent = state.agent_a_pos
        owners = dict(state.box_owner)

        directions = [
            ("North", -1, 0), ("South", 1, 0),
            ("West", 0, -1), ("East", 0, 1)
        ]

        # Dang trong mot lan cuop.
        if self.steal_goal is not None:
            goal = self.steal_goal

            if goal in state.boxes and owners.get(goal) == "B":
                if self.lost_goal == goal:
                    self.lost_goal = None
                self.steal_goal = None
                self.steal_box = None
                self.clear_target()
                return None

            if goal in state.boxes and owners.get(goal) == "A":
                best = None

                for push_action, dr, dc in directions:
                    if time.perf_counter() >= deadline:
                        break

                    candidate = self.can_finish_steal(
                        state, problem, goal,
                        push_action, dr, dc, deadline
                    )

                    if candidate is None:
                        continue

                    if best is None or candidate[0] < best[0]:
                        best = candidate

                if best is None:
                    failed_goal = goal
                    self.steal_goal = None
                    self.steal_box = None
                    self.clear_target()

                    other_goals = {
                        box for box in state.boxes
                        if box in problem.goals
                        and owners.get(box) == "A"
                        and box != failed_goal
                    }

                    if other_goals:
                        return self.choose_steal_action(
                            state, problem, deadline, other_goals
                        )

                    return None

                _, push_pos, push_action, first_action = best

                if agent_pos == push_pos:
                    dr, dc = dict(
                        (a, (r, c)) for a, r, c in directions
                    )[push_action]
                    if (goal[0] + dr, goal[1] + dc) == opponent:
                        return "Wait"
                    self.steal_box = (goal[0] + dr, goal[1] + dc)
                    return push_action

                return first_action

            stolen_box = None

            if self.target_box in state.boxes and owners.get(self.target_box) == "B":
                stolen_box = self.target_box
            elif self.steal_box in state.boxes and owners.get(self.steal_box) == "B":
                stolen_box = self.steal_box
            else:
                for _, dr, dc in directions:
                    box = (goal[0] + dr, goal[1] + dc)
                    if box in state.boxes and owners.get(box) == "B":
                        stolen_box = box
                        break

            if stolen_box is not None:
                self.lost_steal_count = 0
                self.steal_box = stolen_box
                self.target_box = stolen_box
                self.target_goal = goal

                plan_action = self.plan_stolen_box_to_goal(
                    state, problem, stolen_box, goal, deadline
                )

                if plan_action is not None:
                    return plan_action
                return "Wait"

            self.lost_steal_count += 1
            if self.lost_steal_count >= 3:
                self.steal_goal = None
                self.steal_box = None
                self.lost_steal_count = 0
                self.clear_target()
                return None
            return "Wait"

        best = None

        for box in state.boxes:
            if time.perf_counter() >= deadline:
                break
            if box not in problem.goals:
                continue
            if owners.get(box) != "A":
                continue
            if preferred_goals is not None and box not in preferred_goals:
                continue
            if self.steal_blacklist.get(box, -1) > self.turn:
                continue

            for push_action, dr, dc in directions:
                if time.perf_counter() >= deadline:
                    break

                candidate = self.can_finish_steal(
                    state, problem, box,
                    push_action, dr, dc, deadline
                )

                if candidate is None:
                    continue

                distance, push_pos, chosen_push, first_action = candidate
                item = (
                    distance, box, push_pos,
                    chosen_push, first_action
                )

                if best is None or item[0] < best[0]:
                    best = item

        if best is None:
            return None

        _, goal, push_pos, push_action, first_action = best
        self.steal_goal = goal
        self.steal_box = None
        self.clear_target()

        if agent_pos == push_pos:
            dr, dc = dict(
                (a, (r, c)) for a, r, c in directions
            )[push_action]
            if (goal[0] + dr, goal[1] + dc) == opponent:
                return "Wait"
            self.steal_box = (goal[0] + dr, goal[1] + dc)
            return push_action

        return first_action

    def greedy_push_action(self, state, problem, deadline):
        agent_pos = state.agent_b_pos
        opponent = state.agent_a_pos
        box = self.target_box
        goal_map = self.heuristic.maze_dist[self.target_goal]

        directions = [
            ("North", -1, 0), ("South", 1, 0),
            ("West", 0, -1), ("East", 0, 1)
        ]
        best = None

        for push_action, dr, dc in directions:
            push_pos = (box[0] - dr, box[1] - dc)
            box_next = (box[0] + dr, box[1] + dc)

            if push_pos in problem.walls or push_pos in state.boxes:
                continue
            if push_pos == opponent:
                continue
            if box_next in problem.walls or box_next in state.boxes:
                continue
            if box_next == opponent:
                continue
            if box_next not in goal_map:
                continue

            if agent_pos == push_pos:
                distance = 0
                first_action = push_action
            else:
                blocked = set(state.boxes)
                blocked.add(opponent)
                first_action = self.bfs_first_action(
                    agent_pos, push_pos, problem.walls, blocked, deadline
                )
                if first_action is None:
                    continue
                distance = self.bfs_distance(
                    agent_pos, push_pos, problem.walls, blocked
                )

            item = (goal_map[box_next], distance, first_action)
            if best is None or item[:2] < best[:2]:
                best = item

        if best is None:
            return "Wait"
        return best[2]

    def choose_push_action(self, state, problem, deadline):
        agent_pos = state.agent_b_pos
        opponent = state.agent_a_pos
        other_boxes = set(state.boxes)
        other_boxes.discard(self.target_box)

        remain = deadline - time.perf_counter()
        plan_deadline = time.perf_counter() + remain * 0.7
        self.plan_timeout = False

        best = self.plan_box_to_goal(
            agent_pos, self.target_box, self.target_goal,
            other_boxes, problem, opponent, plan_deadline
        )

        if best is None and self.plan_timeout:
            return self.greedy_push_action(state, problem, deadline)

        if best is None:
            best = self.plan_box_to_goal(
                agent_pos, self.target_box, self.target_goal,
                other_boxes, problem, None, plan_deadline
            )
            if best is not None:
                if self.next_cell(agent_pos, best[0]) == opponent:
                    return "Wait"
                return best[0]

            if self.plan_timeout:
                return self.greedy_push_action(state, problem, deadline)

            self.bad_pairs.add((self.target_box, self.target_goal))
            self.bad_pairs_boxes = frozenset(state.boxes)
            return None

        action = best[0]

        next_pos = self.next_cell(agent_pos, action)
        if abs(next_pos[0] - opponent[0]) + abs(next_pos[1] - opponent[1]) <= 1:
            danger = {
                opponent,
                (opponent[0] - 1, opponent[1]),
                (opponent[0] + 1, opponent[1]),
                (opponent[0], opponent[1] - 1),
                (opponent[0], opponent[1] + 1)
            }
            safe = self.plan_box_to_goal(
                agent_pos, self.target_box, self.target_goal,
                other_boxes, problem, opponent, plan_deadline, danger
            )
            if safe is not None and safe[1] <= best[1] + 1:
                action = safe[0]

        return action

    def avoid_collision(self, action, state, problem):
        agent_pos = state.agent_b_pos
        opponent = state.agent_a_pos

        if action is None or action == "Wait":
            self.yield_count = 0
            return "Wait"

        next_pos = self.next_cell(agent_pos, action)

        if next_pos == opponent:
            return "Wait"

        distance = abs(next_pos[0] - opponent[0]) + abs(next_pos[1] - opponent[1])
        if distance > 1:
            self.yield_count = 0
            return action

        if not self.yield_to_opponent:
            return action

        if self.yield_count >= self.max_yield:
            self.yield_count = 0
            return action

        self.yield_count += 1
        return "Wait"

    def choose_action(self, state, problem):
        agent_pos = state.agent_b_pos

        if self.last_action not in (None, "Wait") and self.last_pos == agent_pos:
            self.stuck_count += 1
        else:
            self.stuck_count = 0

        action = self.decide_action(state, problem)
        action = self.avoid_collision(action, state, problem)
        if action == "Wait":
            self.wait_streak += 1
        else:
            self.wait_streak = 0

        self.last_pos = agent_pos
        self.last_action = action
        return action

    def decide_action(self, state, problem):
        deadline = time.perf_counter() + self.time_limit
        if self.heuristic is None:
            return "Wait"
        if self.home_position is None:
            self.home_position = state.agent_b_pos

        owners = dict(state.box_owner)
        opponent = state.agent_a_pos
        self.turn += 1

        if self.steal_goal is not None and self.wait_streak >= self.max_wait:
            if self.steal_goal in state.boxes and owners.get(self.steal_goal) == "A":
                self.steal_blacklist[self.steal_goal] = self.turn + 15
                self.steal_goal = None
                self.steal_box = None
                self.wait_streak = 0
                self.clear_target()

        if self.stuck_count >= self.max_stuck and self.steal_goal is None:
            if self.target_box is not None:
                self.box_blacklist[self.target_box] = self.turn + 15
                self.clear_target()
            self.stuck_count = 0

        self.update_target_box(state.boxes)

        if self.bad_pairs_boxes != frozenset(state.boxes):
            self.bad_pairs = set()
            self.bad_pairs_boxes = None

        current_score = state.score_b

        if current_score < self.previous_score:
            for goal in self.my_completed_goals:
                if goal in state.boxes and owners.get(goal) == "A":
                    self.lost_goal = goal
                    break

        self.previous_score = current_score

        for box in state.boxes:
            if box in problem.goals and owners.get(box) == "B":
                self.my_completed_goals.add(box)

        no_target = self.target_box is None or self.target_goal is None

        if self.lost_goal is not None and self.steal_goal is None and no_target:
            if self.lost_goal in state.boxes and owners.get(self.lost_goal) == "B":
                self.lost_goal = None
            else:
                revenge_action = self.choose_steal_action(
                    state, problem, deadline, {self.lost_goal}
                )

                if revenge_action is not None:
                    return revenge_action

        lost_goals = []
        for goal in self.my_completed_goals:
            if goal in state.boxes and owners.get(goal) == "A":
                lost_goals.append(goal)

        if lost_goals and self.steal_goal is None and no_target:
            revenge_action = self.choose_steal_action(
                state, problem, deadline, set(lost_goals)
            )

            if revenge_action is not None:
                return revenge_action

        if self.steal_goal is not None:
            steal_action = self.choose_steal_action(state, problem, deadline)
            if steal_action is not None:
                return steal_action

        no_target = self.target_box is None or self.target_goal is None
        if self.steal_goal is None and no_target:
            steal_action = self.choose_steal_action(state, problem, deadline)
            if steal_action is not None:
                return steal_action

        box_owner = dict(state.box_owner)
        opponent_boxes = set()

        for box, owner in box_owner.items():
            if owner == "A":
                opponent_boxes.add(box)

        if self.target_box in opponent_boxes:
            if self.steal_goal is None and not self.target_from_opponent:
                self.clear_target()

        if self.target_box is not None:
            if self.target_box not in state.boxes:
                self.clear_target()

        if self.target_box is not None:
            if self.target_box in problem.goals:
                if self.steal_goal is None:
                    self.clear_target()

        if self.target_box is not None and self.target_goal is not None:
            if self.target_goal in state.boxes:
                if self.target_box != self.target_goal:
                    self.choose_goal_for_box(self.target_box, state.boxes, problem)

        for _ in range(3):
            if self.target_box is None or self.target_goal is None:
                self.select_target(state.agent_b_pos, state.boxes, problem, opponent, opponent_boxes)
            if self.target_box is None or self.target_goal is None:
                # Het box "sach": lay ca box doi thu day ra ngoai goal, dung dung yen
                self.select_target(state.agent_b_pos, state.boxes, problem, opponent, opponent_boxes, True)
                if self.target_box is not None and self.target_goal is not None:
                    self.target_from_opponent = True
            if self.target_box is None or self.target_goal is None:
                return "Wait"

            push_action = self.choose_push_action(state, problem, deadline)
            if push_action is not None:
                return push_action
            self.clear_target()
        return "Wait"