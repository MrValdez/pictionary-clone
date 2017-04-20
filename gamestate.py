import random
import string

# Game stages
Stage1 = 1
Stage2 = 2
Stage3 = 3


class Player:
    def __init__(self, name):
        self.name = name
        self.id = "".join([random.choice(string.ascii_lowercase)
                           for i in range(5)])
        self.history = []


class GameState:
    def __init__(self):
        self.current_stage = Stage1
        self.players = {}

    def addPlayer(self, name):
        newPlayer = Player(name)
        self.players[newPlayer.id] = newPlayer

        print("Added new player ({}) with id {}".format(newPlayer.name,
                                                        newPlayer.id))
        return newPlayer

class Room(GameState):
    def __init__(self, server):
        super(Room, self).__init__()
        self.id = 1
        self.server = server

    def update_history(self, player_id, mouse_down, pos):
        if player_id not in self.players:
            print("Invalid player_id sent")
            print(" Sent: {}".format(player_id))
            print(" Currently registered: {}".format(list(self.players.keys())))

        data = [mouse_down, pos]
        self.players[player_id].history.append(data)

        self.server.send_broadcast(self.id, player_id, data)