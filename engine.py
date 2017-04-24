import os
import pygame
import network
from drawingpad import pad


class GameEngine:
    def __init__(self):
        os.environ["SDL_VIDEO_CENTERED"] = "1"

        pygame.init()

        self.resolution = [1024, 768]
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption("Pictionary clone")
        self.clock = pygame.time.Clock()

        self._init_player_state()

    def _init_player_state(self):
        player_name = "Sir Lancelot the Brave"
        self.client = network.client(player_name)

        self.main_pad = pad([40, 40], network_connection=self.client)
        self.p2_pad = pad([700, 40], scale=.45)
        self.p3_pad = pad([700, 300], scale=.45)

        for history in enumerate(self.client.current_game_state["History"]):
            pad_id, draw_commands = history
            for draw_command in draw_commands:
                mouse_down, pos = draw_command
                self._update_drawing_pad(pad_id, mouse_down, pos)

    def draw(self):
        self.screen.fill([255, 255, 255])

        self.main_pad.draw(self.screen)
        self.p2_pad.draw(self.screen)
        self.p3_pad.draw(self.screen)

        pygame.display.update()

    def _update_drawing_pad(self, pad_id, mouse_down, mouse_pos):
        pad_to_update = None
        if pad_id == 0:
            pad_to_update = self.p2_pad
        if pad_id == 1:
            pad_to_update = self.p3_pad

        if pad_to_update:
            pad_to_update.update(mouse_down, mouse_pos, use_screen_pos=False)

    def _update_player_drawing_pad(self):
        mouse_down = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        self.main_pad.update(mouse_down, mouse_pos)

    def _update_other_player_drawing_pad(self):
        while True:
            network_data = self.client.update()
            if not network_data:
                break

            pad_id, mouse_down, mouse_pos = network_data
            self._update_drawing_pad(pad_id, mouse_down, mouse_pos)

    def update(self):
        self._update_player_drawing_pad()
        self._update_other_player_drawing_pad()

        self.clock.tick(60)
