from time import sleep
import packets
from flux_game import Action_Connect, Action_Connect_Ack
import zmq

server_port = 667


class Network:
    def __init__(self, isServer):
        self.message_queue = []
        self.isServer = isServer

    def attach_engine(self, engine):
        self.engine = engine

    def update(self):
        return None

class NetworkServer(Network):
    def __init__(self):
        super(NetworkServer, self).__init__(isServer=True)
        addr = "tcp://*:"

        self.context = zmq.Context()
        self.client_conn = self.context.socket(zmq.REP)
        self.client_conn.bind(addr + str(server_port))

        self.poller = zmq.Poller()
        self.poller.register(self.client_conn, zmq.POLLIN)

        self.engine = None

        print("Server ready")

    def __del__(self):
        self.poller.unregister(self.client_conn)

    def update(self):
        socks = self.poller.poll(10)
        socks = dict(socks)

        if self.client_conn in socks:
            recv = self.client_conn.recv_json()
            player_id = recv[0]
            messages = recv[1:]
            player = self.engine.gamestate.get_player(player_id)
            if player:
                self.client_conn.send_json(player.message_queue)
                player.message_queue = []
                return messages
            elif player is None:
                # only connecting clients have None for player id
                if len(messages) == 1:
                    # let's make the engine parse the CONNECT packet
                    # and grab the player's id
                    # send that to the player
                    message = messages[0]
                    packet_name = message["packet"]
                    if packet_name != Action_Connect.packet_name:
                        print("Warning: expected CONNECT packet, but different packet received")
                        print(" Packet received is:", end="")
                        print(packet_name)
                        return None

                    action = Action_Connect(message["data"])
                    player_id = action.run_server(self.engine.gamestate)
                    self.client_conn.send_json(player_id)

        return None

    def send(self, action):
        target_id = action.target_id
        if target_id is None:
            # broadcast message to all players
            for player in self.engine.gamestate.players.values():
                player.message_queue.append(action.toJSON())
        else:
            player = self.engine.gamestate.get_player(target_id)
            if player:
                player.message_queue.append(action.toJSON())

class NetworkClient(Network):
    def __init__(self):
        super(NetworkClient, self).__init__(isServer=False)

        #self.player_name = input("What is your name? ")
        self.player_name = "Brave sir Robin"

        #server_address = input("Hostname/IP address of server? ")
        server_address = "localhost"
        #server_address = "shuny"

        addr = "tcp://{}:".format(server_address)

        self.context = zmq.Context()

        self.server = self.context.socket(zmq.REQ)
        self.server.connect(addr + str(server_port))
        self.server_poller = zmq.Poller()
        self.server_poller.register(self.server, zmq.POLLIN)
        self.server_send_poll = zmq.Poller()
        self.server_send_poll.register(self.server, zmq.POLLOUT)

        data = {"player_name": self.player_name}
        self.server.send_json([None, Action_Connect(data).toJSON()])

        print("Waiting for server")

        while not self.check_poll(self.server_poller):
            sleep(1)

        # wait for player id
        self.player_id = self.server.recv_json()
        print("Connected with id {}".format(self.player_id))

    def check_poll(self, poller):
        socks = dict(poller.poll(10))
        return self.server in socks

    def update_receive_commands(self):
        has_server_message = self.check_poll(self.server_poller)
        if has_server_message:
            return self.server.recv_json()

        return None

    def send(self, action):
        self.message_queue.append(action.toJSON())

    def update(self):
        can_send = self.check_poll(self.server_send_poll)
        if can_send:
            self.server.send_json([self.player_id] + self.message_queue)
            self.message_queue = []

        return self.update_receive_commands()