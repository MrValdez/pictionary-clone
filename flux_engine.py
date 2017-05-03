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

        self.actions = []

    def apply(self, action):
        self.actions.append(action)

    def update(self):
        self.network_update()

        for action in self.actions:
            action.run(self.gamestate)
        self.actions = []

        self.gamestate.update()
        if self.view:
            self.view.update()

    def draw(self):
        if self.view:
            self.view.draw()

    def network_update(self):
        messages = self.network.update()
        if not messages:
            return

        for message in messages:
            print(message)
            packet, data = message
            #self.apply()
