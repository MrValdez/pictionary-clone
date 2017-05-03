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
        self.messages = []
        self.points = 0
        self.clock = pygame.time.Clock()

    def update(self):
        self.clock.tick(60)

    def draw(self, screen):
        pass