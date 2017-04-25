import os
import packets
import pygame
import network
import stage_drawing
import stage_select_word


class GameEngine:
    def __init__(self):
        os.environ["SDL_VIDEO_CENTERED"] = "1"

        #self.player_name = input("What is your name? ")
        self.player_name = "Brave sir Robin"

        pygame.init()
        pygame.font.init()

        self.resolution = [1024, 768]
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption("Pictionary clone")
        self.clock = pygame.time.Clock()

        self._connect_to_server()

        self.current_stage = stage_drawing.Drawing(self.client)
        self.prev_mouse_down = pygame.mouse.get_pressed()

    def _connect_to_server(self):
        self.client = network.client(self.player_name)

    def draw(self):
        self.current_stage.draw(self.screen)

        pygame.display.update()

    def update_broadcast_commands(self):
        while True:
            network_data = self.client.update_client_commands()
            if not network_data:
                break

            packet, data = network_data[0], network_data[1:]

            if packet == packets.SELECT_ANSWER_INFO:
                # transition to next stage
                self.current_stage = stage_select_word.SelectWord(self.client)
                self.current_stage.update_select_answer_stage(data)
            else:
                self.current_stage.update_broadcast_commands(packet, data)

    def update_server_commands(self):
        while True:
            data = self.client.update_server_commands()
            if not data:
                break

            if data == packets.ACK:
                # server receives our message. move lockstep to server
                break

            self.current_stage.update_server_commands(data)

    def update(self):
        self.clock.tick(60)

        mouse_down = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        self.update_server_commands()
        self.update_broadcast_commands()

        self.current_stage.update(self.clock,
                                  self.prev_mouse_down, mouse_down, mouse_pos)

        self.prev_mouse_down = mouse_down
