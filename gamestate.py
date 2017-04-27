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

        self.status = PLAYER_STATUS_GUESSER
        self.points = 0


class GameState:
    def __init__(self, network_conn):
        self.current_stage = STAGE_DRAWING
        self.players = {}
        self.activeDrawer = None
        self.currentAnswer = random.choice(possible_drawings)
        self.choices = []
        self.number_of_choices = 15
        self.correct_answer_index = 0
        self.generate_choices()

        self.clock = pygame.time.Clock()
        self.conn = network_conn

    def addPlayer(self, name):
        newPlayer = Player(name)
        self.players[newPlayer.id] = newPlayer

        print("Added new player ({}) with id {}".format(newPlayer.name,
                                                        newPlayer.id))

        if self.activeDrawer is None:
            self.activeDrawer = newPlayer
            newPlayer.status = PLAYER_STATUS_DRAWER

        return newPlayer

    def getPlayer(self, id):
        for player_id, player in self.players.items():
            if player_id == id:
                return player
        return None

    def generate_choices(self):
        wrong_answers = list(possible_drawings)
        wrong_answers.remove(self.currentAnswer)
        wrong_answers = random.sample(wrong_answers, self.number_of_choices)
        choices = wrong_answers + [self.currentAnswer]
        random.shuffle(choices)

        self.correct_answer_index = choices.index(self.currentAnswer)
        self.choices = choices

        print("Current drawing should be: {}".format(self.currentAnswer))
        print("Choices are: {}".format(self.choices))
        print(self.correct_answer_index)


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

    def update(self):
        self.clock.tick()

        self.time_remaining -= self.clock.get_time()
        if self.time_remaining <= 0:
            self.change_active_drawer()

    def change_active_drawer(self):
        pass

    def update_network(self, packet, data):
        if packet == packets.CONNECT:
            print("New client connected")

            name = data[0]
            newPlayer = self.addPlayer(name)

            data = packets.CONNECT_data.copy()
            data["Player number"] = newPlayer.number
            data["Player name"] = newPlayer.name
            data["Player ID"] = newPlayer.id
            data["Drawing answer"] = self.currentAnswer

            self.conn.client_conn.send_json(data)

        elif packet == packets.ACK_CONNECT:
            print("Sending stage info")
            self.send_player_stage_info(data)

        elif packet == packets.DRAW:
            self.conn.client_conn.send_json(packets.ACK)

            player_id = data[0]
            mouse_down, pos = data[1]
            self.update_history(player_id, mouse_down, pos)

        elif packet == packets.SEND_ANSWER:
            playerID = data[0]
            question_idx = data[1]
            player = self.getPlayer(playerID)
            if player is None:
                return

            is_correct = question_idx == self.correct_answer_index

            to_send = packets.RESULTS_data.copy()
            if is_correct:
                player.points += 10
                to_send["Message"] = "You are correct"
            else:
                player.points -= 10
                to_send["Message"] = "You are wrong. You get penalty."

            to_send["Current points"] = player.points
            to_send["Time remaining"] = 50
            self.conn.client_conn.send_json([packets.RESULTS, to_send])

    def send_player_stage_info(self, data):
        player_id = data[0]
        player = self.getPlayer(player_id)

        # figure out if player is guesser or drawer.
        if player.status == PLAYER_STATUS_DRAWER:
            packet_id = packets.DRAWING_INFO
            data = packets.DRAWING_INFO_data.copy()
            data["Drawing answer"] = self.currentAnswer

        elif player.status == PLAYER_STATUS_GUESSER:
            packet_id = packets.GUESS_INFO
            data = packets.GUESS_INFO_data.copy()
            data["Choices"] = self.choices
            data["Drawing"] = self.activeDrawer.history

        data["Time remaining"] = self.time_remaining
        self.conn.client_conn.send_json([packet_id, data])
