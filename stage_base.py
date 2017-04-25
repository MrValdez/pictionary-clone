import pygame


class Stage:
    def __init__(self):
        self.NormalText = pygame.font.Font(None, 25)
        self.messages = []

    def draw(self, screen):
        pass

    def update_broadcast_commands(self, packet, data):
        pass

    def update_server_commands(self, data):
        pass

    def update(self, clock, prev_mouse_down, mouse_down, mouse_pos):
        pass

    def draw_messages(self, screen, pos_y):
        for message in self.messages:
            output = self.NormalText.render(message, True, [0, 0, 0])
            screen.blit(output, [40, pos_y])
            pos_y += output.get_height() + 10
