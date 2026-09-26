import pygame

CELL_SIZE = 40

COLOR_WALL = (60, 60, 60)
COLOR_FLOOR = (240, 240, 240)
COLOR_GOAL = (220, 100, 100)
COLOR_BOX = (150, 100, 50)
COLOR_BOX_ON_GOAL = (80, 50, 20)
COLOR_AGENT = (50, 120, 220)


class BoardView:
    def __init__(self, problem):
        self.problem = problem
        all_cells = (problem.walls | problem.goals |
                     {problem.initial_state.agent_pos} |
                     set(problem.initial_state.box_positions))
        self.n_rows = max(r for r, c in all_cells) + 1
        self.n_cols = max(c for r, c in all_cells) + 1
        self.width = self.n_cols * CELL_SIZE
        self.height = self.n_rows * CELL_SIZE

    def draw(self, screen, state):
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                pos = (r, c)
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if pos in self.problem.walls:
                    pygame.draw.rect(screen, COLOR_WALL, rect)
                else:
                    pygame.draw.rect(screen, COLOR_FLOOR, rect)
                    if pos in self.problem.goals:
                        pygame.draw.rect(screen, COLOR_GOAL, rect, 3)

        for box_pos in state.box_positions:
            rect = pygame.Rect(box_pos[1] * CELL_SIZE, box_pos[0] * CELL_SIZE,
                                CELL_SIZE, CELL_SIZE)
            color = COLOR_BOX_ON_GOAL if box_pos in self.problem.goals else COLOR_BOX
            pygame.draw.rect(screen, color, rect.inflate(-8, -8))

        ar, ac = state.agent_pos
        center = (ac * CELL_SIZE + CELL_SIZE // 2, ar * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.circle(screen, COLOR_AGENT, center, CELL_SIZE // 2 - 6)