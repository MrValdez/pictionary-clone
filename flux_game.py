from drawingpad import pad
from flux_gamebase import Action, GameState
import itertools
import pygame
import random


# Game constants
STAGE_DRAWING_TIMER = 45 * 1000
#STAGE_DRAWING_TIMER = 6 * 1000

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
        GameState.main_pad.update(**self.data)

class Action_Send_Canvas(Action):
    packet_name = "SEND_CANVAS"
    network_command = True
    data_required = False

    def run(self, GameState):
        GameState.main_pad.clear()
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
        GameState.network_message = ""
        GameState.main_pad.clear()

    def run_server(self, GameState):
        self.data["active_player_id"] = GameState.active_player
        self.data["drawing_answer"] = GameState.drawing_answer
        self.data["choices"] = GameState.choices

class Action_SendAnswer(Action):
    packet_name = "SEND_ANSWER"
    network_command = True
    data_required = False

    def run_server(self, GameState):
        player = GameState.get_player(self.source_player_id)
        if player.lockdown_timer > 0:
            message = "Player \"{}\" tried to cheat by sending an answer during lockdown"
            message = message.format(player.name)
            print(message)
            return

        is_correct = self.data["answer"] == GameState.correct_answer_index

        if is_correct:
            data = {"winner_id": self.source_player_id,
                    "points": POINTS_GUESSER_CORRECT}
            action = Action_CorrectAnswer(data,
                                          target_id=self.source_player_id)
        else:
            data = {"lockdown_time": GUESSER_TIME_PENALTY,
                    "points": POINTS_GUESSER_WRONG}
            action = Action_WrongAnswer(data,
                                        target_id=self.source_player_id)
            player.lockdown_timer = GUESSER_TIME_PENALTY

        GameState.run_action(action)

class Action_WrongAnswer(Action):
    packet_name = "WRONG_ANSWER"
    network_command = True

    def run(self, GameState):
        GameState.lockdown_timer = self.data["lockdown_time"]
        message = "Wrong answer. You are on lockdown. You get {} points"
        message = message.format(self.data["points"])
        GameState.network_message = message

    def run_server(self, GameState):
        data = {"id": self.target_id,
                "points_delta": POINTS_GUESSER_WRONG}
        action = Action_Update_Points(data)
        GameState.run_action(action)

class Action_CorrectAnswer(Action):
    packet_name = "CORRECT_ANSWER"
    network_command = True

    def run(self, GameState):
        message = "CORRECT ANSWER! You get {} points"
        message = message.format(self.data["points"])
        GameState.network_message = message

    def run_server(self, GameState):
        winning_player = GameState.get_player(self.data["winner_id"])
        drawing_player = GameState.get_player(GameState.active_player)

        # send the player how many points they receive
        self.data["points"] = POINTS_GUESSER_CORRECT

        data = {"winner_name": winning_player.name,
                "drawer_name": drawing_player.name,
                "answer": GameState.drawing_answer,
                "wait_time": TIME_BETWEEN_ROUNDS,
                "drawer_points": POINTS_DRAWER_CORRECTLY_GUESS}

        for player in GameState.players.values():
            if player == winning_player:
                continue

            action = Action_CorrectAnswerBroadcast(data,
                                                   target_id=player.id)
            GameState.run_action(action)

        GameState.timer = TIME_BETWEEN_ROUNDS

        # update points for drawer and winning guesser
        data = {"id": self.target_id,
                "points_delta": POINTS_GUESSER_CORRECT}
        action = Action_Update_Points(data)
        GameState.run_action(action)

        data = {"id": drawing_player.id,
                "points_delta": POINTS_DRAWER_CORRECTLY_GUESS}
        action = Action_Update_Points(data)
        GameState.run_action(action)

class Action_CorrectAnswerBroadcast(Action):
    packet_name = "CORRECT_ANSWER_BROADCAST"
    network_command = True
    data_required = False

    def run(self, GameState):
        message = "{} have found the answer! The correct answer is \"{}.\" "
        message = message.format(self.data["winner_name"],
                                 self.data["answer"])
        message += "{} gets {} points."
        message = message.format(self.data["drawer_name"],
                                 self.data["drawer_points"])
        GameState.network_message = message
        GameState.timer = self.data["wait_time"]

class Action_Update_Points(Action):
    packet_name = "UPDATE_POINTS"
    network_command = True
    data_required = False

    def run(self, GameState):
        GameState.points = self.data["points"]

    def run_server(self, GameState):
        player = GameState.get_player(self.data["id"])
        player.points += self.data["points_delta"]

        self.data = {"points": player.points}
        self.target_id = player.id

# Future tech: automate the data entry instead of doing it manually
ActionList = {"CONNECT": Action_Connect,
              "CONNECT_ACK": Action_Connect_Ack,
              "DRAW": Action_Draw,
              "DRAW_BROADCAST": Action_Draw_Broadcast,
              "SEND_CANVAS": Action_Send_Canvas,
              "TIME_TICK": Action_Time_Tick,
              "INIT_GAME": Action_Init_Game,
              "GAMESTATE_SYNC": Action_GameState_Sync,
              "SEND_ANSWER": Action_SendAnswer,
              "WRONG_ANSWER": Action_WrongAnswer,
              "CORRECT_ANSWER": Action_CorrectAnswer,
              "CORRECT_ANSWER_BROADCAST": Action_CorrectAnswerBroadcast,
              "UPDATE_POINTS": Action_Update_Points}

possible_drawings = [answer
                     for answer in open("answers.txt").read().split("\n")
                     if len(answer) > 2]


class Player:
    unique_id = itertools.count()

    def __init__(self, name):
        self.name = name
        self.message_queue = []

        self.id = next(self.unique_id)
        self.lockdown_timer = 0
        self.points = 0

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
        self.correct_answer_index = 0

        self.player_id = None
        self.lockdown_timer = 0

        # server variables
        self.players = {}
        self.active_player = None

    def update(self):
        super(DrawGame, self).update()

        self.update_timers()
        self.update_messages()

    def update_timers(self):
        time = self.clock.get_time()
        self.timer -= time
        if self.lockdown_timer > 0:
            self.lockdown_timer -= time
            if self.lockdown_timer < 0:
                self.network_message = ""

        # server ticks
        for player in self.players.values():
            player.lockdown_timer -= time
            
        self.run_action(Action_Time_Tick())

    def update_messages(self):
        messages = []

        if not self.network_message:
            if self.is_current_active_player():
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

        self.main_pad.clear()
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
        self.correct_answer_index = choices.index(self.drawing_answer)

    def is_current_active_player(self):
        return self.active_player == self.player_id