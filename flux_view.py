import os
import pygame
import flux_game

class View:
    def __init__(self):
        self.engine = None
        self.screen = None

    def attach_engine(self, engine):
        self.engine = engine

    def send_action(self, action, data):
        self.engine.apply(action)

    def draw(self):
        if self.screen is None:
            return

        self.engine.gamestate.draw(self.screen)

    def update(self):
        pass

class BaseView(View):
    pass

class ClientView(View):
    """
    This is handles the input and output from the client
    """

    def __init__(self):
        super(ClientView, self).__init__()
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.font.init()

        self.resolution = [1024, 768]
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption("Pictionary clone")

        self.prev_mouse_down = pygame.mouse.get_pressed()

    def draw(self):
        super(ClientView, self).draw()

        pygame.display.update()

    def update(self):
        mouse_down = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if any(mouse_down):
            data = {"mouse_down": mouse_down,
                    "pos": mouse_pos}
            action = flux_game.Action_Draw(data)
            self.send_action(action, data)

        self.prev_mouse_down = mouse_down