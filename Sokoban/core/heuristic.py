from collections import deque

class Heuristic:
    DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self, board_matrix: list[list[str]], goals: list[tuple]):
        self.goals = goals
        self.maze_dist: dict[tuple, dict[tuple, int]] = {}
        for goal in goals:
            self.maze_dist[goal] = self._bfs(board_matrix, goal)

    def _bfs(self, board: list[list[str]], start: tuple) -> dict[tuple, int]:
        dist = {start: 0}
        q = deque([start])
        rows, cols = len(board), len(board[0]) if board else 0
        while q:
            r, c = q.popleft()
            for dr, dc in self.DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in dist:
                    if board[nr][nc] != "%":
                        dist[(nr, nc)] = dist[(r, c)] + 1
                        q.append((nr, nc))
        return dist

    def evaluate(self, boxes: frozenset) -> float:
        total = 0
        for box in boxes:
            min_d = float("inf")
            for goal in self.goals:
                d = self.maze_dist[goal].get(box, float("inf"))
                if d < min_d:
                    min_d = d
            if min_d == float("inf"):
                return float("inf")
            total += min_d
        return total
