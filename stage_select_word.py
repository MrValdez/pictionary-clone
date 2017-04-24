from drawingpad import pad
from stage_base import Stage
import packets
import pygame


class SelectWord(Stage):
    def __init__(self, network_client):
        super(SelectWord, self).__init__()

        self.main_pad = pad([220, 40], scale=1.3)

        self.client = network_client
        self.player_answers = []
        self.current_player_to_test = 0

    def draw(self, screen):
        screen.fill([255, 255, 255])

        self.draw_answers(screen)
        self.main_pad.draw(screen)

        self.draw_messages(screen, pos_y=600)

    def draw_answers(self, screen):
        if self.current_player_to_test >= len(self.player_answers):
            return

        self.messages = []
        answers, draw_commands = self.player_answers[self.current_player_to_test]

        for answer in answers:
            self.messages.append(answer)

        for draw_command in draw_commands:
            mouse_down, pos = draw_command
            self.main_pad(mouse_down, pos)

    def update_select_answer_stage(self, data):
        while data is None:
            # wait for the next broadcast
            data = self.client.update_client_commands()
        self.player_answers = data

    def update_broadcast_commands(self, packet, data):
        if packet == packets.SELECT_ANSWER_INFO:
            self.update_select_answer_stage(data)

    def update_server_commands(self, data):
        pass

    def update(self, clock):
        pass
