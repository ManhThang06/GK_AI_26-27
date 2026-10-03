"""
core/agents.py
Thuật toán GBFS (Greedy Best-First Search) cho Agent A và Agent B.
Mỗi agent tự lập kế hoạch trong giới hạn thời gian, tránh đối thủ,
tránh góc chết, ưu tiên đẩy thùng gần đích nhất.
"""
import time
import heapq
from collections import deque


import random

_DIRS = {
    "North": (-1, 0),
    "South": (1,  0),
    "West":  (0, -1),
    "East":  (0,  1),
}
ACTIONS = tuple(_DIRS.keys())


def _bfs_dist(start, target, walls, blocked):
    """BFS thực tế trên bản đồ, tránh tường và các ô bị chặn."""
    if start == target:
        return 0
    q = deque([(start, 0)])
    seen = {start}
    while q:
        pos, d = q.popleft()
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nxt = (pos[0]+dr, pos[1]+dc)
            if nxt in seen or nxt in walls or nxt in blocked:
                continue
            if nxt == target:
                return d + 1
            seen.add(nxt)
            q.append((nxt, d + 1))
    return float("inf")


def _is_corner_deadlock(pos, walls):
    """Trả về True nếu ô này là góc chết (bị tường ở 2 hướng kề nhau)."""
    r, c = pos
    up    = (r-1, c) in walls
    down  = (r+1, c) in walls
    left  = (r, c-1) in walls
    right = (r, c+1) in walls
    return (up and left) or (up and right) or (down and left) or (down and right)


def _push_priority(agent_pos, boxes, problem, opponent, heuristic):
    """
    Tính (goal_dist, agent_dist) nhỏ nhất trong số các nước đẩy khả thi.
    Dùng làm tie-breaker khi h(n) bằng nhau.
    """
    occupied = set(boxes) & set(problem.goals)
    free_goals = set(problem.goals) - occupied
    if not free_goals:
        return (0, 0)

    best = (float("inf"), float("inf"))
    blocked = set(boxes) | {opponent}

    for box in boxes:
        if box in occupied:
            continue
        br, bc = box
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            push_from = (br - dr, bc - dc)   # ô agent phải đứng để đẩy
            box_dest  = (br + dr, bc + dc)   # ô thùng sẽ đến

            if push_from in problem.walls or push_from in boxes:
                continue
            if box_dest in problem.walls or box_dest in boxes:
                continue

            # khoảng cách thùng đến đích gần nhất theo heuristic
            g_dist = min(
                heuristic.maze_dist[g].get(box_dest, float("inf"))
                for g in free_goals
            )
            if g_dist == float("inf"):
                continue

            a_dist = _bfs_dist(agent_pos, push_from, problem.walls, blocked)
            if a_dist == float("inf"):
                continue

            best = min(best, (g_dist, a_dist))
    return best


class _GBFSAgent:
    """Base GBFS agent. Subclass đặt agent_key = 'A' hoặc 'B'."""
    agent_key: str = "A"

    def __init__(self, heuristic, time_limit: float = 0.9):
        self.heuristic  = heuristic
        self.time_limit = time_limit

    def choose_action(self, state, problem) -> str:
        if self.heuristic is None:
            return "Wait"

        # Lấy thông tin theo agent_key
        if self.agent_key == "A":
            my_pos   = state.agent_a_pos
            opponent = state.agent_b_pos
        else:
            my_pos   = state.agent_b_pos
            opponent = state.agent_a_pos

        deadline = time.perf_counter() + self.time_limit
        boxes    = state.boxes

        start_node = (my_pos, boxes)
        h0    = self.heuristic.evaluate(boxes)
        pp0   = _push_priority(my_pos, boxes, problem, opponent, self.heuristic)

        frontier   = []
        heapq.heappush(frontier, (h0, pp0, 0, my_pos, boxes))
        frontier_h = {start_node: h0}   # dict giống M4 gốc
        explored   = set()
        parent     = {start_node: None}
        parent_act = {start_node: None}
        counter    = 1

        best_node = start_node
        best_h    = h0
        best_pp   = pp0

        while frontier:
            if time.perf_counter() >= deadline:
                break

            h, pp, _, pos, bxs = heapq.heappop(frontier)
            node = (pos, bxs)
            if node in explored:
                continue
            frontier_h.pop(node, None)
            explored.add(node)

            # Cập nhật trạng thái tốt nhất
            if h < best_h or (h == best_h and pp < best_pp):
                best_h    = h
                best_pp   = pp
                best_node = node

            # Đã giải xong
            if all(b in problem.goals for b in bxs):
                best_node = node
                break

            for action in ACTIONS:
                if time.perf_counter() >= deadline:
                    break

                dr, dc   = _DIRS[action]
                next_pos = (pos[0] + dr, pos[1] + dc)

                if next_pos == opponent or next_pos in problem.walls:
                    continue

                next_bxs = bxs
                if next_pos in bxs:
                    box_dest = (next_pos[0] + dr, next_pos[1] + dc)
                    if (box_dest in problem.walls
                            or box_dest in bxs
                            or box_dest == opponent):
                        continue
                    # Tránh đẩy thùng vào góc chết (nếu không phải đích)
                    if box_dest not in problem.goals and _is_corner_deadlock(box_dest, problem.walls):
                        continue
                    new_bxs  = set(bxs)
                    new_bxs.remove(next_pos)
                    new_bxs.add(box_dest)
                    next_bxs = frozenset(new_bxs)

                next_node = (next_pos, next_bxs)
                if next_node in explored or next_node in frontier_h:
                    continue

                next_h  = self.heuristic.evaluate(next_bxs)
                next_pp = _push_priority(next_pos, next_bxs, problem, opponent, self.heuristic)
                parent[next_node]     = node
                parent_act[next_node] = action
                frontier_h[next_node] = next_h
                counter += 1
                heapq.heappush(frontier, (next_h, next_pp, counter, next_pos, next_bxs))

        # Truy ngược lại hành động đầu tiên
        if best_node == start_node:
            # BỊ KẸT: Không tìm thấy đường nào tốt hơn, buộc phải đi lang thang (random walk)
            # Tìm tất cả các hướng có thể đi được (không vướng tường, không vướng đối thủ)
            valid_moves = []
            for action in ACTIONS:
                dr, dc = _DIRS[action]
                nxt = (my_pos[0] + dr, my_pos[1] + dc)
                if nxt not in problem.walls and nxt != opponent:
                    valid_moves.append(action)
            
            if valid_moves:
                return random.choice(valid_moves)
            else:
                return "North" # Cùng đường (kẹt 4 phía), trả về đại 1 hướng
            
        node = best_node
        while parent[node] != start_node:
            node = parent[node]
        return parent_act[node]


class AgentA(_GBFSAgent):
    """Agent A - điều khiển agent_a_pos."""
    agent_key = "A"


class AgentB(_GBFSAgent):
    """Agent B - điều khiển agent_b_pos."""
    agent_key = "B"
