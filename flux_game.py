from drawingpad import pad
from flux_gamebase import Action, GameState
import itertools
import pygame
import random


# Game constants
STAGE_DRAWING_TIMER = 45 * 1000
STAGE_DRAWING_TIMER = 6 * 1000

TIME_BETWEEN_ROUNDS = 5 * 1000
GUESSER_TIME_PENALTY = 7 * 1000

POINTS_GUESSER_CORRECT = 10
POINTS_GUESSER_WRONG = 1
POINTS_DRAWER_CORRECTLY_GUESS = 30
POINTS_DRAWER_TIMEOUT = -20

NUMBER_OF_CHOICES = 10


class Action_Connect(Action):
    packet_name = "CONNECT"

    def run_server(self, GameState):
        id = GameState.addPlayer(self.data["player_name"])
        data = {"id": id}

        GameState.run_action(Action_Connect_Ack(data, target_id=id))
        GameState.run_action(Action_GameState_Sync(target_id=id))
        GameState.run_action(Action_Send_Canvas(target_id=id))

        # Action_Connect is the only packet that returns a value
        return id

class Action_Connect_Ack(Action):
    packet_name = "CONNECT_ACK"
    network_command = True

    def run(self, GameState):
        GameState.player_id = self.data["id"]

class Action_Draw(Action):
    packet_name = "DRAW"
    network_command = True

    def run(self, GameState):
        if not GameState.is_current_active_player():
            # Inactive player can't draw
            self.network_command = False
            return

        GameState.main_pad.update(**self.data)

    def run_server(self, GameState):
        if GameState.active_player != self.source_player_id:
            return

        GameState.main_pad.update(**self.data)
        GameState.run_action(Action_Draw_Broadcast(self.data))

class Action_Draw_Broadcast(Action):
    packet_name = "DRAW_BROADCAST"
    network_command = True

    def run(self, GameState):
        if GameState.is_current_active_player():
            # Ignore. We are the active player
            return

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
        if GameState.timer < 0:
            GameState.run_action(Action_Init_Game())
            GameState.timer = TIME_BETWEEN_ROUNDS

class Action_Init_Game(Action):
    packet_name = "INIT_GAME"
    network_command = True
    data_required = False

    def run_server(self, GameState):
        GameState.initialize_game()
        GameState.run_action(Action_GameState_Sync())

class Action_GameState_Sync(Action):
    packet_name = "GAMESTATE_SYNC"
    network_command = True
    data_required = False

    def run(self, GameState):
        GameState.active_player = self.data["active_player_id"]
        GameState.drawing_answer = self.data["drawing_answer"]
        GameState.choices = self.data["choices"]

    def run_server(self, GameState):
        self.data["active_player_id"] = GameState.active_player
        self.data["drawing_answer"] = GameState.drawing_answer
        self.data["choices"] = GameState.choices


# Future tech: automate the data entry instead of doing it manually
ActionList = {"CONNECT": Action_Connect,
              "CONNECT_ACK": Action_Connect_Ack,
              "DRAW": Action_Draw,
              "DRAW_BROADCAST": Action_Draw_Broadcast,
              "SEND_CANVAS": Action_Send_Canvas,
              "TIME_TICK": Action_Time_Tick,
              "INIT_GAME": Action_Init_Game,
              "GAMESTATE_SYNC": Action_GameState_Sync}

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
        self.choices = []

        self.player_id = None

        # server variables
        self.players = {}
        self.active_player = None

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
        should_initialize = len(self.players) == 0
        new_player = Player(name)
        self.players[new_player.id] = new_player
        print("Added {} with id {}".format(name, new_player.id))

        if should_initialize:
            self.run_action(Action_Init_Game())

        return new_player.id

    def get_player(self, player_id):
        return self.players.get(player_id, None)

    def initialize_game(self):
        self.timer = STAGE_DRAWING_TIMER
        player = random.choice(self.players)
        self.active_player = player.id
        self.drawing_answer = random.choice(possible_drawings)
        self.generate_choices()

        print("")
        print("New active player is: {} ({})".format(player.name, self.active_player))
        print(" drawing: {}".format(self.drawing_answer))

    def generate_choices(self):
        wrong_answers = list(possible_drawings)
        wrong_answers.remove(self.drawing_answer)
        wrong_answers = random.sample(wrong_answers, NUMBER_OF_CHOICES)
        choices = wrong_answers + [self.drawing_answer]
        random.shuffle(choices)

        self.choices = choices

    def is_current_active_player(self):
        return self.active_player == self.player_id