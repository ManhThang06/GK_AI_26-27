class MapParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.walls: set = set()
        self.goals: set = set()
        self.initial_agent: tuple | None = None
        self.initial_boxes: set = set()
        self._lines: list[str] = []
        self._parse()

    def _parse(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            self._lines = [line.rstrip("\n\r") for line in f.readlines()]
        for row, line in enumerate(self._lines):
            for col, ch in enumerate(line):
                pos = (row, col)
                if   ch == "%": self.walls.add(pos)
                elif ch == "D": self.goals.add(pos)
                elif ch == "A": self.initial_agent = pos
                elif ch == "B": self.initial_boxes.add(pos)
                elif ch == "C":
                    self.initial_boxes.add(pos)
                    self.goals.add(pos)

    @property
    def board_matrix(self) -> list[list[str]]:
        if not self._lines:
            return []
        max_cols = max(len(l) for l in self._lines)
        matrix = []
        for line in self._lines:
            row = list(line.ljust(max_cols))
            matrix.append(row)
        return matrix

    def two_agent_start(self) -> tuple[tuple, tuple]:
        if self.initial_agent is None:
            raise ValueError("Not found 'A'.")
        pos_a = self.initial_agent
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            pos_b = (pos_a[0] + dr, pos_a[1] + dc)
            if pos_b not in self.walls and pos_b not in self.initial_boxes:
                return pos_a, pos_b
        raise ValueError("Not found a valid position for Agent B.")
