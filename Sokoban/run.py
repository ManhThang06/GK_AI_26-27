"""
run.py – Entry point duy nhất của Sokoban game.
Chỉ cần chạy: python run.py
Không phụ thuộc vào bất kỳ folder M2/M3/M4 nào.
"""
import sys
import os

# Đưa thư mục Sokoban/ vào sys.path để import package 'core' và 'gui' đúng
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pygame
from gui.main_menu  import MainMenu, WIDTH, HEIGHT
from gui.app_1agent import SingleAgentApp
from gui.app_2agent import TwoAgentApp


def main():
    pygame.init()

    while True:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sokoban")
        result = MainMenu(screen).run()

        if result is None:
            break

        mode, data = result

        if mode == "1 Agent":
            algorithm, map_path = data
            SingleAgentApp(screen, map_path, algorithm).run()

        elif mode == "2 Agents":
            n_steps, map_path = data
            TwoAgentApp(screen, map_path, n_steps).run()

    pygame.quit()


if __name__ == "__main__":
    main()
