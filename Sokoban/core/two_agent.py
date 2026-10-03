import time
import pygame

try:
    from .two_agent_board_view import TwoAgentBoardView
    from .ui_widgets import make_grass
except ImportError:
    from two_agent_board_view import TwoAgentBoardView
    from ui_widgets import make_grass

PANEL_WIDTH = 220
MARGIN = 20
MIN_HEIGHT = 460
COLOR_INFO_BOX = (25, 25, 25)
COLOR_INFO_TEXT = (255, 255, 255)
COLOR_STATUS = (250, 210, 60)

class TwoAgentCompetitiveApp:
    def __init__(self, problem, agent_a, agent_b, fps=5):
        pygame.init()

        self.problem = problem
        self.state = problem.initial_state
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.view = TwoAgentBoardView(problem)
        self.board_surface = pygame.Surface((self.view.width, self.view.height))
        self.board_pos = (PANEL_WIDTH + MARGIN, MARGIN)
        self.width = (PANEL_WIDTH + self.view.width + 2 * MARGIN)
        self.height = max(self.view.height + 2 * MARGIN, MIN_HEIGHT)
        self.background = make_grass(self.width, self.height)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Sokoban - Competitive Mode")
        self.font = pygame.font.Font(None, 22)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.running = True
        self.paused = True
        self.time_a_ms = 0.0
        self.time_b_ms = 0.0
        self.history = [self.state]
        self.history_times = [(0.0, 0.0)]
        self.history_index = 0
        self.start_button = pygame.Rect(MARGIN, 315, PANEL_WIDTH - 2 * MARGIN, 40)

    def step(self):
        if self.paused or self.problem.is_terminal(self.state):
            return

        pre_state = self.state
        start = time.perf_counter()
        action_a = self.agent_a.choose_action(pre_state, self.problem)
        self.time_a_ms = (time.perf_counter() - start) * 1000
        start = time.perf_counter()
        action_b = self.agent_b.choose_action(pre_state, self.problem)
        self.time_b_ms = (time.perf_counter() - start) * 1000
        self.state = self.problem.transition_model(pre_state, action_a, action_b)

        # Neu dang o mot state cu va chay lai, bo nhanh history phia truoc.
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
            self.history_times = self.history_times[:self.history_index + 1]

        self.history.append(self.state)
        self.history_times.append((self.time_a_ms, self.time_b_ms))
        self.history_index += 1

    def text(self, value, x, y, size=24):
        font = pygame.font.Font(None, size)
        image = font.render(value, True, (30, 30, 30))
        self.screen.blit(image, (x, y))

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        info_rect = pygame.Rect(MARGIN, 60, PANEL_WIDTH - 2 * MARGIN, 230)
        pygame.draw.rect(self.screen, COLOR_INFO_BOX, info_rect, border_radius=8)
        x = MARGIN + 15
        y = 75
        text = self.font.render("COMPETITIVE MODE", True, COLOR_INFO_TEXT)
        self.screen.blit(text, (x, y))
        y += 35
        text = self.font.render("Agent A", True, COLOR_INFO_TEXT)
        self.screen.blit(text, (x, y))
        y += 25
        text = self.font.render(f"Score: {self.state.score_a}", True, COLOR_INFO_TEXT)
        self.screen.blit(text, (x, y))
        y += 25
        text = self.font.render(f"Time: {self.time_a_ms:.2f} ms", True, COLOR_INFO_TEXT)
        self.screen.blit(text, (x, y))

        y += 35
        text = self.font.render("Agent B", True, COLOR_INFO_TEXT)
        self.screen.blit(text, (x, y))
        y += 25
        text = self.font.render(f"Score: {self.state.score_b}", True, COLOR_INFO_TEXT)
        self.screen.blit(text, (x, y))
        y += 25
        text = self.font.render(f"Time: {self.time_b_ms:.2f} ms", True, COLOR_INFO_TEXT)
        self.screen.blit(text, (x, y))
        y += 30
        if self.paused:
            button_text = "START"
        else:
            button_text = "PAUSE"
        button_image = self.font.render(button_text, True, COLOR_INFO_TEXT)
        button_rect = button_image.get_rect(center=self.start_button.center)
        self.screen.blit(button_image, button_rect)
        text = self.font.render(f"Steps left: {self.state.steps_left}", True, COLOR_INFO_TEXT)
        self.screen.blit(text, (x, y))
        y += 25
        text = self.font.render(f"Actions: {self.history_index}", True, COLOR_INFO_TEXT)
        self.screen.blit(text, (x, y))
        self.text("Space: Pause | Left: Back | Right: Forward", MARGIN, self.height - 28, 18)
        pygame.draw.rect(self.screen, (240, 150, 50), self.start_button, border_radius=8)
        
        if self.paused:
            self.text("PAUSED", 560, 50, 22)
        if self.problem.is_terminal(self.state):
            self.text("GAME OVER", 560, 15, 22)
        self.board_surface.fill((255, 255, 255))
        self.view.draw(self.board_surface, self.state)
        self.screen.blit(self.board_surface, self.board_pos)
        pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_LEFT:
                    self.paused = True
                    if self.history_index > 0:
                        self.history_index -= 1
                        self.state = self.history[self.history_index]
                        self.time_a_ms, self.time_b_ms = self.history_times[self.history_index]
                elif event.key == pygame.K_RIGHT:
                    self.paused = True
                    if self.history_index < len(self.history) - 1:
                        self.history_index += 1
                        self.state = self.history[self.history_index]
                        self.time_a_ms, self.time_b_ms = self.history_times[self.history_index]
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def run(self):
        while self.running:
            self.events()
            self.step()
            self.draw()
            self.clock.tick(self.fps)
        pygame.quit()