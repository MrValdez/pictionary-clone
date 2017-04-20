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


class GameState:
    def __init__(self):
        self.current_stage = Stage1
        self.players = []

    def addPlayer(self, name):
        newPlayer = Player(name)
        self.players.append(newPlayer)

        print("Added new player ({}) with id {}".format(newPlayer.name,
                                                        newPlayer.id))
        return newPlayer

class Room(GameState):
    def __init__(self):
        super(Room, self).__init__()
        self.id = 1