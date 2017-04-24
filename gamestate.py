from collections import OrderedDict
import pygame
import packets
import random
import string

# Game stages
STAGE_DRAWING = 1
STAGE_SELECT_ANSWER = 2

# Game constants
STAGE_DRAWING_TIMER = 60 * 1000
STAGE_DRAWING_TIMER = 1 * 1000
STAGE_DRAWING_TIMER = 10 * 1000

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
        self.drawing_answer = random.choice(possible_drawings)


class GameState:
    def __init__(self):
        self.current_stage = STAGE_DRAWING
        self.players = {}
        self.clock = pygame.time.Clock()

    def addPlayer(self, name):
        newPlayer = Player(name)
        self.players[newPlayer.id] = newPlayer

        print("Added new player ({}) with id {}".format(newPlayer.name,
                                                        newPlayer.id))
        print(" their drawing should be: {}".format(newPlayer.drawing_answer))
        return newPlayer

    def change_stage(self, newStage):
        self.current_stage = newStage


class Room(GameState):
    def __init__(self, server):
        super(Room, self).__init__()
        self.id = 1
        self.server = server
        self.time_remaining = STAGE_DRAWING_TIMER

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
        self.server.send_broadcast(self.id, packets.DRAW, data)

    def change_stage(self, newStage):
        if (self.current_stage == STAGE_DRAWING and
           newStage == STAGE_SELECT_ANSWER):
            # transitioning from stage_drawing to stage_select_answer
            self.broadcast_change_to_stage_select_answer()
        else:
            # there is no stage transition. do not call super
            return

#debug comment
        super(Room, self).change_stage(newStage)

    def broadcast_change_to_stage_select_answer(self):
        players = OrderedDict(self.players).values()    # force consistency

        all_choices = []
        all_drawings = []

        for player in players:
            wrong_answers = list(possible_drawings)
            wrong_answers.remove(player.drawing_answer)
            wrong_answers = random.sample(wrong_answers, 3)
            choices = wrong_answers + [player.drawing_answer]
            random.shuffle(choices)

            all_choices.append(choices)
            all_drawings.append(player.history)

        data = zip(all_choices, all_drawings)

        self.server.send_broadcast(self.id,
                                   packets.SELECT_ANSWER_INFO,
                                   data)

    def update(self):
        self.clock.tick()

        self.time_remaining -= self.clock.get_time()
        if self.time_remaining <= 0:
            self.change_stage(STAGE_SELECT_ANSWER)
