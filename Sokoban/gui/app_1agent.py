import threading
import pygame
from gui.widgets import (Button, make_bg, make_wall_tile, draw_box, draw_doraemon,
                         shadow_text, C_OUTLINE, C_INFO_BG, C_INFO_TEXT,
                         C_STATUS, C_FLOOR, C_GOAL_FLOOR, C_GOAL_MARK,
                         C_GOAL_MARK_DONE, C_BOX_FREE)
from core.map_parser import MapParser
from core.sokoban    import SokobanProblem, ucs, astar
from core.heuristic  import Heuristic

CELL  = 44
PANEL = 220
MRG   = 20
MIN_H = 460
DELAY = 220  

_ST_WAITING   = "waiting"    
_ST_SOLVING   = "solving"    
_ST_NO_SOL    = "no_sol"     
_ST_PLAYING   = "playing"  
_ST_PAUSED    = "paused"   
_ST_DONE      = "done"    


class _BoardView:
    def __init__(self, problem):
        self.problem = problem
        cells = (problem.walls | problem.goals |
                 {problem.initial_state.agent_pos} |
                 set(problem.initial_state.boxes))
        self.n_rows = max(r for r, _ in cells) + 1
        self.n_cols = max(c for _, c in cells) + 1
        self.width  = self.n_cols * CELL
        self.height = self.n_rows * CELL
        self.wall_t = make_wall_tile(CELL)

    def draw(self, surf, state):
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                pos  = (r, c)
                rect = pygame.Rect(c * CELL, r * CELL, CELL, CELL)
                if pos in self.problem.walls:
                    surf.blit(self.wall_t, rect)
                elif pos in self.problem.goals:
                    pygame.draw.rect(surf, C_GOAL_FLOOR, rect)
                    on_box = pos in state.boxes
                    pygame.draw.rect(surf, C_GOAL_MARK_DONE if on_box else C_GOAL_MARK, rect, 3)
                else:
                    pygame.draw.rect(surf, C_FLOOR, rect)

        for box in state.boxes:
            r, c = box
            inner = pygame.Rect(c * CELL + 4, r * CELL + 4, CELL - 8, CELL - 8)
            draw_box(surf, inner, box in self.problem.goals, C_BOX_FREE)

        ar, ac = state.agent_pos
        draw_doraemon(surf, (ac * CELL + CELL // 2, ar * CELL + CELL // 2), CELL)


class SingleAgentApp:
    def __init__(self, screen: pygame.Surface, map_path: str, algorithm: str):
        self.screen     = screen
        self.map_path   = map_path
        self.algorithm  = algorithm
        self.level_name = map_path.replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0]
        self.clock      = pygame.time.Clock()
        self._f_big  = pygame.font.SysFont("arial", 18, bold=True)
        self._f_med  = pygame.font.SysFont("arial", 22, bold=True)
        self._f_sm   = pygame.font.SysFont("arial", 16)
        self._f_hint = pygame.font.SysFont("arial", 15)
        self._f_btn  = pygame.font.SysFont("arial", 20, bold=True)

    def run(self):
        mp        = MapParser(self.map_path)
        problem   = SokobanProblem(mp)
        heuristic = Heuristic(mp.board_matrix, list(problem.goals))
        view      = _BoardView(problem)
        bsurf     = pygame.Surface((view.width, view.height))
        bpos      = (PANEL + MRG, MRG)
        W         = PANEL + view.width + 2 * MRG
        H         = max(view.height + 2 * MRG, MIN_H)
        self.screen = pygame.display.set_mode((W, H))
        bg        = make_bg(W, H)
        pygame.display.set_caption(f"Sokoban – {self.algorithm} – {self.level_name}")

        btn_back = Button((MRG, H - 60, PANEL - 2 * MRG, 42), "← Menu", self._f_btn)

        states  = [problem.initial_state]
        idx     = 0
        timer   = 0
        phase   = _ST_WAITING
        dot_t   = 0   
        dots    = 0

        def _solve_thread():
            nonlocal states, phase
            if self.algorithm == "UCS":
                path, _, __ = ucs(problem)
            else:
                path, _, __ = astar(problem, heuristic)
            if path is None:
                phase = _ST_NO_SOL
                return
            s = problem.initial_state
            st = [s]
            for a in path:
                s = problem.result(s, a)
                st.append(s)
            states = st
            phase  = _ST_PLAYING   

        while True:
            dt = self.clock.tick(60)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: return
                if btn_back.handle_event(ev): return

                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE:
                        if phase == _ST_WAITING:
                            phase = _ST_SOLVING
                            threading.Thread(target=_solve_thread, daemon=True).start()
                        elif phase == _ST_PLAYING:
                            phase = _ST_PAUSED
                        elif phase == _ST_PAUSED:
                            if idx < len(states) - 1:
                                phase = _ST_PLAYING
                    elif ev.key == pygame.K_LEFT and phase == _ST_PAUSED:
                        if idx > 0: idx -= 1
                    elif ev.key == pygame.K_RIGHT and phase == _ST_PAUSED:
                        if idx < len(states) - 1: idx += 1

            if phase == _ST_PLAYING:
                timer += dt
                if timer >= DELAY:
                    timer = 0
                    if idx < len(states) - 1:
                        idx += 1
                    else:
                        phase = _ST_DONE

            if phase == _ST_SOLVING:
                dot_t += dt
                if dot_t >= 400:
                    dot_t = 0
                    dots  = (dots + 1) % 4

            self.screen.blit(bg, (0, 0))

            view.draw(bsurf, states[idx])
            br = bsurf.get_rect(topleft=bpos)
            self.screen.blit(bsurf, br)
            pygame.draw.rect(self.screen, C_OUTLINE, br.inflate(6, 6), 3)

            shadow_text(self.screen, self._f_big, "Level: " + self.level_name, (MRG, 15))
            shadow_text(self.screen, self._f_med, self.algorithm, (MRG, 55))

            info = pygame.Rect(MRG, 95, PANEL - 2 * MRG, 130)
            pygame.draw.rect(self.screen, C_INFO_BG, info, border_radius=8)
            x0, y0 = info.x + 12, info.y + 12

            if phase == _ST_WAITING:
                status = "Ready"
                hint   = "Press SPACE to start"
            elif phase == _ST_SOLVING:
                status = "Calculating" + "." * dots
                hint   = "Please wait..."
            elif phase == _ST_NO_SOL:
                status = "No solution found"
                hint   = ""
            elif phase == _ST_PLAYING:
                status = "Running..."
                hint   = "SPACE: pause"
            elif phase == _ST_PAUSED:
                status = "Paused"
                hint   = "SPACE: resume  ←/→: step"
            else:  
                status = "Completed! 🎉"
                hint   = ""

            self.screen.blit(self._f_sm.render(status, True, C_STATUS),    (x0, y0))
            self.screen.blit(self._f_sm.render(f"Step : {idx}",                   True, C_INFO_TEXT), (x0, y0 + 28))
            self.screen.blit(self._f_sm.render(f"Total: {max(len(states)-1,0)}",  True, C_INFO_TEXT), (x0, y0 + 52))
            if hint:
                self.screen.blit(self._f_hint.render(hint, True, (180, 180, 180)), (x0, y0 + 82))

            btn_back.draw(self.screen)
            pygame.display.flip()
