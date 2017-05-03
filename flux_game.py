from drawingpad import pad
from flux_gamebase import Action, GameState
import pygame


class Action_Connect(Action):
    packet_name = "CONNECT"

    def run_server(self, GameState):
        GameState.addPlayer(self.data["player_name"])

class Action_Draw(Action):
    packet_name = "DRAW"
    network_command = True

    def run(self, GameState):
        GameState.main_pad.update(**self.data)

    def run_server(self, GameState):
        GameState.main_pad.update(**self.data)
        GameState.engine.apply(Action_Draw_Broadcast(self.data))

class Action_Draw_Broadcast(Action):
    packet_name = "DRAW_BROADCAST"
    network_command = True

    def run(self, GameState):
        GameState.main_pad.update(**self.data)

# Future tech: automate the data entry instead of doing it manually
ActionList = {"CONNECT": Action_Connect,
              "DRAW": Action_Draw,
              "DRAW_BROADCAST": Action_Draw_Broadcast}


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
        print("Added {}".format(name))