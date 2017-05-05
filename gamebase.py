import pygame


class Action:
    packet_name = None
    network_command = False
    data_required = True

    def __init__(self, data=None, target_id=None):
        # target_id is the id of the player to send this packet to
        if not self.packet_name:
            raise TypeError("packet_name not initialized")
        if not isinstance(self.network_command, bool):
            raise TypeError("network_command should be boolean")
        if data is not None and not isinstance(data, dict):
            raise TypeError("Data should be dictionary")
        if self.data_required and data is None:
            raise TypeError("Data should not be empty in this packet")

        self.data = data or {}
        self.target_id = target_id

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
        self.clock = pygame.time.Clock()

    def attach_engine(self, engine):
        self.engine = engine

    def run_action(self, action):
        self.engine.apply(action)

    def update(self):
        self.clock.tick(60)

    def draw(self, screen):
        pass
