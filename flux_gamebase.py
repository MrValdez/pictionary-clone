import pygame


class Action:
    def __init__(self, data):
        if not isinstance(data, dict):
            raise TypeError("Data should be dictionary")

        self.data = data

    def run(self, GameState):
        pass

class GameState:
    """
    This is the store in the Flux architecture
    """
    def __init__(self):
        self.NormalText = pygame.font.Font(None, 25)
        self.messages = []
        self.ui_points_pos = [970, 700]

    def attach_engine(self, engine):
        self.engine = engine

    def update(self):
        pass

    def draw(self, screen):
        pass

    def draw_messages(self, screen, pos_y):
        for message in self.messages:
            output = self.NormalText.render(message, True, [0, 0, 0])
            screen.blit(output, [40, pos_y])
            pos_y += output.get_height() + 10

