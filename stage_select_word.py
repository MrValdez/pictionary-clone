from drawingpad import pad
from stage_base import Stage
import packets
import pygame

button_back_color = [255, 128, 255]
button_width = 50
timer_to_next_question = 1000


class SelectWord(Stage):
    def __init__(self, network_client, drawing, choices, time_remaining, resolution):
        super(SelectWord, self).__init__()

        self.view_pad = pad([10, 20])
        for draw_command in drawing:
            mouse_down, pos = draw_command
            self.view_pad.update(mouse_down, pos, use_screen_pos=False)

        self.client = network_client
        self.current_timer_to_next_question = time_remaining
        self.wait_for_next_question = False

        self.buttons = []
        self.player_answers = choices
        self.generate_buttons(start_pos = [600, 30], max_width = resolution[0])

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

    def generate_buttons(self, start_pos, max_width, padding= 10):
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
        print(packet, data)
        print(packets.DRAW)
        if packet == packets.DRAW:
            player_id, mouse_down, mouse_pos = data
            self.view_pad.update(mouse_down, mouse_pos, use_screen_pos=False)

    def update_server_commands(self, packet, data):
        print(packet, data)
        correct_answer = data["Correct Answer"]
        self.messages = ["The correct answer is \"{}\"".format(correct_answer)]

    def _update_send_answer(self, answer_index):
        self.client.send_answer(answer_index,
                                self.current_player_to_test)

        self.wait_for_next_question = True
        self.current_timer_to_next_question = timer_to_next_question

    def update(self, clock, prev_mouse_down, mouse_down, mouse_pos):
        if not mouse_down[0] and prev_mouse_down[0]:
            # left click up
            for answer_index, button in enumerate(self.button_renders):
                output, rect, pos = button
                if rect.collidepoint(mouse_pos):
                    self._update_send_answer(answer_index)

                    break

        if self.wait_for_next_question:
            self.current_timer_to_next_question -= clock.get_time()

            if self.current_timer_to_next_question <= 0:
                self.wait_for_next_question = False
                self.switch_player_to_test()
