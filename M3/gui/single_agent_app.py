import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pygame
from engine_stub import SokobanProblem
from search_stub import ucs, astar
from heuristics_stub import zero_heuristic
from board_view import BoardView
from ui_widgets import Button, make_grass, COLOR_OUTLINE
from main_menu import MainMenu, WIDTH as MENU_WIDTH, HEIGHT as MENU_HEIGHT

MAP_PATH = "example_map.txt"
STEP_DELAY_MS = 200
PANEL_WIDTH = 220
MARGIN = 20
MIN_HEIGHT = 460
COLOR_TEXT = (40, 40, 40)
COLOR_SHADOW = (255, 255, 255)
COLOR_INFO_BOX = (25, 25, 25)
COLOR_INFO_TEXT = (255, 255, 255)
COLOR_STATUS = (250, 210, 60)

class GameController:
    def __init__(self, problem, algorithm):
        self.problem = problem
        self.algorithm = algorithm
        self.states = [problem.initial_state]
        self.index = 0
        self.paused = True
        self.timer = 0
        self.attempted = False
        self.found = False

    def solve(self):
        self.attempted = True
        if self.algorithm == "UCS":
            path, cost, expanded, max_frontier = ucs(self.problem)
        else:
            path, cost, expanded, max_frontier = astar(self.problem, zero_heuristic)
        if path is None:
            self.found = False
            return False
        state = self.problem.initial_state
        self.states = [state]
        for action in path:
            state = self.problem.result(state, action)
            self.states.append(state)
        self.index = 0
        self.paused = True
        self.found = True
        return True
    def current_state(self):
        return self.states[self.index]
    def action_count(self):
        return self.index
    def is_finished(self):
        return self.index == len(self.states) - 1
    def toggle_pause(self):
        self.paused = not self.paused
    def step_forward(self):
        self.paused = True
        if not self.is_finished():
            self.index += 1
    def step_backward(self):
        self.paused = True
        if self.index > 0:
            self.index -= 1
    def update(self, elapsed_ms):
        if self.paused or self.is_finished():
            return
        self.timer += elapsed_ms
        if self.timer >= STEP_DELAY_MS:
            self.timer = 0
            self.index += 1


class SingleAgentApp:
    def __init__(self, map_path):
        pygame.init()
        self.map_path = map_path
        self.level_name = os.path.splitext(os.path.basename(map_path))[0]
        self.screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
        pygame.display.set_caption("Sokoban")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("arial", 18, bold=True)
        self.font_text = pygame.font.SysFont("arial", 22, bold=True)
        self.font_small = pygame.font.SysFont("arial", 16)
        self.font_btn = pygame.font.SysFont("arial", 20, bold=True)

    def run(self):
        while True:
            self.screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
            pygame.display.set_caption("Sokoban - Main Menu")
            result = MainMenu(self.screen).run()
            if result is None:
                break
            mode, algorithm = result
            if not self.play(algorithm):
                break
        pygame.quit()

    def play(self, algorithm):
        problem = SokobanProblem(self.map_path)
        self.board_view = BoardView(problem)
        self.board_surface = pygame.Surface((self.board_view.width, self.board_view.height))
        self.board_pos = (PANEL_WIDTH + MARGIN, MARGIN)
        width = PANEL_WIDTH + self.board_view.width + 2 * MARGIN
        self.height = max(self.board_view.height + 2 * MARGIN, MIN_HEIGHT)
        self.screen = pygame.display.set_mode((width, self.height))
        self.background = make_grass(width, self.height)
        pygame.display.set_caption("Sokoban - " + algorithm)
        self.controller = GameController(problem, algorithm)
        self.clock.tick()
        self.btn_find = Button((MARGIN, 205, PANEL_WIDTH - 2 * MARGIN, 42), "Find Path", self.font_btn)
        self.btn_show = Button((MARGIN, 253, PANEL_WIDTH - 2 * MARGIN, 42), "Show Path", self.font_btn)
        half_w = (PANEL_WIDTH - 2 * MARGIN - 8) // 2
        self.btn_undo = Button((MARGIN, 301, half_w, 40), "<", self.font_btn)
        self.btn_redo = Button((MARGIN + half_w + 8, 301, half_w, 40), ">", self.font_btn)
        self.btn_back = Button((MARGIN, self.height - 60, PANEL_WIDTH - 2 * MARGIN, 42), "Back", self.font_btn)
        self.btn_exit = Button((width - 44, 12, 32, 32), "X", self.font_btn)
        while True:
            elapsed = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if self.btn_back.handle_event(event):
                    return True
                if self.btn_exit.handle_event(event):
                    return False
                if self.btn_find.handle_event(event) and not self.controller.attempted:
                    self.controller.solve()
                if self.controller.found and self.btn_show.handle_event(event):
                    self.controller.paused = False
                if self.controller.found and self.btn_undo.handle_event(event):
                    self.controller.step_backward()
                if self.controller.found and self.btn_redo.handle_event(event):
                    self.controller.step_forward()
                if event.type == pygame.KEYDOWN and self.controller.found:
                    if event.key == pygame.K_SPACE:
                        self.controller.toggle_pause()
                    elif event.key == pygame.K_RIGHT:
                        self.controller.step_forward()
                    elif event.key == pygame.K_LEFT:
                        self.controller.step_backward()
            self.controller.update(elapsed)
            self.draw_game()
            pygame.display.flip()

    def draw_game(self):
        self.screen.blit(self.background, (0, 0))
        self.board_view.draw(self.board_surface, self.controller.current_state())
        board_rect = self.board_surface.get_rect(topleft=self.board_pos)
        self.screen.blit(self.board_surface, board_rect)
        pygame.draw.rect(self.screen, COLOR_OUTLINE, board_rect.inflate(6, 6), 3)
        self.draw_shadow_text("Level: " + self.level_name, self.font_big, (MARGIN, 15))
        self.draw_shadow_text(self.controller.algorithm, self.font_text, (MARGIN, 55))
        box = pygame.Rect(MARGIN, 90, PANEL_WIDTH - 2 * MARGIN, 100)
        pygame.draw.rect(self.screen, COLOR_INFO_BOX, box, border_radius=8)
        if not self.controller.attempted:
            status = "Press Find Path"
        elif not self.controller.found:
            status = "No solution"
        elif self.controller.is_finished():
            status = "Finished"
        elif self.controller.paused:
            status = "Paused"
        else:
            status = "Playing"
        self.screen.blit(self.font_small.render(status, True, COLOR_STATUS), (box.x + 10, box.y + 10))
        actions = "Steps: " + str(self.controller.action_count())
        self.screen.blit(self.font_small.render(actions, True, COLOR_INFO_TEXT), (box.x + 10, box.y + 36))
        total = "Total: " + str(max(len(self.controller.states) - 1, 0))
        self.screen.blit(self.font_small.render(total, True, COLOR_INFO_TEXT), (box.x + 10, box.y + 60))
        self.btn_find.draw(self.screen)
        self.btn_show.draw(self.screen)
        self.btn_undo.draw(self.screen)
        self.btn_redo.draw(self.screen)
        self.btn_back.draw(self.screen)
        self.btn_exit.draw(self.screen)

    def draw_shadow_text(self, text, font, pos):
        shadow = font.render(text, True, COLOR_SHADOW)
        main = font.render(text, True, COLOR_TEXT)
        self.screen.blit(shadow, (pos[0] + 2, pos[1] + 2))
        self.screen.blit(main, pos)

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SingleAgentApp(os.path.join(root, MAP_PATH)).run()
if __name__ == "__main__":
    main()