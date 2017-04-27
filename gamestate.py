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
STAGE_DRAWING_TIMER = 45 * 1000
#STAGE_DRAWING_TIMER = 6 * 1000

TIME_BETWEEN_ROUNDS = 5 * 1000
GUESSER_TIME_PENALTY = 15 * 1000

POINTS_GUESSER_CORRECT = 10
POINTS_GUESSER_WRONG = 1
POINTS_DRAWER_CORRECTLY_GUESS = 30
POINTS_DRAWER_TIMEOUT = -20

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
        self.timer = 0


class GameState:
    def __init__(self, network_conn):
        self.current_stage = STAGE_DRAWING
        self.players = {}
        self.activeDrawer = None
        self.currentAnswer = ""
        self.choices = []
        self.number_of_choices = 15
        self.correct_answer_index = 0

        self.clock = pygame.time.Clock()
        self.conn = network_conn
        self.timer_to_next_round = 0
        self.start_transition_to_next_round = False

    def addPlayer(self, name):
        newPlayer = Player(name)
        self.players[newPlayer.id] = newPlayer

        print("Added new player ({}) with id {}".format(newPlayer.name,
                                                        newPlayer.id))

        if self.activeDrawer is None:
            self.change_active_drawer(broadcast_to_network=False)

        return newPlayer

    def getPlayer(self, id):
        for player_id, player in self.players.items():
            if player_id == id:
                return player
        return None

    def generate_choices(self):
        self.currentAnswer = random.choice(possible_drawings)

        wrong_answers = list(possible_drawings)
        wrong_answers.remove(self.currentAnswer)
        wrong_answers = random.sample(wrong_answers, self.number_of_choices)
        choices = wrong_answers + [self.currentAnswer]
        random.shuffle(choices)

        self.correct_answer_index = choices.index(self.currentAnswer)
        self.choices = choices

        print("Current drawing should be: {}".format(self.currentAnswer))

    def change_active_drawer(self, broadcast_to_network=True):
        if not len(self.players):
            # no players in room
            return

        print("\nStarting next round")

        self.generate_choices()
        self.time_remaining = STAGE_DRAWING_TIMER
        self.start_transition_to_next_round = False

        for player in self.players.values():
            player.status = PLAYER_STATUS_GUESSER
            player.history = []

        self.activeDrawer = random.choice(list(self.players.values()))
        self.activeDrawer.status = PLAYER_STATUS_DRAWER
        print("Next drawer is " + self.activeDrawer.name)

        self.conn.send_broadcast(self.id, packets.REQUEST_NEXT_STAGE, [])


class Room(GameState):
    def __init__(self, network_conn):
        super(Room, self).__init__(network_conn)
        self.id = 1
        self.time_remaining = 0
        self.all_correct_answers = []
        self.winner_name = ""

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

        timer = self.clock.get_time()

        self.time_remaining -= timer
        self.timer_to_next_round -= timer

        if (self.activeDrawer and self.time_remaining < 0 and
           not self.start_transition_to_next_round):
            # Penalty for active drawer for letting time run out
            self.activeDrawer.points += POINTS_DRAWER_TIMEOUT

            # No winner
            self.announce_winner(None)

        if (self.start_transition_to_next_round and
           self.timer_to_next_round < 0):
            self.change_active_drawer()

        for player in self.players.values():
            player.timer -= timer

        if self.time_remaining % 3 == 0:
            # broadcast current time every 3 seconds
            self.conn.send_broadcast(self.id, packets.TIME, [self.time_remaining])

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
            player_id = data[0]
            self.send_player_stage_info(player_id)

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

            if player.timer > 0:
                # player is under penalty time
                # ignore their guess
                self.conn.client_conn.send_json([packets.ACK])
                return

            is_correct = question_idx == self.correct_answer_index

            to_send = packets.RESULTS_data.copy()
            if is_correct:
                player.points += POINTS_GUESSER_CORRECT
                self.activeDrawer.points += POINTS_DRAWER_CORRECTLY_GUESS
                to_send["Message"] = "You are correct"
            else:
                player.points += POINTS_GUESSER_WRONG
                player.timer = GUESSER_TIME_PENALTY

                total_seconds = player.timer / 1000
                minutes = int(total_seconds / 60)
                seconds = int(total_seconds % 60)

                message = "You are wrong. You cannot answer for "
                if minutes:
                    message += "{}:{} minutes".format(minutes, seconds)
                else:
                    message += "{} seconds".format(seconds)
                to_send["Message"] = message

            to_send["Current points"] = player.points
            to_send["Time remaining"] = GUESSER_TIME_PENALTY
            self.conn.client_conn.send_json([packets.RESULTS, to_send])

            if is_correct:
                self.announce_winner(player)

        elif packet == packets.REQUEST_RESULTS:
            playerID = data[0]
            player = self.getPlayer(playerID)
            if player is None:
                return

            if self.winner_name:
                win_quote = "{} got the correct answer! You get points!"
                message = win_quote.format(self.winner_name)
            else:
                message = "No one got the answer. The correct answer is: {}"
                message = message.format(self.currentAnswer)

            to_send = packets.RESULTS_data.copy()
            to_send["Current points"] = player.points
            to_send["Next round timer"] = self.timer_to_next_round
            to_send["Message"] = message
            self.conn.client_conn.send_json([packets.RESULTS, to_send])

    def send_player_stage_info(self, player_id):
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

        data["Player points"] = player.points
        data["Time remaining"] = self.time_remaining
        self.conn.client_conn.send_json([packet_id, data])

    def announce_winner(self, player):
        if player:
            self.winner_name = player.name
        else:
            self.winner_name = None

        self.conn.send_broadcast(self.id, packets.ANSWER_FOUND, [])

        self.timer_to_next_round = TIME_BETWEEN_ROUNDS
        self.start_transition_to_next_round = True
