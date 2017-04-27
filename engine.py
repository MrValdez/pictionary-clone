import os
import packets
import pygame
import network
import stage_base
import stage_drawing
import stage_select_word


class GameEngine:
    def __init__(self):
        #self.player_name = input("What is your name? ")
        self.player_name = "Brave sir Robin"

        #server_address = input("IP address of server? ")
        server_address = "localhost"
        server_address = "shuny"

        self.client = network.client(self.player_name, server_address)

        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.font.init()

        self.resolution = [1024, 768]
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption("Pictionary clone")
        self.clock = pygame.time.Clock()

        self.current_stage = stage_base.Stage()     # blank stage
        self.prev_mouse_down = pygame.mouse.get_pressed()

    def draw(self):
        self.current_stage.draw(self.screen)

        pygame.display.update()

    def transition_stage(self, packet, data):
        if packet == packets.DRAWING_INFO:
            data = data[0]
            drawing_answer = data["Drawing answer"]
            time_remaining = data["Time remaining"]
            points = data["Player points"]
            new_stage = stage_drawing.Drawing(self.client,
                                              drawing_answer, time_remaining,
                                              points)
            new_stage.main_pad.clear()
            self.current_stage = new_stage
        elif packet == packets.GUESS_INFO:
            data = data[0]
            drawing = data["Drawing"]
            choices = data["Choices"]
            time_remaining = data["Time remaining"]
            points = data["Player points"]
            new_stage = stage_select_word.SelectWord(self.client,
                                                     drawing, choices,
                                                     time_remaining,
                                                     self.resolution,
                                                     points)
            new_stage.view_pad.clear()
            self.current_stage = new_stage

    def update_broadcast_commands(self):
        while True:
            network_data = self.client.update_client_commands()
            if not network_data:
                break

            packet, data = network_data[0], network_data[1:]

            if packet == packets.REQUEST_NEXT_STAGE:
                self.client.send_request_for_stage_info()
            else:
                self.current_stage.update_broadcast_commands(packet, data)

    def update_server_commands(self):
        while True:
            network_data = self.client.update_server_commands()
            if not network_data:
                break

            if network_data == packets.ACK:
                # server receives our message. move lockstep to server
                break

            packet, data = network_data[0], network_data[1:]

            if packet == packets.DRAWING_INFO or packet == packets.GUESS_INFO:
                self.transition_stage(packet, data)
            else:
                self.current_stage.update_server_commands(packet, data)

    def update(self):
        self.clock.tick(60)

        mouse_down = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        self.update_server_commands()
        self.update_broadcast_commands()

        self.current_stage.update(self.clock,
                                  self.prev_mouse_down, mouse_down, mouse_pos)

        self.prev_mouse_down = mouse_down
