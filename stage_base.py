import pygame


class Stage:
    def __init__(self):
        self.NormalText = pygame.font.Font(None, 25)
        self.messages = []

        self.points = 0
        #self.ui_points_pos = [30, 20]
        self.ui_points_pos = [970, 700]

    def draw(self, screen):
        pass

    def update_broadcast_commands(self, packet, data):
        pass

    def update_server_commands(self, packet, data):
        pass

    def update(self, clock, prev_mouse_down, mouse_down, mouse_pos):
        pass

    def draw_messages(self, screen, pos_y):
        for message in self.messages:
            output = self.NormalText.render(message, True, [0, 0, 0])
            screen.blit(output, [40, pos_y])
            pos_y += output.get_height() + 10

        points_text = self.NormalText.render(
            "{} pts".format(self.points), True, [0, 0, 0])
        pygame.draw.circle(screen,
                           [255, 128, 128],
                           self.ui_points_pos,
                           points_text.get_width() + 10)
        points_pos = points_text.get_rect()
        points_pos.center = self.ui_points_pos
        screen.blit(points_text,  points_pos)
