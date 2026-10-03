"""
core/sokoban.py
Trạng thái, bài toán và các thuật toán tìm kiếm cho chế độ 1 Agent.
  - SokobanState  : trạng thái (agent_pos, boxes)
  - SokobanProblem: luật di chuyển và hàm goal_test
  - ucs()         : Uniform Cost Search
  - astar()       : A* Search
"""
import heapq
from core.heuristic import Heuristic


# ── State ────────────────────────────────────────────────────────────────────

class SokobanState:
    __slots__ = ("agent_pos", "boxes")

    def __init__(self, agent_pos: tuple, boxes):
        self.agent_pos = agent_pos
        self.boxes = frozenset(boxes)

    def __eq__(self, other):
        return self.agent_pos == other.agent_pos and self.boxes == other.boxes

    def __hash__(self):
        return hash((self.agent_pos, self.boxes))

    def __lt__(self, other):   # cho heapq
        return False


# ── Problem ──────────────────────────────────────────────────────────────────

DIRS = {
    "North": (-1, 0),
    "South": (1,  0),
    "West":  (0, -1),
    "East":  (0,  1),
}


class SokobanProblem:
    def __init__(self, map_parser):
        self.walls = map_parser.walls
        self.goals = map_parser.goals
        self.initial_state = SokobanState(
            map_parser.initial_agent,
            map_parser.initial_boxes,
        )

    def is_goal(self, state: SokobanState) -> bool:
        return state.boxes == self.goals

    def result(self, state: SokobanState, action: str) -> SokobanState:
        """Áp dụng action, trả về trạng thái mới (hoặc nguyên bản nếu không hợp lệ)."""
        dr, dc = DIRS[action]
        r, c = state.agent_pos
        nr, nc = r + dr, c + dc

        if (nr, nc) in self.walls:
            return state
        if (nr, nc) in state.boxes:
            nnr, nnc = nr + dr, nc + dc
            if (nnr, nnc) in self.walls or (nnr, nnc) in state.boxes:
                return state
            new_boxes = set(state.boxes)
            new_boxes.remove((nr, nc))
            new_boxes.add((nnr, nnc))
            return SokobanState((nr, nc), new_boxes)
        return SokobanState((nr, nc), state.boxes)

    def successors(self, state: SokobanState):
        """Sinh các trạng thái kế tiếp hợp lệ: [(action, new_state, cost)]"""
        results = []
        r, c = state.agent_pos
        for action, (dr, dc) in DIRS.items():
            nr, nc = r + dr, c + dc
            if (nr, nc) in self.walls:
                continue
            if (nr, nc) in state.boxes:
                nnr, nnc = nr + dr, nc + dc
                if (nnr, nnc) in self.walls or (nnr, nnc) in state.boxes:
                    continue
                new_boxes = set(state.boxes)
                new_boxes.remove((nr, nc))
                new_boxes.add((nnr, nnc))
                results.append((action, SokobanState((nr, nc), new_boxes), 1))
            else:
                results.append((action, SokobanState((nr, nc), state.boxes), 1))
        return results


# ── UCS ──────────────────────────────────────────────────────────────────────

def ucs(problem: SokobanProblem):
    """
    Uniform Cost Search.
    Trả về (path, cost, nodes_expanded) hoặc (None, inf, nodes_expanded).
    """
    start = problem.initial_state
    frontier = [(0, 0, start, [])]   # (g, tie, state, path)
    visited = {start: 0}
    expanded = 0
    counter = 1

    while frontier:
        g, _, state, path = heapq.heappop(frontier)
        if g > visited.get(state, float("inf")):
            continue
        if problem.is_goal(state):
            return path, g, expanded
        expanded += 1
        for action, next_state, cost in problem.successors(state):
            new_g = g + cost
            if new_g < visited.get(next_state, float("inf")):
                visited[next_state] = new_g
                heapq.heappush(frontier, (new_g, counter, next_state, path + [action]))
                counter += 1

    return None, float("inf"), expanded


# ── A* ───────────────────────────────────────────────────────────────────────

def astar(problem: SokobanProblem, heuristic: Heuristic):
    """
    A* Search với heuristic BFS.
    Trả về (path, cost, nodes_expanded) hoặc (None, inf, nodes_expanded).
    """
    start = problem.initial_state
    h0 = heuristic.evaluate(start.boxes)
    frontier = [(h0, 0, 0, start, [])]   # (f, g, tie, state, path)
    visited = {start: 0}
    expanded = 0
    counter = 1

    while frontier:
        f, g, _, state, path = heapq.heappop(frontier)
        if g > visited.get(state, float("inf")):
            continue
        if problem.is_goal(state):
            return path, g, expanded
        expanded += 1
        for action, next_state, cost in problem.successors(state):
            new_g = g + cost
            if new_g < visited.get(next_state, float("inf")):
                h = heuristic.evaluate(next_state.boxes)
                if h == float("inf"):
                    continue   # deadlock, bỏ qua
                visited[next_state] = new_g
                heapq.heappush(frontier, (new_g + h, new_g, counter, next_state, path + [action]))
                counter += 1

    return None, float("inf"), expanded
