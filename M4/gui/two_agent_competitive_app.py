import time
import pygame

try:
    from .two_agent_board_view import TwoAgentBoardView
except ImportError:
    from two_agent_board_view import TwoAgentBoardView

class TwoAgentCompetitiveApp:
    def __init__(self, problem, agent_a, agent_b, fps=5):
        pygame.init()

        self.problem = problem
        self.state = problem.initial_state
        self.agent_a = agent_a
        self.agent_b = agent_b

        self.view = TwoAgentBoardView(problem)
        self.width = max(720, self.view.width)
        self.height = 120 + self.view.height + 20

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Sokoban - Competitive Mode")

        self.clock = pygame.time.Clock()
        self.fps = fps
        self.running = True
        self.paused = True
        self.time_a_ms = 0.0
        self.time_b_ms = 0.0

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

        self.state = self.problem.transition_model(
            pre_state,
            action_a,
            action_b
        )

    def text(self, value, x, y, size=24):
        font = pygame.font.Font(None, size)
        image = font.render(value, True, (30, 30, 30))
        self.screen.blit(image, (x, y))

    def draw(self):
        self.screen.fill((255, 255, 255))

        self.text("Agent A: " + str(self.state.score_a), 20, 15, 28)
        self.text("Agent B: " + str(self.state.score_b), 210, 15, 28)
        self.text("Steps left: " + str(self.state.steps_left), 400, 15, 28)

        self.text("A: %.2f ms" % self.time_a_ms, 20, 50, 20)
        self.text("B: %.2f ms" % self.time_b_ms, 210, 50, 20)
        self.text("SPACE: Pause/Resume | ESC: Exit", 20, 82, 20)

        if self.paused:
            self.text("PAUSED", 560, 50, 22)

        if self.problem.is_terminal(self.state):
            self.text("GAME OVER", 560, 15, 22)

        self.view.draw(self.screen, self.state)
        pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def run(self):
        while self.running:
            self.events()
            self.step()
            self.draw()
            self.clock.tick(self.fps)
        pygame.quit()