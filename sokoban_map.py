class MapParser:
    def __init__(self, filepath):
        self.walls = set()
        self.goals = set()
        self.initial_agent = None
        self.initial_boxes = set()
        self._parse(filepath)
    def _parse(self, filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()
        for y, line in enumerate(lines):
            # Cắt ký tự xuống dòng để tránh lỗi
            for x, char in enumerate(line.strip('\n')):
                pos = (x, y)
                if char == '%':
                    self.walls.add(pos)
                elif char == 'D':
                    self.goals.add(pos)
                elif char == 'A':
                    self.initial_agent = pos
                elif char == 'B':
                    self.initial_boxes.add(pos)
                elif char == 'C':
                    # C là box đang nằm sẵn trên đích (dark brown boxes)
                    self.initial_boxes.add(pos)
                    self.goals.add(pos)