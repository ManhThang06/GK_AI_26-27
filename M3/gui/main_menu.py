import pygame
from ui_widgets import Button, make_grass

WIDTH, HEIGHT = 480, 420
COLOR_TITLE = (40, 40, 40)
COLOR_SHADOW = (255, 255, 255)
COLOR_SUBTITLE = (40, 40, 40)
COLOR_NOTE = (150, 30, 30)
SCREEN_MODE = "mode"
SCREEN_ALGO = "algo"

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.background = make_grass(WIDTH, HEIGHT)
        self.font_title = pygame.font.SysFont("arial", 48, bold=True)
        self.font_text = pygame.font.SysFont("arial", 22)
        font_btn = pygame.font.SysFont("arial", 24, bold=True)
        self.current = SCREEN_MODE
        self.algorithm = "UCS"
        self.note = ""
        self.running = True
        self.result = None
        left = WIDTH // 2 - 100
        self.btn_one = Button((left, 160, 200, 50), "1 Agent", font_btn)
        self.btn_two = Button((left, 235, 200, 50), "2 Agents", font_btn)
        self.btn_exit = Button((left, 310, 200, 50), "Exit", font_btn)
        self.btn_ucs = Button((WIDTH // 2 - 105, 160, 100, 50), "UCS", font_btn)
        self.btn_astar = Button((WIDTH // 2 + 5, 160, 100, 50), "A*", font_btn)
        self.btn_start = Button((left, 250, 200, 50), "Start", font_btn)
        self.btn_back = Button((left, 325, 200, 50), "Back", font_btn)
        self.btn_ucs.selected = True

    def current_buttons(self):
        if self.current == SCREEN_MODE:
            return [self.btn_one, self.btn_two, self.btn_exit]
        return [self.btn_ucs, self.btn_astar, self.btn_start, self.btn_back]

    def on_click(self, button):
        if button is self.btn_one:
            self.current = SCREEN_ALGO
            self.note = ""
        elif button is self.btn_two:
            self.note = "2 Agents mode is handled by M4"
        elif button is self.btn_exit:
            self.running = False
        elif button is self.btn_ucs or button is self.btn_astar:
            self.algorithm = button.text
            self.btn_ucs.selected = button is self.btn_ucs
            self.btn_astar.selected = button is self.btn_astar
        elif button is self.btn_start:
            self.result = ("1 Agent", self.algorithm)
            self.running = False
        elif button is self.btn_back:
            self.current = SCREEN_MODE

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        shadow = self.font_title.render("SOKOBAN", True, COLOR_SHADOW)
        self.screen.blit(shadow, shadow.get_rect(center=(WIDTH // 2 + 3, 68)))
        title = self.font_title.render("SOKOBAN", True, COLOR_TITLE)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 65)))
        if self.current == SCREEN_MODE:
            subtitle_text = "Choose game mode"
        else:
            subtitle_text = "Choose algorithm"
        subtitle = self.font_text.render(subtitle_text, True, COLOR_SUBTITLE)
        self.screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 120)))
        for button in self.current_buttons():
            button.draw(self.screen)
        if self.note:
            note = self.font_text.render(self.note, True, COLOR_NOTE)
            self.screen.blit(note, note.get_rect(center=(WIDTH // 2, 390)))

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                for button in self.current_buttons():
                    if button.handle_event(event):
                        self.on_click(button)
                        break
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        return self.result

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sokoban - Main Menu")
    result = MainMenu(screen).run()
    print("Ket qua menu:", result)
    pygame.quit()

if __name__ == "__main__":
    main()