import time
import heapq
from types import SimpleNamespace
class AgentAlgorithm2:
    ACTIONS = ("North", "South", "West", "East", "Wait"); 
    DIRECTIONS = (("North", -1, 0), ("South", 1, 0), ("West", 0, -1), ("East", 0, 1))
    MOVES = {"North": (-1, 0), "South": (1, 0), "West": (0, -1), "East": (0, 1), "Wait": (0, 0)}

    def __init__(self, heuristic=None, time_limit=1.0):
        self.heuristic = heuristic; 
        self.time_limit = time_limit
        self.target_box = self.target_goal = None; 
        self.previous_boxes = self.home_position = None
        self.steal_goal = self.steal_box = self.lost_goal = None; 
        self.my_completed_goals = set()
        self.previous_score = 0; 
        self.bad_pairs = set()
        self.bad_pairs_boxes = None; 
        self.plan_timeout = False
        self.target_from_opponent = False; 
        self.yield_to_opponent = True
        self.yield_count = 0; 
        self.max_yield = 1
        self.turn = 0; 
        self.wait_streak = 0
        self.max_wait = 4; 
        self.steal_blacklist = {}
        self.lost_steal_count = 0; 
        self.last_pos = None
        self.last_action = None; 
        self.stuck_count = 0
        self.max_stuck = 2; 
        self.box_blacklist = {}

    def set_heuristic(self, heuristic):
        self.heuristic = heuristic

    def clear_target(self):
        self.target_box = None; 
        self.target_goal = None
        self.target_from_opponent = False

    def end_steal(self):
        self.steal_goal = None; 
        self.steal_box = None
        self.lost_steal_count = 0
        self.clear_target()

    def next_cell(self, pos, action):
        dr, dc = self.MOVES[action]
        return (pos[0] + dr, pos[1] + dc)
    
    def near(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def is_corner_deadlock(self, pos, problem):
        blocked = {a for a, dr, dc in self.DIRECTIONS if (pos[0] + dr, pos[1] + dc) in problem.walls}
        return bool(blocked & {"North", "South"}) and bool(blocked & {"West", "East"})
    
    def push_options(self, box, boxes, problem, opponent):
        options = []
        for action, dr, dc in self.DIRECTIONS:
            push_pos = (box[0] - dr, box[1] - dc); box_next = (box[0] + dr, box[1] + dc)
            if push_pos in problem.walls or push_pos in boxes or push_pos == opponent: 
                continue
            if box_next in problem.walls or box_next in boxes or box_next == opponent: 
                continue
            options.append((action, push_pos, box_next))
        return options
    
    def select_target(self, agent_pos, boxes, problem, opponent, opponent_boxes, allow_opponent_boxes=False):
        self.target_from_opponent = False; occupied_goals = set(boxes) & set(problem.goals)
        free_goals = set(problem.goals) - occupied_goals; 
        best_box = best_goal = None
        best_priority = (float("inf"),) * 3; 
        blocked = set(boxes) | {opponent}

        for box in boxes:
            if box in occupied_goals or self.box_blacklist.get(box, -1) > self.turn: continue
            if box in opponent_boxes and not allow_opponent_boxes: continue
            best_agent_distance = min( (self.bfs(agent_pos, push_pos, problem.walls, blocked)[0] for _, push_pos, _ in self.push_options(box, boxes, problem, opponent)), default=float("inf") )
            if best_agent_distance == float("inf"): 
                continue
            home_distance = self.bfs(self.home_position, box, problem.walls, set())[0]

            for goal in free_goals:
                if (box, goal) in self.bad_pairs or box not in self.heuristic.maze_dist[goal]: 
                    continue
                goal_distance = self.heuristic.maze_dist[goal][box]; priority = (best_agent_distance + goal_distance, goal_distance, home_distance)
                if priority < best_priority:
                    best_priority, best_box, best_goal = priority, box, goal
        self.target_box, self.target_goal = best_box, best_goal

    def choose_goal_for_box(self, box, boxes, problem):
        occupied_goals = set(boxes) & set(problem.goals); best_goal, best_distance = None, float("inf")

        for goal in problem.goals:
            if goal in occupied_goals or (box, goal) in self.bad_pairs: 
                continue
            if box not in self.heuristic.maze_dist[goal]: 
                continue
            if self.heuristic.maze_dist[goal][box] < best_distance:
                best_distance, best_goal = self.heuristic.maze_dist[goal][box], goal
        if best_goal is None:
            self.clear_target()
        else:
            self.target_goal = best_goal

    def update_target_box(self, boxes):
        if self.target_box is None or self.previous_boxes is None:
            self.previous_boxes = set(boxes)
            return
        current_boxes = set(boxes)

        if self.target_box not in current_boxes:
            possible_positions = {(self.target_box[0] + dr, self.target_box[1] + dc) for _, dr, dc in self.DIRECTIONS}
            moved_positions = (current_boxes - self.previous_boxes) & possible_positions
            if len(moved_positions) == 1:
                self.target_box = next(iter(moved_positions))
            else:
                self.clear_target()
        self.previous_boxes = current_boxes

    def bfs(self, start, target, walls, blocked, deadline=None):
        if start == target: return (0, "Wait")
        queue = [(start, 0, None)]; explored = {start}

        while queue:
            if deadline is not None and time.perf_counter() >= deadline: break
            current, distance, first = queue.pop(0)
            for action, dr, dc in self.DIRECTIONS:
                next_pos = (current[0] + dr, current[1] + dc)
                if next_pos in explored or next_pos in walls or next_pos in blocked: continue
                first_action = action if first is None else first
                if next_pos == target: return (distance + 1, first_action)
                explored.add(next_pos)
                queue.append((next_pos, distance + 1, first_action))
        return (float("inf"), None)
    
    def plan_box_to_goal(self, agent_start, box, goal, other_boxes, problem, opponent, deadline, forbidden_first=None):
        if box == goal: return ("Wait", 0)
        if goal not in self.heuristic.maze_dist or box not in self.heuristic.maze_dist[goal]: 
            return None
        goal_map = self.heuristic.maze_dist[goal]; count = 0
        frontier = [(goal_map[box], count, 0, agent_start, box, None)]; 
        explored = set()

        while frontier:
            if time.perf_counter() >= deadline:
                self.plan_timeout = True
                return None
            h, _, cost, agent_pos, box_pos, first_action = heapq.heappop(frontier)
            current_state = (agent_pos, box_pos)
            if current_state in explored: 
                continue
            explored.add(current_state)
            if box_pos == goal: 
                return (first_action, cost)
            
            for action, dr, dc in self.DIRECTIONS:
                next_agent = (agent_pos[0] + dr, agent_pos[1] + dc); next_box = box_pos
                if next_agent in problem.walls or next_agent in other_boxes or next_agent == opponent: 
                    continue
                if cost == 0 and forbidden_first is not None and next_agent in forbidden_first: 
                    continue
                if next_agent == box_pos:
                    pushed_box = (box_pos[0] + dr, box_pos[1] + dc)
                    if pushed_box in problem.walls or pushed_box in other_boxes or pushed_box == opponent: 
                        continue
                    if pushed_box not in goal_map: continue
                    if pushed_box != goal and self.is_corner_deadlock(pushed_box, problem): 
                        continue
                    next_box = pushed_box
                next_state = (next_agent, next_box)
                if next_state in explored: continue
                next_cost = cost + 1
                count += 1
                heapq.heappush(frontier, ( goal_map[next_box], count, next_cost, next_agent, next_box, action if first_action is None else first_action ))
        return None
    
    def plan_ignoring_opponent(self, agent_pos, box, goal, other_boxes, problem, opponent, deadline):
        result = self.plan_box_to_goal(agent_pos, box, goal, other_boxes, problem, None, deadline)
        if result is not None and self.next_cell(agent_pos, result[0]) == opponent: 
            return ("Wait", result[1])
        return result
    
    def plan_stolen_box_to_goal(self, state, problem, box, goal, deadline):
        agent_start = state.agent_b_pos; 
        opponent = state.agent_a_pos
        other_boxes = set(state.boxes) - {box}; 
        result = self.plan_box_to_goal(agent_start, box, goal, other_boxes, problem, opponent, deadline)
        if result is None:
            result = self.plan_ignoring_opponent(agent_start, box, goal, other_boxes, problem, opponent, deadline)
        return None if result is None else result[0]
    
    def can_finish_steal(self, state, problem, goal, push_action, dr, dc, deadline):
        agent_pos = state.agent_b_pos; 
        opponent = state.agent_a_pos
        push_pos = (goal[0] - dr, goal[1] - dc); 
        box_out = (goal[0] + dr, goal[1] + dc)

        if push_pos in problem.walls or push_pos in state.boxes: 
            return None
        if box_out in problem.walls or box_out in state.boxes: 
            return None
        
        blocked = set(state.boxes) | {opponent}; 
        distance, first_action = self.bfs(agent_pos, push_pos, problem.walls, blocked, deadline)
        if first_action is None:
            blocked = set(state.boxes); 
            distance, first_action = self.bfs(agent_pos, push_pos, problem.walls, blocked, deadline)
            if first_action is None: return None
        temp = SimpleNamespace( agent_b_pos=goal, agent_a_pos=opponent, boxes=frozenset((set(state.boxes) - {goal}) | {box_out}) )
        if self.plan_stolen_box_to_goal(temp, problem, box_out, goal, deadline) is None: return None
        if push_pos == opponent or box_out == opponent:
            distance += 100
        return (distance, push_pos, push_action, first_action)
    
    def best_steal_candidate(self, state, problem, goal, deadline):
        best = None
        for push_action, dr, dc in self.DIRECTIONS:
            if time.perf_counter() >= deadline: break
            candidate = self.can_finish_steal(state, problem, goal, push_action, dr, dc, deadline)
            if candidate is not None and (best is None or candidate[0] < best[0]):
                best = candidate
        return best
    
    def start_push(self, push_action, goal, opponent):
        dr, dc = self.MOVES[push_action]; box_out = (goal[0] + dr, goal[1] + dc)
        if box_out == opponent: 
            return "Wait"
        self.steal_box = box_out
        return push_action
    
    def choose_steal_action(self, state, problem, deadline, preferred_goals=None):
        agent_pos = state.agent_b_pos; opponent = state.agent_a_pos
        owners = dict(state.box_owner)

        if self.steal_goal is not None:
            goal = self.steal_goal
            if goal in state.boxes and owners.get(goal) == "B":
                if self.lost_goal == goal:
                    self.lost_goal = None
                self.end_steal()
                return None
            
            if goal in state.boxes and owners.get(goal) == "A":
                best = self.best_steal_candidate(state, problem, goal, deadline)
                if best is None:
                    self.end_steal()
                    other_goals = { box for box in state.boxes if box in problem.goals and owners.get(box) == "A" and box != goal }
                    if other_goals: return self.choose_steal_action(state, problem, deadline, other_goals)
                    return None
                _, push_pos, push_action, first_action = best
                if agent_pos == push_pos: return self.start_push(push_action, goal, opponent)
                return first_action
            
            candidates = [self.target_box, self.steal_box] + [ (goal[0] + dr, goal[1] + dc) for _, dr, dc in self.DIRECTIONS ]
            stolen_box = next( (box for box in candidates if box in state.boxes and owners.get(box) == "B"), None )
            if stolen_box is not None:
                self.lost_steal_count = 0; self.steal_box = stolen_box
                self.target_box = stolen_box; self.target_goal = goal
                plan_action = self.plan_stolen_box_to_goal(state, problem, stolen_box, goal, deadline)
                return "Wait" if plan_action is None else plan_action
            self.lost_steal_count += 1
            if self.lost_steal_count >= 3:
                self.end_steal()
                return None
            return "Wait"
        best = None

        for box in state.boxes:
            if time.perf_counter() >= deadline: break
            if box not in problem.goals or owners.get(box) != "A": 
                continue
            if preferred_goals is not None and box not in preferred_goals: 
                continue
            if self.steal_blacklist.get(box, -1) > self.turn: 
                continue
            candidate = self.best_steal_candidate(state, problem, box, deadline)
            if candidate is not None and (best is None or candidate[0] < best[0][0]):
                best = (candidate, box)

        if best is None: return None
        (_, push_pos, push_action, first_action), goal = best
        self.steal_goal = goal; self.steal_box = None
        self.clear_target()
        if agent_pos == push_pos: return self.start_push(push_action, goal, opponent)
        return first_action
    
    def greedy_push_action(self, state, problem, deadline):
        agent_pos = state.agent_b_pos; opponent = state.agent_a_pos
        goal_map = self.heuristic.maze_dist[self.target_goal]; blocked = set(state.boxes) | {opponent}
        best = None

        for push_action, push_pos, box_next in self.push_options(self.target_box, state.boxes, problem, opponent):
            if box_next not in goal_map: 
                continue
            if agent_pos == push_pos:
                distance, first_action = 0, push_action
            else:
                distance, first_action = self.bfs(agent_pos, push_pos, problem.walls, blocked, deadline)
                if first_action is None: continue
            item = (goal_map[box_next], distance, first_action)
            if best is None or item[:2] < best[:2]:
                best = item
        return "Wait" if best is None else best[2]
    
    def choose_push_action(self, state, problem, deadline):
        agent_pos = state.agent_b_pos; opponent = state.agent_a_pos
        other_boxes = set(state.boxes) - {self.target_box}; plan_deadline = time.perf_counter() + (deadline - time.perf_counter()) * 0.7
        plan_args = (self.target_box, self.target_goal, other_boxes, problem); self.plan_timeout = False
        best = self.plan_box_to_goal(agent_pos, *plan_args, opponent, plan_deadline)

        if best is None:
            if self.plan_timeout: 
                return self.greedy_push_action(state, problem, deadline)
            best = self.plan_ignoring_opponent(agent_pos, *plan_args, opponent, plan_deadline)
            if best is not None: 
                return best[0]
            if self.plan_timeout: 
                return self.greedy_push_action(state, problem, deadline)
            self.bad_pairs.add((self.target_box, self.target_goal))
            self.bad_pairs_boxes = frozenset(state.boxes)
            return None
        
        action = best[0]
        if self.near(self.next_cell(agent_pos, action), opponent) <= 1:
            danger = {opponent} | {(opponent[0] + dr, opponent[1] + dc) for _, dr, dc in self.DIRECTIONS}
            safe = self.plan_box_to_goal(agent_pos, *plan_args, opponent, plan_deadline, danger)
            if safe is not None and safe[1] <= best[1] + 1:
                action = safe[0]
        return action
    
    def avoid_collision(self, action, state):
        agent_pos = state.agent_b_pos; opponent = state.agent_a_pos
        if action is None or action == "Wait":
            self.yield_count = 0
            return "Wait"
        next_pos = self.next_cell(agent_pos, action)
        if next_pos == opponent:
            return "Wait"
        if self.near(next_pos, opponent) <= 1 and self.yield_to_opponent and self.yield_count < self.max_yield:
            self.yield_count += 1
            return "Wait"
        self.yield_count = 0
        return action
    
    def choose_action(self, state, problem):
        agent_pos = state.agent_b_pos
        if self.last_action not in (None, "Wait") and self.last_pos == agent_pos:
            self.stuck_count += 1
        else:
            self.stuck_count = 0
        action = self.avoid_collision(self.decide_action(state, problem), state)
        self.wait_streak = self.wait_streak + 1 if action == "Wait" else 0
        self.last_pos = agent_pos; self.last_action = action
        return action
    
    def decide_action(self, state, problem):
        deadline = time.perf_counter() + self.time_limit
        if self.heuristic is None: return "Wait"
        if self.home_position is None:
            self.home_position = state.agent_b_pos
        owners = dict(state.box_owner); opponent = state.agent_a_pos
        self.turn += 1

        if self.steal_goal is not None and self.wait_streak >= self.max_wait:
            if self.steal_goal in state.boxes and owners.get(self.steal_goal) == "A":
                self.steal_blacklist[self.steal_goal] = self.turn + 15
                self.end_steal()
                self.wait_streak = 0

        if self.stuck_count >= self.max_stuck and self.steal_goal is None:
            if self.target_box is not None:
                self.box_blacklist[self.target_box] = self.turn + 15
                self.clear_target()
            self.stuck_count = 0
        self.update_target_box(state.boxes)

        if self.bad_pairs_boxes != frozenset(state.boxes):
            self.bad_pairs = set(); self.bad_pairs_boxes = None
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

        if self.lost_goal in state.boxes and owners.get(self.lost_goal) == "B":
            self.lost_goal = None
        if self.steal_goal is None and no_target:
            lost_goals = { goal for goal in self.my_completed_goals if goal in state.boxes and owners.get(goal) == "A" }
            first_choice = None if self.lost_goal is None else {self.lost_goal}
            for preferred in (first_choice, lost_goals):
                if not preferred: continue
                revenge_action = self.choose_steal_action(state, problem, deadline, preferred)
                if revenge_action is not None: return revenge_action

        if self.steal_goal is not None:
            steal_action = self.choose_steal_action(state, problem, deadline)
            if steal_action is not None: return steal_action
        no_target = self.target_box is None or self.target_goal is None

        if self.steal_goal is None and no_target:
            steal_action = self.choose_steal_action(state, problem, deadline)
            if steal_action is not None: return steal_action
        opponent_boxes = {box for box, owner in owners.items() if owner == "A"}

        if self.target_box in opponent_boxes and self.steal_goal is None and not self.target_from_opponent:
            self.clear_target()
        if self.target_box is not None and self.target_box not in state.boxes:
            self.clear_target()
        if self.target_box is not None and self.target_box in problem.goals and self.steal_goal is None:
            self.clear_target()
        if self.target_box is not None and self.target_goal is not None:
            if self.target_goal in state.boxes and self.target_box != self.target_goal:
                self.choose_goal_for_box(self.target_box, state.boxes, problem)
                
        for _ in range(3):
            if self.target_box is None or self.target_goal is None:
                self.select_target(state.agent_b_pos, state.boxes, problem, opponent, opponent_boxes)
            if self.target_box is None or self.target_goal is None:
                self.select_target(state.agent_b_pos, state.boxes, problem, opponent, opponent_boxes, True)
                if self.target_box is not None and self.target_goal is not None:
                    self.target_from_opponent = True
            if self.target_box is None or self.target_goal is None: return "Wait"
            push_action = self.choose_push_action(state, problem, deadline)
            if push_action is not None: return push_action
            self.clear_target()
        return "Wait"