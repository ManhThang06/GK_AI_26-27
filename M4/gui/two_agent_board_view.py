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
GOAL = (200, 70, 70)
BOX_FREE = (170, 120, 60)
BOX_A = (70, 130, 230)
BOX_B = (225, 85, 140)
AGENT_A = (45, 95, 210)
AGENT_B = (210, 55, 115)

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

def draw_door(screen, rect, is_open, color):
    body = color
    edge = COLOR_DOOR_EDGE
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

def draw_agent_b(screen, center, size):
    cx, cy = center
    r = size // 2 - 4
    pygame.draw.circle(screen, AGENT_B, (cx, cy), r)
    pygame.draw.circle(screen, AGENT_B, (cx - r // 2, cy - r + 3), r // 3)
    pygame.draw.circle(screen, AGENT_B, (cx + r // 2, cy - r + 3), r // 3)
    pygame.draw.circle(screen, (255, 255, 255), (cx, cy + r // 4), r // 2)
    pygame.draw.circle(screen, (255, 255, 255), (cx - r // 4, cy - r // 4), r // 4)
    pygame.draw.circle(screen, (255, 255, 255), (cx + r // 4, cy - r // 4), r // 4)
    pygame.draw.circle(screen, (0, 0, 0), (cx - r // 5, cy - r // 4), max(2, r // 10))
    pygame.draw.circle(screen, (0, 0, 0), (cx + r // 5, cy - r // 4), max(2, r // 10))
    pygame.draw.circle(screen, (255, 80, 100), (cx, cy), max(2, r // 8))

class TwoAgentBoardView:
    def __init__(self, problem):
        self.problem = problem

        cells = (set(problem.walls) | set(problem.goals) |
                 set(problem.initial_state.boxes) |
                 {problem.initial_state.agent_a_pos,
                  problem.initial_state.agent_b_pos})

        self.wall_tile = make_wall_tile(CELL_SIZE)
        self.n_rows = max(row for row, col in cells) + 1
        self.n_cols = max(col for row, col in cells) + 1
        self.width = self.n_cols * CELL_SIZE
        self.height = self.n_rows * CELL_SIZE

    def draw(self, screen, state):
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                pos = (row, col)
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if pos in self.problem.walls:
                    screen.blit(self.wall_tile, rect)
                else:
                    pygame.draw.rect(screen, COLOR_FLOOR, rect)
                    if pos in self.problem.goals:
                        goal_color = COLOR_DOOR_OPEN_EDGE if pos in state.boxes else COLOR_GOAL_MARK
                        pygame.draw.rect(
                            screen,
                            goal_color,
                            rect,
                            3
                        )

        owners = dict(state.box_owner)
        for row, col in state.boxes:
            pos = (row, col)
            owner = owners.get(pos)
            color = BOX_FREE
            if owner == "A":
                color = BOX_A
            elif owner == "B":
                color = BOX_B
            rect = pygame.Rect(col * CELL_SIZE + 4, row * CELL_SIZE + 4, CELL_SIZE - 8, CELL_SIZE - 8)
            draw_door(screen, rect, pos in self.problem.goals, color)
        ar, ac = state.agent_a_pos
        center_a = (ac * CELL_SIZE + CELL_SIZE // 2, ar * CELL_SIZE + CELL_SIZE // 2)
        draw_doraemon(screen, center_a, CELL_SIZE)
        br, bc = state.agent_b_pos
        center_b = (bc * CELL_SIZE + CELL_SIZE // 2, br * CELL_SIZE + CELL_SIZE // 2)
        draw_agent_b(screen, center_b, CELL_SIZE)