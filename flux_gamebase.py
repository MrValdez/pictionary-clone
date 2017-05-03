import pygame


class Action:
    packet_name = None
    network_command = False

    def __init__(self, data):
        if not self.packet_name:
            raise TypeError("packet_name not initialized")
        if not isinstance(self.network_command, bool):
            raise TypeError("network_command should be boolean")
        if not isinstance(data, dict):
            raise TypeError("Data should be dictionary")

        self.data = data

    def toJSON(self):
        return {"packet": self.packet_name,
                "data": self.data}

    def run(self, GameState):
        """
        Command run in the client
        """
        pass

    def run_server(self, GameState):
        """
        Command run when server receives this action
        """
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