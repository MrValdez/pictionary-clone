import pygame
import random
import string

# Game stages
Stage1 = 1
Stage2 = 2
Stage3 = 3

# Game constants
STAGE1_TIMER = 60 * 1000
STAGE1_TIMER = 15 * 1000


class Player:
    current_player_number = 0
    possible_drawings = [answer
                         for answer in open("answers.txt").read().split("\n")
                         if len(answer) > 2]

    def __init__(self, name):
        self.name = name
        self.id = "".join([random.choice(string.ascii_lowercase)
                           for i in range(5)])
        self.history = []
        self.number = Player.current_player_number
        Player.current_player_number += 1
        self.drawing_answer = random.choice(self.possible_drawings)

class GameState:
    def __init__(self):
        self.current_stage = Stage1
        self.players = {}
        self.clock = pygame.time.Clock()

    def addPlayer(self, name):
        newPlayer = Player(name)
        self.players[newPlayer.id] = newPlayer

        print("Added new player ({}) with id {}".format(newPlayer.name,
                                                        newPlayer.id))
        print(" their drawing should be: {}".format(newPlayer.drawing_answer))
        return newPlayer


class Room(GameState):
    def __init__(self, server):
        super(Room, self).__init__()
        self.id = 1
        self.server = server
        self.time_remaining = STAGE1_TIMER

    def update_history(self, player_id, mouse_down, pos):
        if player_id not in self.players:
            print("Invalid player_id sent")
            print(" Sent: {}".format(player_id))
            current_players = list(self.players.keys())
            print(" Currently registered: {}".format(current_players))

        data = [mouse_down, pos]
        player = self.players[player_id]
        player.history.append(data)

        self.server.send_broadcast(self.id, player, data)

    def update(self):
        self.clock.tick()

        self.time_remaining -= self.clock.get_time()
