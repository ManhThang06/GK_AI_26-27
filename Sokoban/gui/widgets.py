"""
gui/widgets.py
Các thành phần UI dùng chung: Button, nền cỏ, vẽ agent Doraemon & Agent B.
"""
import pygame

# ── Màu sắc ──────────────────────────────────────────────────────────────────
C_BG             = (210, 185, 155)
C_OUTLINE        = (30,  30,  30)
C_BTN            = (222, 115, 38)
C_BTN_EDGE       = (150, 80,  30)
C_BTN_HOVER      = (240, 140, 60)
C_BTN_DOWN       = (170, 85,  25)
C_BTN_SEL        = (105, 55,  40)
C_BTN_SEL_EDGE   = (70,  35,  25)
C_BTN_TEXT       = (30,  30,  30)
C_BTN_TEXT_SEL   = (255, 255, 255)
EDGE_H           = 5

C_WALL           = (196, 164, 132)
C_WALL_EDGE      = (150, 115, 85)
C_FLOOR          = (235, 214, 182)
C_GOAL_FLOOR     = (233, 150, 122)
C_GOAL_MARK      = (255, 140, 0)
C_GOAL_MARK_DONE = (34,  139, 34)

C_BOX_FREE       = (170, 120, 60)
C_BOX_A          = (70,  130, 230)
C_BOX_B          = (225, 85,  140)
C_BOX_EDGE       = (120, 70,  30)

C_DORA_BODY      = (60,  140, 220)
C_DORA_BELLY     = (245, 245, 245)
C_DORA_RED       = (220, 50,  50)
C_DORA_BLACK     = (20,  20,  20)
C_AGENT_B        = (210, 55,  115)

C_INFO_BG        = (25,  25,  25)
C_INFO_TEXT      = (255, 255, 255)
C_STATUS         = (250, 210, 60)
C_SHADOW         = (255, 255, 255)
C_TEXT           = (40,  40,  40)
C_NOTE           = (180, 40,  40)
C_INPUT_BG       = (255, 255, 220)
C_INPUT_BORDER   = (100, 80,  40)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_bg(width: int, height: int) -> pygame.Surface:
    surf = pygame.Surface((width, height))
    surf.fill(C_BG)
    return surf


def make_wall_tile(size: int) -> pygame.Surface:
    tile = pygame.Surface((size, size))
    tile.fill(C_WALL_EDGE)
    gap  = 3
    half = size // 2
    brick = half - gap - gap // 2
    for bx, by in ((gap, gap), (half + gap // 2, gap),
                   (gap, half + gap // 2), (half + gap // 2, half + gap // 2)):
        pygame.draw.rect(tile, C_WALL, (bx, by, brick, brick), border_radius=3)
    return tile


def draw_box(screen: pygame.Surface, rect: pygame.Rect,
             on_goal: bool, color: tuple):
    """Vẽ thùng với màu theo chủ sở hữu; viền xanh lá nếu nằm trên đích."""
    pygame.draw.rect(screen, color, rect, border_radius=6)
    edge = C_GOAL_MARK_DONE if on_goal else C_BOX_EDGE
    pygame.draw.rect(screen, edge, rect, 3, border_radius=6)
    if not on_goal:
        mx = rect.centerx
        pygame.draw.line(screen, edge, (mx, rect.top + 6), (mx, rect.bottom - 6), 2)
        pygame.draw.circle(screen, edge, (mx - 6, rect.centery), 2)
        pygame.draw.circle(screen, edge, (mx + 6, rect.centery), 2)


def draw_doraemon(screen: pygame.Surface, center: tuple, size: int):
    cx, cy = center
    r = size // 2 - 4
    pygame.draw.circle(screen, C_DORA_BODY, (cx, cy), r)
    ear_y = cy - r + 6
    pygame.draw.circle(screen, C_DORA_BODY, (cx - r // 2, ear_y), r // 3)
    pygame.draw.circle(screen, C_DORA_BODY, (cx + r // 2, ear_y), r // 3)
    belly = pygame.Rect(0, 0, int(r * 1.3), int(r * 1.1))
    belly.center = (cx, cy + r // 4)
    pygame.draw.ellipse(screen, C_DORA_BELLY, belly)
    pygame.draw.circle(screen, C_DORA_RED, (cx, cy - r // 4), r // 6)
    eo, ey = r // 3, cy - r // 2
    pygame.draw.circle(screen, C_DORA_BLACK, (cx - eo, ey), 3)
    pygame.draw.circle(screen, C_DORA_BLACK, (cx + eo, ey), 3)


def draw_agent_b(screen: pygame.Surface, center: tuple, size: int):
    cx, cy = center
    r = size // 2 - 4
    pygame.draw.circle(screen, C_AGENT_B, (cx, cy), r)
    pygame.draw.circle(screen, C_AGENT_B, (cx - r // 2, cy - r + 3), r // 3)
    pygame.draw.circle(screen, C_AGENT_B, (cx + r // 2, cy - r + 3), r // 3)
    pygame.draw.circle(screen, (255, 255, 255), (cx, cy + r // 4), r // 2)
    pygame.draw.circle(screen, (255, 255, 255), (cx - r // 4, cy - r // 4), r // 4)
    pygame.draw.circle(screen, (255, 255, 255), (cx + r // 4, cy - r // 4), r // 4)
    pygame.draw.circle(screen, (0, 0, 0), (cx - r // 5, cy - r // 4), max(2, r // 10))
    pygame.draw.circle(screen, (0, 0, 0), (cx + r // 5, cy - r // 4), max(2, r // 10))
    pygame.draw.circle(screen, (255, 80, 100), (cx, cy), max(2, r // 8))


def shadow_text(screen, font, text: str, pos: tuple):
    screen.blit(font.render(text, True, C_SHADOW), (pos[0] + 2, pos[1] + 2))
    screen.blit(font.render(text, True, C_TEXT), pos)


# ── Button ───────────────────────────────────────────────────────────────────

class Button:
    def __init__(self, rect, text: str, font):
        self.rect     = pygame.Rect(rect)
        self.text     = text
        self.font     = font
        self.selected = False
        self.pressed  = False

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            clicked = self.pressed and self.rect.collidepoint(event.pos)
            self.pressed = False
            return clicked
        return False

    def draw(self, screen):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        txt_c = C_BTN_TEXT
        if self.pressed:
            face_c, edge_c = C_BTN_DOWN, C_BTN_DOWN
        elif self.selected:
            face_c, edge_c = C_BTN_SEL, C_BTN_SEL_EDGE
            txt_c = C_BTN_TEXT_SEL
        elif hover:
            face_c, edge_c = C_BTN_HOVER, C_BTN_EDGE
        else:
            face_c, edge_c = C_BTN, C_BTN_EDGE

        offset = EDGE_H - 2 if self.pressed else 0
        face = self.rect.move(0, offset)
        edge = self.rect.move(0, EDGE_H)
        pygame.draw.rect(screen, edge_c, edge, border_radius=8)
        pygame.draw.rect(screen, face_c, face, border_radius=8)
        pygame.draw.rect(screen, C_OUTLINE, face, 3, border_radius=8)
        ts = self.font.render(self.text, True, txt_c)
        screen.blit(ts, ts.get_rect(center=face.center))
