"""
gui/main_menu.py
Màn hình chính: Chọn chế độ → Chọn thuật toán / Nhập steps → Chọn map.
Trả về (mode, data) khi hoàn tất:
  mode="1 Agent"  →  data=(algorithm: str, map_path: str)
  mode="2 Agents" →  data=(n_steps: int, map_path: str)
"""
import os
import pygame
from gui.widgets import Button, make_bg, C_TEXT, C_SHADOW, C_NOTE, C_INPUT_BG, C_INPUT_BORDER

WIDTH, HEIGHT = 480, 520

MAP1_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "map1Agent")
MAP2_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "map2Agent")

_S_MODE  = "mode"
_S_ALGO  = "algo"
_S_STEPS = "steps"
_S_MAP1  = "map1"
_S_MAP2  = "map2"


def _get_maps(folder: str) -> list[str]:
    if not os.path.exists(folder):
        return []
    return sorted(f for f in os.listdir(folder) if f.endswith(".txt"))


class MainMenu:
    def __init__(self, screen: pygame.Surface):
        self.screen  = screen
        self.bg      = make_bg(WIDTH, HEIGHT)
        self.state   = _S_MODE
        self.algo    = "UCS"
        self.steps_input = ""
        self.note    = ""
        self.running = True
        self.result  = None
        self.map_buttons: list[Button] = []

        f_title = pygame.font.SysFont("arial", 44, bold=True)
        f_sub   = pygame.font.SysFont("arial", 20)
        f_btn   = pygame.font.SysFont("arial", 22, bold=True)
        f_sm    = pygame.font.SysFont("arial", 18, bold=True)
        self._f_title = f_title
        self._f_sub   = f_sub
        self._f_btn   = f_btn
        self._f_sm    = f_sm
        self._f_inp   = pygame.font.SysFont("arial", 26, bold=True)

        cx = WIDTH // 2 - 100
        # Mode
        self.b_one  = Button((cx, 165, 200, 48), "1 Agent",  f_btn)
        self.b_two  = Button((cx, 235, 200, 48), "2 Agents", f_btn)
        self.b_exit = Button((cx, 305, 200, 48), "Exit",     f_btn)
        # Algo
        self.b_ucs   = Button((WIDTH//2 - 105, 170, 100, 48), "UCS", f_btn)
        self.b_astar = Button((WIDTH//2 + 5,   170, 100, 48), "A*",  f_btn)
        self.b_next  = Button((cx, 255, 200, 48), "Next →",  f_btn)
        self.b_back  = Button((cx, 320, 200, 48), "← Back",  f_btn)
        self.b_ucs.selected = True
        # Steps
        self.input_rect   = pygame.Rect(WIDTH//2 - 80, 200, 160, 44)
        self.b_steps_next = Button((cx, 275, 200, 48), "Next →", f_btn)
        self.b_steps_back = Button((cx, 340, 200, 48), "← Back", f_btn)
        # Map
        self.b_map_back = Button((cx, 450, 200, 44), "← Back", f_sm)

    # ── Button sets ──────────────────────────────────────────────────────────

    def _active_btns(self) -> list[Button]:
        if self.state == _S_MODE:
            return [self.b_one, self.b_two, self.b_exit]
        if self.state == _S_ALGO:
            return [self.b_ucs, self.b_astar, self.b_next, self.b_back]
        if self.state == _S_STEPS:
            return [self.b_steps_next, self.b_steps_back]
        return self.map_buttons + [self.b_map_back]

    # ── Click handler ────────────────────────────────────────────────────────

    def _on_click(self, btn: Button):
        if btn is self.b_exit:
            self.running = False
        elif btn is self.b_one:
            self.state = _S_ALGO;  self.note = ""
        elif btn is self.b_two:
            self.state = _S_STEPS; self.steps_input = ""; self.note = ""
        elif btn in (self.b_ucs, self.b_astar):
            self.algo = btn.text
            self.b_ucs.selected   = (btn is self.b_ucs)
            self.b_astar.selected = (btn is self.b_astar)
        elif btn is self.b_next:
            self._build_maps(MAP1_DIR); self.state = _S_MAP1
        elif btn is self.b_back:
            self.state = _S_MODE
        elif btn is self.b_steps_next:
            if self.steps_input.isdigit() and int(self.steps_input) >= 1:
                self._build_maps(MAP2_DIR); self.state = _S_MAP2; self.note = ""
            else:
                self.note = "Please enter steps >= 1"
        elif btn is self.b_steps_back:
            self.state = _S_MODE
        elif btn is self.b_map_back:
            self.state = _S_ALGO if self.state == _S_MAP1 else _S_STEPS
        else:
            # map button — tìm index trong map_buttons để lấy filename gốc
            folder = MAP1_DIR if self.state == _S_MAP1 else MAP2_DIR
            idx    = self.map_buttons.index(btn)
            path   = os.path.join(folder, self._map_filenames[idx])
            if self.state == _S_MAP1:
                self.result = ("1 Agent", (self.algo, path))
            else:
                self.result = ("2 Agents", (int(self.steps_input), path))
            self.running = False

    def _build_maps(self, folder: str):
        maps = _get_maps(folder)
        f = pygame.font.SysFont("arial", 18, bold=True)
        # Lưu tên file gốc để dùng khi build path, nhưng hiển thị dạng 'Map 1'
        self._map_filenames = maps
        self.map_buttons = [
            Button((WIDTH//2 - 130, 155 + i * 52, 260, 42), f"Map {i+1}", f)
            for i, name in enumerate(maps)
        ]

    # ── Input ────────────────────────────────────────────────────────────────

    def _handle_key(self, event):
        if self.state == _S_STEPS and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.steps_input = self.steps_input[:-1]
            elif event.unicode.isdigit() and len(self.steps_input) < 4:
                self.steps_input += event.unicode

    # ── Draw ─────────────────────────────────────────────────────────────────

    def _draw(self):
        self.screen.blit(self.bg, (0, 0))

        # Title
        sh = self._f_title.render("SOKOBAN", True, C_SHADOW)
        ti = self._f_title.render("SOKOBAN", True, C_TEXT)
        self.screen.blit(sh, sh.get_rect(center=(WIDTH//2 + 2, 67)))
        self.screen.blit(ti, ti.get_rect(center=(WIDTH//2, 65)))

        if self.state == _S_MODE:
            sub = "Select game mode"
        elif self.state == _S_ALGO:
            sub = "Select algorithm"
        elif self.state == _S_STEPS:
            sub = "Enter number of steps (>= 1):"
        elif self.state == _S_MAP1:
            sub = "Select map  –  1 Agent"
        else:
            sub = "Select map  –  2 Agents"

        s = self._f_sub.render(sub, True, C_TEXT)
        self.screen.blit(s, s.get_rect(center=(WIDTH//2, 120)))

        # Input box for steps
        if self.state == _S_STEPS:
            pygame.draw.rect(self.screen, C_INPUT_BG,    self.input_rect, border_radius=6)
            pygame.draw.rect(self.screen, C_INPUT_BORDER, self.input_rect, 2, border_radius=6)
            inp = self._f_inp.render(self.steps_input + "|", True, (30, 30, 30))
            self.screen.blit(inp, inp.get_rect(center=self.input_rect.center))

        if self.state in (_S_MAP1, _S_MAP2) and not self.map_buttons:
            nm = self._f_sub.render("No maps found!", True, C_NOTE)
            self.screen.blit(nm, nm.get_rect(center=(WIDTH//2, 230)))

        for btn in self._active_btns():
            btn.draw(self.screen)

        if self.note:
            n = self._f_sm.render(self.note, True, C_NOTE)
            self.screen.blit(n, n.get_rect(center=(WIDTH//2, 480)))

    # ── Run ──────────────────────────────────────────────────────────────────

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self._handle_key(event)
                for btn in self._active_btns():
                    if btn.handle_event(event):
                        self._on_click(btn)
                        break
            self._draw()
            pygame.display.flip()
            clock.tick(60)
        return self.result
