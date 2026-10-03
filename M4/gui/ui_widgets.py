import pygame
COLOR_BG = (210, 185, 155)
COLOR_OUTLINE = (30, 30, 30)
COLOR_BTN = (222, 115, 38)
COLOR_BTN_EDGE = (150, 80, 30)
COLOR_BTN_HOVER = (240, 140, 60)
COLOR_BTN_DOWN = (170, 85, 25)
COLOR_BTN_SELECTED = (105, 55, 40)
COLOR_BTN_SELECTED_EDGE = (70, 35, 25)
COLOR_BTN_TEXT = (30, 30, 30)
COLOR_BTN_TEXT_SELECTED = (255, 255, 255)
EDGE = 5

def make_grass(width, height):
    surface = pygame.Surface((width, height))
    surface.fill(COLOR_BG)
    return surface

class Button:
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.selected = False
        self.pressed = False
    def handle_event(self, event):
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
        text_color = COLOR_BTN_TEXT
        if self.pressed:
            face_color, edge_color = COLOR_BTN_DOWN, COLOR_BTN_DOWN
        elif self.selected:
            face_color, edge_color = COLOR_BTN_SELECTED, COLOR_BTN_SELECTED_EDGE
            text_color = COLOR_BTN_TEXT_SELECTED
        elif hover:
            face_color, edge_color = COLOR_BTN_HOVER, COLOR_BTN_EDGE
        else:
            face_color, edge_color = COLOR_BTN, COLOR_BTN_EDGE

        offset = EDGE - 2 if self.pressed else 0
        face = self.rect.move(0, offset)
        edge = self.rect.move(0, EDGE)
        pygame.draw.rect(screen, edge_color, edge, border_radius=8)
        pygame.draw.rect(screen, face_color, face, border_radius=8)
        pygame.draw.rect(screen, COLOR_OUTLINE, face, 3, border_radius=8)
        text_surface = self.font.render(self.text, True, text_color)
        screen.blit(text_surface, text_surface.get_rect(center=face.center))

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((360, 300))
    pygame.display.set_caption("Test Button")
    font = pygame.font.SysFont("arial", 24, bold=True)
    background = make_grass(360, 300)
    btn_one = Button((90, 40, 180, 50), "1 Agent", font)
    btn_two = Button((90, 120, 180, 50), "2 Agents", font)
    btn_exit = Button((90, 200, 180, 50), "Exit", font)
    buttons = [btn_one, btn_two, btn_exit]
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for b in buttons:
                if b.handle_event(event):
                    print("Da bam:", b.text)
                    if b is btn_exit:
                        running = False
        screen.blit(background, (0, 0))
        for b in buttons:
            b.draw(screen)
        pygame.display.flip()
    pygame.quit()