import os
import pygame
import stage_base


class View:
    def __init__(self):
        self.engine = None
        self.screen = None

    def attach_engine(self, engine):
        self.engine = engine

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
        self.clock = pygame.time.Clock()

        self.current_stage = stage_base.Stage()     # blank stage
        self.prev_mouse_down = pygame.mouse.get_pressed()

    def draw(self):
        super(ClientView, self).draw()

        pygame.display.update()

    def update(self):
        self.clock.tick(60)
        
        mouse_down = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # send actions
        #self.engine.gamestate.update(self.clock,
        #                             self.prev_mouse_down, mouse_down, mouse_pos)

        self.prev_mouse_down = mouse_down