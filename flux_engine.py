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

        actions_prev_frame = self.actions[:]
        self.actions = []
        for action in actions_prev_frame:
            if self.network.isServer:
                action.run_server(self.gamestate)
            else:
                action.run(self.gamestate)

            if action.network_command:
                self.network.send(action)

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
            try:
                packet_name = message["packet"]
                action = flux_game.ActionList.get(packet_name)
                self.apply(action(message["data"]))
            except TypeError:
                print("Warning: Malformed packet")
                print(message)
                print("")