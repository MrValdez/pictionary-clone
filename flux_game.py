from drawingpad import pad
import pygame


class Action:
    def __init__(self):
        pass

    def run(self, GameState):
        pass

class GameState:
    """
    This is the store in the Flux architecture
    """
    def __init__(self):
        self.NormalText = pygame.font.Font(None, 25)
        self.messages = []
        self.ui_points_pos = [970, 700]

    def attach_engine(self, engine):
        self.engine = engine

    def update(self):
        pass

    def draw(self, screen):
        pass

    def draw_messages(self, screen, pos_y):
        for message in self.messages:
            output = self.NormalText.render(message, True, [0, 0, 0])
            screen.blit(output, [40, pos_y])
            pos_y += output.get_height() + 10

class DrawGame(GameState):
    def __init__(self):
        super(DrawGame, self).__init__()

        self.main_pad = pad([250, 40], network_connection=None)
        self.points = 0

    def update(self):
        pass

    def draw(self, screen):
        screen.fill([255, 255, 255])

        self.main_pad.draw(screen)

        self.draw_messages(screen, pos_y=600)
        self.draw_points(screen)

    def draw_points(self, screen):
        points_text = self.NormalText.render(
            "{} pts".format(self.points), True, [0, 0, 0])
        pygame.draw.circle(screen,
                           [255, 128, 128],
                           self.ui_points_pos,
                           points_text.get_width() + 10)
        points_pos = points_text.get_rect()
        points_pos.center = self.ui_points_pos
        screen.blit(points_text,  points_pos)
