import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from engine_stub import SokobanProblem
from board_view import BoardView, CELL_SIZE

BACKGROUND_COLOR = (240, 240, 240)
MAP_PATH = "example_map.txt"


class Renderer:
    def __init__(self, map_path):
        pygame.init()
        self.problem = SokobanProblem(map_path)
        self.board_view = BoardView(self.problem)

        self.screen = pygame.display.set_mode(
            (self.board_view.width, self.board_view.height)
        )
        pygame.display.set_caption("Sokoban")
        self.clock = pygame.time.Clock()
        self.current_state = self.problem.initial_state

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill(BACKGROUND_COLOR)
            self.board_view.draw(self.screen, self.current_state)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    map_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), MAP_PATH)
    renderer = Renderer(map_full_path)
    renderer.run()