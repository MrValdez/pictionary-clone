from collections import OrderedDict
import json
import pygame
import packets
import random
import string
import zmq

# Player status
PLAYER_STATUS_DRAWER = 0
PLAYER_STATUS_GUESSER = 1

# Game stages
STAGE_DRAWING = 1
STAGE_SELECT_ANSWER = 2

# Game constants
STAGE_DRAWING_TIMER = 60 * 1000
STAGE_DRAWING_TIMER = (124 * 1000)
#STAGE_DRAWING_TIMER = 1 * 1000
#STAGE_DRAWING_TIMER = 15 * 1000

possible_drawings = [answer
                     for answer in open("answers.txt").read().split("\n")
                     if len(answer) > 2]


class Player:
    current_player_number = 0

    def __init__(self, name):
        self.name = name
        self.id = "".join([random.choice(string.ascii_lowercase)
                           for i in range(5)])
        self.history = []
        self.number = Player.current_player_number
        Player.current_player_number += 1

        self.status = PLAYER_STATUS_DRAWER
        self.drawing_answer = random.choice(possible_drawings)


class GameState:
    def __init__(self, network_conn):
        self.current_stage = STAGE_DRAWING
        self.players = {}
        self.clock = pygame.time.Clock()
        self.conn = network_conn

    def addPlayer(self, name):
        newPlayer = Player(name)
        self.players[newPlayer.id] = newPlayer

        print("Added new player ({}) with id {}".format(newPlayer.name,
                                                        newPlayer.id))
        print(" their drawing should be: {}".format(newPlayer.drawing_answer))
        return newPlayer

    def getPlayer(self, id):
        for player_id, player in self.players.items():
            if player_id == id:
                return player
        return None

    def change_stage(self, newStage):
        self.current_stage = newStage

class Room(GameState):
    def __init__(self, network_conn):
        super(Room, self).__init__(network_conn)
        self.id = 1
        self.time_remaining = STAGE_DRAWING_TIMER
        self.all_correct_answers = []
        self.active_drawing_player = 0

    def update_history(self, player_id, mouse_down, pos):
        if player_id not in self.players:
            print("Invalid player_id sent")
            print(" Sent: {}".format(player_id))
            current_players = list(self.players.keys())
            print(" Currently registered: {}".format(current_players))

        history_data = [mouse_down, pos]

        player = self.players[player_id]
        player.history.append(history_data)

        data = [player.number, *history_data]
        self.conn.send_broadcast(self.id, packets.DRAW, data)

    def change_stage(self, newStage):
        if (self.current_stage == STAGE_DRAWING and
           newStage == STAGE_SELECT_ANSWER):
            # transitioning from stage_drawing to stage_select_answer
            self.broadcast_change_to_stage_select_answer()
        else:
            # there is no stage transition. do not call super
            return

        super(Room, self).change_stage(newStage)

    def broadcast_change_to_stage_select_answer(self):
        players = OrderedDict(self.players).values()    # force consistency

        all_choices = []
        all_drawings = []
        all_correct_answers = []

        for player in players:
            wrong_answers = list(possible_drawings)
            wrong_answers.remove(player.drawing_answer)
            wrong_answers = random.sample(wrong_answers, 3)
            choices = wrong_answers + [player.drawing_answer]
            random.shuffle(choices)

            all_choices.append(choices)
            all_drawings.append(player.history)
            all_correct_answers.append(player.drawing_answer)

        data = zip(all_choices, all_drawings)

        self.conn.send_broadcast(self.id,
                                   packets.SELECT_ANSWER_INFO,
                                   data)
        self.all_correct_answers = all_correct_answers

    def update(self):
        self.clock.tick()

        self.time_remaining -= self.clock.get_time()
        if self.time_remaining <= 0:
            self.change_stage(STAGE_SELECT_ANSWER)

    def update_network(self, packet, data):
        if packet == packets.CONNECT:
            print("New client connected")

            name = data[0]
            newPlayer = self.addPlayer(name)

            data = packets.CONNECT_data.copy()
            data["Player number"] = newPlayer.number
            data["Player name"] = newPlayer.name
            data["Player ID"] = newPlayer.id
            data["Drawing answer"] = newPlayer.drawing_answer

            self.conn.client_conn.send_json(data)

        if packet == packets.ACK_CONNECT:
            self.send_player_stage_info(data)
        if packet == packets.DRAW:
            self.conn.client_conn.send_json(packets.ACK)

            player_id = data[0]
            mouse_down, pos = data[1]
            self.update_history(player_id, mouse_down, pos)

        if packet == packets.SEND_ANSWER:
            playerID = data[0]
            question_idx, player_choice = data[1]

            to_send = packets.SEND_CORRECT_ANSWER_data.copy()
            to_send["Correct Answer"] = self.all_correct_answers[question_idx]
            self.conn.client_conn.send_json(to_send)

    def send_player_stage_info(self, data):
        player_id = data[0]
        player = self.getPlayer(player_id)

        # figure out if player is guesser or drawer.
        if player.status == PLAYER_STATUS_DRAWER:
            packet_id = packets.DRAWING_INFO
            data = packets.DRAWING_INFO_data.copy()
            data["Drawing answer"] = player.drawing_answer

        elif player.status == PLAYER_STATUS_GUESSER:
            packet_id = packets.GUESS_INFO
            data = packets.GUESS_INFO_data.copy()
            data["Choices"] = ["a", "b"]
            data["Drawing"] = activePlayer.history

        data["Time remaining"] = self.time_remaining
        self.conn.client_conn.send_json([packet_id, data])
