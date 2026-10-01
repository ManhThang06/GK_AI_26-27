import pygame

CELL_SIZE = 40
WALL = (60, 60, 60)
FLOOR = (240, 240, 240)
GOAL = (200, 70, 70)
BOX_FREE = (170, 120, 60)
BOX_A = (70, 130, 230)
BOX_B = (225, 85, 140)
AGENT_A = (45, 95, 210)
AGENT_B = (210, 55, 115)

class TwoAgentBoardView:
    def __init__(self, problem, top_offset=120):
        self.problem = problem
        self.top_offset = top_offset

        cells = (set(problem.walls) | set(problem.goals) |
                 set(problem.initial_state.boxes) |
                 {problem.initial_state.agent_a_pos,
                  problem.initial_state.agent_b_pos})

        self.n_rows = max(row for row, col in cells) + 1
        self.n_cols = max(col for row, col in cells) + 1
        self.width = self.n_cols * CELL_SIZE
        self.height = self.n_rows * CELL_SIZE

    def draw(self, screen, state):
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                pos = (row, col)
                rect = pygame.Rect(col * CELL_SIZE, self.top_offset + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if pos in self.problem.walls:
                    pygame.draw.rect(screen, WALL, rect)
                else:
                    pygame.draw.rect(screen, FLOOR, rect)
                    if pos in self.problem.goals:
                        pygame.draw.rect(screen, GOAL, rect, 3)

        owners = dict(state.box_owner)
        for row, col in state.boxes:
            pos = (row, col)
            owner = owners.get(pos)
            color = BOX_FREE
            if owner == "A":
                color = BOX_A
            elif owner == "B":
                color = BOX_B
            rect = pygame.Rect(col * CELL_SIZE, self.top_offset + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect.inflate(-8, -8))
        self._agent(screen, state.agent_a_pos, AGENT_A)
        self._agent(screen, state.agent_b_pos, AGENT_B)

    def _agent(self, screen, pos, color):
        row, col = pos
        center = (col * CELL_SIZE + CELL_SIZE // 2, self.top_offset + row * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.circle(screen, color, center, CELL_SIZE // 2 - 6)