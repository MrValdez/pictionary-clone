from drawingpad import pad
from flux_gamebase import Action, GameState
import itertools
import pygame


class Action_Connect(Action):
    packet_name = "CONNECT"

    def run_server(self, GameState):
        id = GameState.addPlayer(self.data["player_name"])
        data = {"id": id}

        GameState.run_action(Action_Connect_Ack(data, target_id=id))
        GameState.run_action(Action_Send_Canvas({}, target_id=id))

        # Action_Connect is the only packet that returns a value
        return id

class Action_Connect_Ack(Action):
    packet_name = "CONNECT_ACK"
    network_command = True

class Action_Draw(Action):
    packet_name = "DRAW"
    network_command = True

    def run(self, GameState):
        GameState.main_pad.update(**self.data)

    def run_server(self, GameState):
        GameState.main_pad.update(**self.data)
        GameState.run_action(Action_Draw_Broadcast(self.data))

class Action_Draw_Broadcast(Action):
    packet_name = "DRAW_BROADCAST"
    network_command = True

    def run(self, GameState):
        GameState.main_pad.update(**self.data)

class Action_Send_Canvas(Action):
    packet_name = "SEND_CANVAS"
    network_command = True

    def run(self, GameState):
        for draw in self.data["history"]:
            GameState.main_pad.apply_brush(*draw)

    def run_server(self, GameState):
        self.data["history"] = GameState.main_pad.history

# Future tech: automate the data entry instead of doing it manually
ActionList = {"CONNECT": Action_Connect,
              "CONNECT_ACK": Action_Connect_Ack,
              "DRAW": Action_Draw,
              "DRAW_BROADCAST": Action_Draw_Broadcast,
              "SEND_CANVAS": Action_Send_Canvas}


class Player:
    unique_id = itertools.count()

    def __init__(self, name):
        self.name = name
        self.message_queue = []

        self.id = next(self.unique_id)

class DrawGame(GameState):
    def __init__(self):
        super(DrawGame, self).__init__()

        self.main_pad = pad([250, 40], network_connection=None)
        self.messages = []
        self.points = 0
        self.clock = pygame.time.Clock()

        self.player_id = None

        # server variables
        self.players = {}

    def update(self):
        self.clock.tick(60)

    def draw(self, screen):
        pass

    def addPlayer(self, name):
        new_player = Player(name)
        self.players[new_player.id] = new_player
        print("Added {} with id {}".format(name, new_player.id))

        return new_player.id

    def get_player(self, player_id):
        return self.players.get(player_id, None)