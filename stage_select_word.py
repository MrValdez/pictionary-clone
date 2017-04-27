from drawingpad import pad
from stage_base import Stage
import packets
import pygame

button_back_color = [255, 128, 255]
button_width = 50
timer_to_next_question = 1000


class SelectWord(Stage):
    def __init__(self,
                 network_client,
                 drawing, choices, time_remaining, resolution,
                 points):
        super(SelectWord, self).__init__()

        self.view_pad = pad([10, 20])
        for draw_command in drawing:
            mouse_down, pos = draw_command
            self.view_pad.update(mouse_down, pos, use_screen_pos=False)

        self.client = network_client
        self.timer = time_remaining
        self.wait_for_next_question = False
        self.network_message = ""
        self.lockdown_timer = 0
        self.points = points

        self.buttons = []
        self.player_answers = choices
        self.generate_buttons(start_pos=[600, 30], max_width=resolution[0])

    def draw(self, screen):
        screen.fill([255, 255, 255])

        self.view_pad.draw(screen)
        self.draw_answers(screen)

        self.draw_messages(screen, pos_y=600)

    def draw_answers(self, screen):
        for output, rect, pos in self.button_renders:
            pygame.draw.rect(screen,
                             button_back_color,
                             rect)
            screen.blit(output, pos)

    def generate_buttons(self, start_pos, max_width, padding=10):
        self.button_renders = []

        answers = self.player_answers
        current_x, current_y = start_pos
        max_height = 0
        for answer in self.player_answers:
            output = self.NormalText.render(answer, True, [0, 0, 0])
            pos = [current_x, current_y]
            rect = (output.get_rect()
                    .move(*pos)
                    .inflate(button_width, button_width / 2))
            max_height = max(max_height, rect.height + padding)

            if rect.right >= max_width:
                current_x = start_pos[0]
                current_y += max_height
                rect.move_ip(-pos[0], -pos[1])
                rect.move_ip(current_x, current_y)
                pos = [current_x, current_y]
                max_height = 0

            self.button_renders.append([output, rect, pos])
            current_x += rect.width + padding

    def update_broadcast_commands(self, packet, data):
        if packet == packets.DRAW:
            player_id, mouse_down, mouse_pos = data
            self.view_pad.update(mouse_down, mouse_pos, use_screen_pos=False)

    def update_server_commands(self, packet, data):
        if packet == packets.RESULTS:
            data = data[0]
            self.lockdown_timer = data["Time remaining"]
            self.network_message = data["Message"]
            self.points = data["Current points"]

    def _update_send_answer(self, answer_index):
        self.client.send_answer(answer_index)

    def update_messages(self):
        messages = []

        messages.append(self.network_message)

        total_seconds = self.timer / 1000
        minutes = int(total_seconds / 60)
        seconds = int(total_seconds % 60)
        message = "Time left for drawer: {}:{:02d}".format(minutes, seconds)
        messages.append(message)

        if self.timer <= 0:
            messages.append("Waiting for server...")

        self.messages = messages

    def update(self, clock, prev_mouse_down, mouse_down, mouse_pos):
        if (self.lockdown_timer <= 0 and
           (not mouse_down[0] and prev_mouse_down[0])):
            # player does left_click_up and is not in lockdown
            for answer_index, button in enumerate(self.button_renders):
                output, rect, pos = button
                if rect.collidepoint(mouse_pos):
                    self._update_send_answer(answer_index)

                    break

        time = clock.get_time()
        self.timer -= time
        self.lockdown_timer -= time

        if self.lockdown_timer <= 0:
            self.network_message = ""

        self.update_messages()
