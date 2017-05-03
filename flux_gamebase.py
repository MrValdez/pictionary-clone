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
        pass

    def attach_engine(self, engine):
        self.engine = engine

    def update(self):
        pass

    def draw(self, screen):
        pass