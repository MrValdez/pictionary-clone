class Action:
    def __init__(self):
        pass

    def run(self, GameState):
        pass

class GameState:
    """
    This is the store in the Flux architecture
    """
    pass

class Engine:
    """
    This is the dispatcher in the Flux architecture
    """

    def __init__(self, network, view=None):
        """
        If view is None, then the Engine will not receive direct input and output.
        (It's still possible for the network to change the gamestate)
        """
        self.gamestate = GameState()
        self.view = view
        self.network = network

    def apply(self, action):
        action.run(self.gamestate)

    def update(self):
        if self.view:
            self.view.update()

    def draw(self):
        if self.view:
            self.view.draw()