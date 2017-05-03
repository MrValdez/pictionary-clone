from drawingpad import pad
from flux_gamebase import Action, GameState
import pygame


class Action_Connect(Action):
    packet_name = "CONNECT"

    def __init__(self, player_name):
        data = {"player_name": player_name}
        super(Action_Connect, self).__init__(data)

    def run(self, GameState):
        GameState.addPlayer(self.Name)

class Action_Draw(Action):
    packet_name = "DRAW"

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

    def addPlayer(self, name):
        self.name = name
        print("Added " + name)