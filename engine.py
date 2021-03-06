import game
import view as flux_view


class Engine:
    """
    This is the dispatcher in the Flux architecture
    """

    def __init__(self, network, view=None):
        """
        If view is None, then the Engine will not receive
        direct input and output. It will still possible for
        the network to change the gamestate
        """
        self.gamestate = game.DrawGame()
        self.gamestate.attach_engine(self)

        self.network = network
        self.network.attach_engine(self)

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
        have_update = self.network.update()
        if have_update is None:
            return

        messages, player_id = have_update
        if messages:
            for message in messages:
                self.parse_network_message(message, player_id)

    def parse_network_message(self, message, player_id):
        try:
            packet_name = message["packet"]
            action_func = game.ActionList.get(packet_name, None)
            if action_func is None:
                print("Warning: {} is not registered".format(packet_name))
                return

            action = action_func(data=message["data"])
            action.source_player_id = player_id

            # if received as a network command, don't rebroadcast
            action.network_command = False

            self.apply(action)

            return action
        except TypeError as ex:
            import pdb
            pdb.set_trace()
            print("Warning: Malformed packet")
            print(message)
            print("")
