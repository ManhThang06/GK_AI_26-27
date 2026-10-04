import time
import pygame
from gui.widgets import (Button, make_bg, make_wall_tile, draw_box,
                         draw_doraemon, draw_agent_b,
                         C_INFO_BG, C_INFO_TEXT, C_STATUS,
                         C_FLOOR, C_GOAL_MARK, C_GOAL_MARK_DONE,
                         C_BOX_FREE, C_BOX_A, C_BOX_B, C_OUTLINE)
from core.map_parser  import MapParser
from core.two_agent   import TwoAgentProblem
from core.agent1 import AgentAlgorithm1
from core.agent2 import AgentAlgorithm2
from core.heuristic   import Heuristic

CELL  = 44
PANEL = 220
MRG   = 20
MIN_H = 500

class _BoardView2:
    def __init__(self, problem):
        self.problem = problem
        cells = (problem.walls | problem.goals |
                 {problem.initial_state.agent_a_pos,
                  problem.initial_state.agent_b_pos} |
                 set(problem.initial_state.boxes))
        self.n_rows = max(r for r, _ in cells) + 1
        self.n_cols = max(c for _, c in cells) + 1
        self.width  = self.n_cols * CELL
        self.height = self.n_rows * CELL
        self.wall_t = make_wall_tile(CELL)

    def draw(self, surf, state):
        owners = dict(state.box_owner)

        for r in range(self.n_rows):
            for c in range(self.n_cols):
                pos  = (r, c)
                rect = pygame.Rect(c * CELL, r * CELL, CELL, CELL)
                if pos in self.problem.walls:
                    surf.blit(self.wall_t, rect)
                else:
                    pygame.draw.rect(surf, C_FLOOR, rect)
                    if pos in self.problem.goals:
                        on_box = pos in state.boxes
                        mark_c = C_GOAL_MARK_DONE if on_box else C_GOAL_MARK
                        pygame.draw.rect(surf, mark_c, rect, 3)

        for box in state.boxes:
            r, c  = box
            owner = owners.get(box)
            color = C_BOX_A if owner == "A" else (C_BOX_B if owner == "B" else C_BOX_FREE)
            inner = pygame.Rect(c*CELL+4, r*CELL+4, CELL-8, CELL-8)
            draw_box(surf, inner, box in self.problem.goals, color)

        ar, ac = state.agent_a_pos
        draw_doraemon(surf, (ac*CELL+CELL//2, ar*CELL+CELL//2), CELL)
        br, bc = state.agent_b_pos
        draw_agent_b(surf, (bc*CELL+CELL//2, br*CELL+CELL//2), CELL)

class TwoAgentApp:
    def __init__(self, screen: pygame.Surface, map_path: str, n_steps: int, fps: int = 5):
        self.screen   = screen
        self.map_path = map_path
        self.n_steps  = n_steps
        self.fps      = fps
        self._f       = pygame.font.Font(None, 22)
        self._f_btn   = pygame.font.SysFont("arial", 18, bold=True)

    def _build(self):
        mp     = MapParser(self.map_path)
        pos_a, pos_b = mp.two_agent_start()
        prob   = TwoAgentProblem(mp, pos_a, pos_b, self.n_steps)
        h      = Heuristic(mp.board_matrix, list(prob.goals))
        agent_a = AgentAlgorithm1(heuristic=h, time_limit=0.9)
        agent_b = AgentAlgorithm2(heuristic=h, time_limit=0.9)
        return prob, agent_a, agent_b

    def run(self):
        prob, agent_a, agent_b = self._build()
        view  = _BoardView2(prob)
        bsurf = pygame.Surface((view.width, view.height))
        bpos  = (PANEL + MRG, MRG)
        W     = PANEL + view.width + 2 * MRG
        H     = max(view.height + 2 * MRG, MIN_H)
        self.screen = pygame.display.set_mode((W, H))
        bg    = make_bg(W, H)
        pygame.display.set_caption("Sokoban – 2 Agents Competitive")

        state   = prob.initial_state
        paused  = True
        t_a, t_b = 0.0, 0.0
        clock   = pygame.time.Clock()

        # History de xem lai cac buoc da choi.
        history = [state]
        history_times = [(t_a, t_b)]
        history_index = 0

        # Buttons
        btn_back    = Button((MRG, 18,  PANEL - 2*MRG, 36), "← Menu",   self._f_btn)
        btn_toggle  = Button((MRG, 315, PANEL - 2*MRG, 40), "START",   self._f_btn)
        btn_step    = Button((MRG, 365, PANEL - 2*MRG, 40), "STEP",    self._f_btn)
        btn_restart = Button((MRG, 415, PANEL - 2*MRG, 40), "RESTART", self._f_btn)

        def do_step():
            nonlocal state, t_a, t_b, history_index
            if history_index < len(history) - 1:
                history_index += 1
                state = history[history_index]
                t_a, t_b = history_times[history_index]
                return

            if prob.is_terminal(state):
                return
            pre = state

            t0 = time.perf_counter()
            a_a = agent_a.choose_action(pre, prob)
            t_a = (time.perf_counter() - t0) * 1000

            t0 = time.perf_counter()
            a_b = agent_b.choose_action(pre, prob)
            t_b = (time.perf_counter() - t0) * 1000

            state = prob.transition_model(pre, a_a, a_b)
            history.append(state)
            history_times.append((t_a, t_b))
            history_index += 1

        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: running = False
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE:
                        paused = not paused
                    elif ev.key == pygame.K_LEFT:
                        paused = True
                        if history_index > 0:
                            history_index -= 1
                            state = history[history_index]
                            t_a, t_b = history_times[history_index]
                    elif ev.key == pygame.K_RIGHT:
                        paused = True
                        if history_index < len(history) - 1:
                            history_index += 1
                            state = history[history_index]
                            t_a, t_b = history_times[history_index]
                    elif ev.key == pygame.K_ESCAPE:
                        running = False
                if btn_back.handle_event(ev):    running = False
                if btn_toggle.handle_event(ev):  paused = not paused
                if btn_step.handle_event(ev):
                    if paused and not prob.is_terminal(state): do_step()
                if btn_restart.handle_event(ev):
                    # Tao lai toan bo game de xoa trang thai cu cua 2 agent.
                    prob, agent_a, agent_b = self._build()
                    state = prob.initial_state
                    view = _BoardView2(prob)
                    bsurf = pygame.Surface((view.width, view.height))
                    t_a = t_b = 0.0
                    paused = True
                    history = [state]
                    history_times = [(t_a, t_b)]
                    history_index = 0

            if not paused and not prob.is_terminal(state):
                do_step()
                if prob.is_terminal(state): paused = True

            self.screen.blit(bg, (0, 0))

            btn_toggle.text = "PAUSE" if not paused else "START"
            for btn in (btn_back, btn_toggle, btn_step, btn_restart):
                btn.draw(self.screen)

            hint = self._f.render("SPACE: pause   <- / ->: history", True, C_INFO_TEXT)
            self.screen.blit(hint, (MRG, 465))

            # Info panel
            ip = pygame.Rect(MRG, 65, PANEL - 2*MRG, 235)
            pygame.draw.rect(self.screen, C_INFO_BG, ip, border_radius=8)
            f, x, y = self._f, MRG + 12, 80

            def lbl(txt, color=C_INFO_TEXT):
                nonlocal y
                self.screen.blit(f.render(txt, True, color), (x, y)); y += 22

            lbl("COMPETITIVE MODE", C_STATUS)
            y += 6
            lbl("Agent A  (Doraemon)"); lbl(f"  Score : {state.score_a}"); lbl(f"  Time  : {t_a:.1f} ms")
            y += 6
            lbl("Agent B  (Doraemi)");     lbl(f"  Score : {state.score_b}"); lbl(f"  Time  : {t_b:.1f} ms")
            y += 6
            lbl(f"Steps left : {state.steps_left}", C_STATUS)
            lbl(f"History    : {history_index}/{len(history) - 1}")

            # Board
            bsurf.fill((255, 255, 255))
            view.draw(bsurf, state)
            self.screen.blit(bsurf, bpos)

            # Game-over overlay
            if prob.is_terminal(state):
                if   state.score_a > state.score_b: res = "AGENT A WINS! 🎉"
                elif state.score_b > state.score_a: res = "AGENT B WINS! 🎉"
                else:                               res = "DRAW! 🤝"
                ov = pygame.Rect(0, 0, 320, 150)
                ov.center = (W // 2, H // 2)
                pygame.draw.rect(self.screen, (20, 20, 20), ov, border_radius=14)
                go = self._f.render("GAME OVER", True, C_STATUS)
                rs = self._f.render(res, True, C_STATUS)
                self.screen.blit(go, go.get_rect(center=(ov.centerx, ov.centery - 28)))
                self.screen.blit(rs, rs.get_rect(center=(ov.centerx, ov.centery + 22)))
            pygame.display.flip()
            clock.tick(self.fps)