import pygame

CELL_SIZE = 44
COLOR_WALL = (196, 164, 132)
COLOR_WALL_EDGE = (150, 115, 85)
COLOR_FLOOR = (235, 214, 182)
COLOR_GOAL_MARK = (255, 140, 0)
COLOR_DOOR = (219, 90, 140)
COLOR_DOOR_EDGE = (150, 50, 90)
COLOR_DOOR_OPEN = (50, 205, 50)
COLOR_DOOR_OPEN_EDGE = (34, 139, 34)
COLOR_DORA_BODY = (60, 140, 220)
COLOR_DORA_BELLY = (245, 245, 245)
COLOR_DORA_RED = (220, 50, 50)
COLOR_DORA_BLACK = (20, 20, 20)

def make_wall_tile(size):
    tile = pygame.Surface((size, size))
    tile.fill(COLOR_WALL_EDGE)
    gap = 3
    half = size // 2
    brick = half - gap - gap // 2
    for bx, by in ((gap, gap), (half + gap // 2, gap),
                   (gap, half + gap // 2), (half + gap // 2, half + gap // 2)):
        pygame.draw.rect(tile, COLOR_WALL, (bx, by, brick, brick), border_radius=3)
    return tile

def draw_door(screen, rect, is_open):
    body = COLOR_DOOR_OPEN if is_open else COLOR_DOOR
    edge = COLOR_DOOR_OPEN_EDGE if is_open else COLOR_DOOR_EDGE
    pygame.draw.rect(screen, body, rect, border_radius=6)
    pygame.draw.rect(screen, edge, rect, 3, border_radius=6)
    if not is_open:
        mx = rect.centerx
        pygame.draw.line(screen, edge, (mx, rect.top + 6), (mx, rect.bottom - 6), 2)
        pygame.draw.circle(screen, edge, (mx - 6, rect.centery), 2)
        pygame.draw.circle(screen, edge, (mx + 6, rect.centery), 2)

def draw_doraemon(screen, center, size):
    cx, cy = center
    r = size // 2 - 4
    pygame.draw.circle(screen, COLOR_DORA_BODY, (cx, cy), r)
    ear_y = cy - r + 6
    pygame.draw.circle(screen, COLOR_DORA_BODY, (cx - r // 2, ear_y), r // 3)
    pygame.draw.circle(screen, COLOR_DORA_BODY, (cx + r // 2, ear_y), r // 3)
    belly = pygame.Rect(0, 0, int(r * 1.3), int(r * 1.1))
    belly.center = (cx, cy + r // 4)
    pygame.draw.ellipse(screen, COLOR_DORA_BELLY, belly)
    pygame.draw.circle(screen, COLOR_DORA_RED, (cx, cy - r // 4), r // 6)
    eo = r // 3
    ey = cy - r // 2
    pygame.draw.circle(screen, COLOR_DORA_BLACK, (cx - eo, ey), 3)
    pygame.draw.circle(screen, COLOR_DORA_BLACK, (cx + eo, ey), 3)

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
        self.wall_tile = make_wall_tile(CELL_SIZE)

    def draw(self, screen, state):
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                pos = (r, c)
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if pos in self.problem.walls:
                    screen.blit(self.wall_tile, rect)
                else:
                    pygame.draw.rect(screen, COLOR_FLOOR, rect)
                    if pos in self.problem.goals:
                        pygame.draw.rect(screen, COLOR_GOAL_MARK, rect, 3)
        for box_pos in state.box_positions:
            rect = pygame.Rect(box_pos[1] * CELL_SIZE, box_pos[0] * CELL_SIZE,
                                CELL_SIZE, CELL_SIZE).inflate(-8, -8)
            draw_door(screen, rect, box_pos in self.problem.goals)
        ar, ac = state.agent_pos
        center = (ac * CELL_SIZE + CELL_SIZE // 2, ar * CELL_SIZE + CELL_SIZE // 2)
        draw_doraemon(screen, center, CELL_SIZE)