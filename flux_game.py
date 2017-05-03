from drawingpad import pad
from flux_gamebase import Action, GameState
import pygame


class Action_Draw(Action):
    def run(self, GameState):
        GameState.main_pad.update(**self.data)

class DrawGame(GameState):
    def __init__(self):
        super(DrawGame, self).__init__()

        self.main_pad = pad([250, 40], network_connection=None)
        self.points = 0
        self.clock = pygame.time.Clock()

    def update(self):
        self.clock.tick(60)

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
