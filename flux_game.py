from drawingpad import pad
from flux_gamebase import Action, GameState
import itertools
import pygame
import random


class Action_Connect(Action):
    packet_name = "CONNECT"

    def run_server(self, GameState):
        id = GameState.addPlayer(self.data["player_name"])
        data = {"id": id}

        GameState.run_action(Action_Connect_Ack(data, target_id=id))
        GameState.run_action(Action_Send_Canvas(target_id=id))
        GameState.run_action(Action_Init_Game(target_id=id))

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
    data_required = False

    def run(self, GameState):
        for draw in self.data["history"]:
            GameState.main_pad.apply_brush(*draw)

    def run_server(self, GameState):
        self.data["history"] = GameState.main_pad.history

class Action_Time_Tick(Action):
    packet_name = "TIME_TICK"
    network_command = True
    data_required = False

    def run(self, GameState):
        if "timer" in self.data:
            GameState.timer = self.data["timer"]

    def run_server(self, GameState):
        self.data["timer"] = GameState.timer

class Action_Init_Game(Action):
    packet_name = "INIT_GAME"
    network_command = True
    data_required = False

    def run(self, GameState):
        GameState.drawing_answer = self.data["drawing_answer"]

    def run_server(self, GameState):
        self.data["drawing_answer"] = GameState.drawing_answer


# Future tech: automate the data entry instead of doing it manually
ActionList = {"CONNECT": Action_Connect,
              "CONNECT_ACK": Action_Connect_Ack,
              "DRAW": Action_Draw,
              "DRAW_BROADCAST": Action_Draw_Broadcast,
              "SEND_CANVAS": Action_Send_Canvas,
              "TIME_TICK": Action_Time_Tick,
              "INIT_GAME": Action_Init_Game}

possible_drawings = [answer
                     for answer in open("answers.txt").read().split("\n")
                     if len(answer) > 2]


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
        self.network_message = None
        self.points = 0
        self.timer = 5 * 60 * 1000

        self.drawing_answer = None
        self.generate_answer()

        self.player_id = None

        # server variables
        self.players = {}

    def update(self):
        super(DrawGame, self).update()
        self.timer -= self.clock.get_time()

        self.run_action(Action_Time_Tick())

        self.update_messages()

    def update_messages(self):
        messages = []

        if not self.network_message:
            message = ("Your drawing should be: \"{}\""
                       .format(self.drawing_answer))
            messages.append(message)
        else:
            messages.append(self.network_message)

        total_seconds = self.timer / 1000
        minutes = int(total_seconds / 60)
        seconds = int(total_seconds % 60)
        messages.append("Time left: {}:{:02d}".format(minutes, seconds))

        if self.timer <= 0:
            messages.append("Waiting for server...")

        self.messages = messages

    def draw(self, screen):
        pass

    def addPlayer(self, name):
        new_player = Player(name)
        self.players[new_player.id] = new_player
        print("Added {} with id {}".format(name, new_player.id))

        return new_player.id

    def get_player(self, player_id):
        return self.players.get(player_id, None)

    def generate_answer(self):
        self.drawing_answer = random.choice(possible_drawings)