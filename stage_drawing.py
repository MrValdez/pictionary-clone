from drawingpad import pad
from stage_base import Stage
import packets
import pygame


class Drawing(Stage):
    def __init__(self, network_client, drawing_answer, time_remaining):
        super(Drawing, self).__init__()

        self.client = network_client

        self.drawing_answer = drawing_answer
        self.timer = time_remaining
        self.can_draw = True
        self.network_message = ""

        self.main_pad = pad([250, 40], network_connection=network_client)

    def draw(self, screen):
        screen.fill([255, 255, 255])

        self.main_pad.draw(screen)

        self.draw_messages(screen, pos_y=600)

    def update_player_drawing_pad(self,
                                  prev_mouse_down, mouse_down, mouse_pos):
        if self.timer <= 0 or not self.can_draw:
            return

        self.main_pad.update(mouse_down, mouse_pos)

    def update_messages(self):
        messages = []

        if not self.network_message:
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

    def update_broadcast_commands(self, packet, data):
        if packet == packets.ANSWER_FOUND:
            self.client.request_results()
            self.can_draw = False

    def update_server_commands(self, packet, data):
        if packet == packets.RESULTS:
            data = data[0]
            self.points = data["Current points"]
            self.timer = data["Time remaining"]
            self.network_message = data["Message"]

    def update(self, clock, prev_mouse_down, mouse_down, mouse_pos):
        self.timer -= clock.get_time()
        self.update_player_drawing_pad(prev_mouse_down, mouse_down, mouse_pos)
        self.update_messages()
