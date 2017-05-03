import flux_game
import flux_view


class Engine:
    """
    This is the dispatcher in the Flux architecture
    """

    def __init__(self, network, view=None):
        """
        If view is None, then the Engine will not receive direct input and output.
        (It's still possible for the network to change the gamestate)
        """
        self.gamestate = flux_game.DrawGame()
        self.gamestate.attach_engine(self)

        self.network = network

        if view is None:
            view = flux_view.BaseView()
        view.attach_engine(self)
        self.view = view

    def apply(self, action):
        action.run(self.gamestate)

    def update(self):
        self.gamestate.update()
        if self.view:
            self.view.update()

    def draw(self):
        if self.view:
            self.view.draw()