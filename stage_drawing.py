from drawingpad import pad
from stage_base import Stage
import packets
import pygame


class Drawing(Stage):
    def __init__(self, network_client):
        super(Drawing, self).__init__()

        self.client = network_client

        self.timer = 0

        self.main_pad = pad([40, 40], network_connection=network_client)
        self.p2_pad = pad([700, 40], scale=.45)
        self.p3_pad = pad([700, 300], scale=.45)

    def draw(self, screen):
        screen.fill([255, 255, 255])

        self.main_pad.draw(screen)
        self.p2_pad.draw(screen)
        self.p3_pad.draw(screen)

        self.draw_messages(screen, pos_y=600)

    def update_drawing_pad(self, pad_id, mouse_down, mouse_pos):
        pad_to_update = None
        if pad_id == 0:
            pad_to_update = self.p2_pad
        if pad_id == 1:
            pad_to_update = self.p3_pad

        if pad_to_update:
            pad_to_update.update(mouse_down, mouse_pos, use_screen_pos=False)

    def update_player_drawing_pad(self,
                                  prev_mouse_down, mouse_down, mouse_pos):
        if self.timer <= 0:
            return

        self.main_pad.update(mouse_down, mouse_pos)

    def update_messages(self):
        messages = []

        message = ("Your drawing should be: \"{}\""
                   .format(self.client.drawing_answer))
        messages.append(message)

        total_seconds = self.timer / 1000
        minutes = int(total_seconds / 60)
        seconds = int(total_seconds % 60)
        messages.append("Time left: {}:{:02d}".format(minutes, seconds))

        if self.timer <= 0:
            messages.append("TIME OVER. Waiting for server...")

        self.messages = messages

    def update_network_player_drawing_pad(self, data):
        pad_id, mouse_down, mouse_pos = data
        self.update_drawing_pad(pad_id, mouse_down, mouse_pos)

    def update_broadcast_commands(self, packet, data):
        if packet == packets.DRAW:
            self.update_network_player_drawing_pad(data)

    def update_server_commands(self, data):
        self.timer = data["Time remaining"]
        for history in enumerate(data["History"]):
            pad_id, draw_commands = history
            for draw_command in draw_commands:
                mouse_down, pos = draw_command
                self.update_drawing_pad(pad_id, mouse_down, pos)

    def update(self, clock, prev_mouse_down, mouse_down, mouse_pos):
        self.timer -= clock.get_time()
        self.update_player_drawing_pad(prev_mouse_down, mouse_down, mouse_pos)
        self.update_messages()
