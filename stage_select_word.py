from drawingpad import pad
from stage_base import Stage
import packets
import pygame

button_back_color = [255, 128, 255]
button_width = 100
timer_to_next_question = 1000


class SelectWord(Stage):
    def __init__(self, network_client):
        super(SelectWord, self).__init__()

        self.main_pad = pad([220, 40], scale=1.05)

        self.client = network_client
        self.player_answers = []
        self.current_player_to_test = 0
        self.wait_for_next_question = False
        self.current_timer_to_next_question = 0

        col1 = 50
        col2 = 750
        row1 = 200
        row2 = 500

        self.buttons = [[col1, row1],
                        [col2, row1],
                        [col1, row2],
                        [col2, row2]]
        self.button_renders = []

    def draw(self, screen):
        screen.fill([255, 255, 255])

        self.main_pad.draw(screen)
        self.draw_answers(screen)

        self.draw_messages(screen, pos_y=600)

    def draw_answers(self, screen):
        if self.current_player_to_test >= len(self.player_answers):
            return

        self.messages = []

        for output, rect, pos in self.button_renders:
            pygame.draw.rect(screen,
                             button_back_color,
                             rect)
            screen.blit(output, pos)

        commands = self.player_answers[self.current_player_to_test][1]
        for draw_command in commands:
            mouse_down, pos = draw_command
            self.main_pad.update(mouse_down, pos, use_screen_pos=False)

    def generate_buttons(self):
        self.button_renders = []

        answers = self.player_answers[self.current_player_to_test][0]
        for pos, answer in zip(self.buttons, answers):
            output = self.NormalText.render(answer, True, [0, 0, 0])
            rect = (output.get_rect()
                    .move(*pos).inflate(button_width, button_width))
            self.button_renders.append([output, rect, pos])

    def update_select_answer_stage(self, data):
        while data is None:
            # wait for the next broadcast
            data = self.client.update_client_commands()

        self.player_answers = data
        self.switch_player_to_test()

    def switch_player_to_test(self):
        self.current_player_to_test = (
            (self.current_player_to_test + 1) % len(self.player_answers))

        self.main_pad.clear()
        self.generate_buttons()

    def update_broadcast_commands(self, packet, data):
        pass

    def update_server_commands(self, data):
        pass

    def _update_send_answer(self, answer_index):
        print("Sending answer #{}".format(answer_index))

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
