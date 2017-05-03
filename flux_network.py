import packets
from flux_game import Action_Connect
import zmq

server_port = 667


class Network:
    def __init__(self):
        self.message_queue = []

    def update(self):
        return None

class NetworkServer(Network):
    def __init__(self):
        super(NetworkServer, self).__init__()
        addr = "tcp://*:"

        self.context = zmq.Context()
        self.client_conn = self.context.socket(zmq.REP)
        self.client_conn.bind(addr + str(server_port))

        self.poller = zmq.Poller()
        self.poller.register(self.client_conn, zmq.POLLIN)

        print("Server ready")

    def __del__(self):
        self.poller.unregister(self.client_conn)

    def update(self):
        socks = self.poller.poll(10)
        socks = dict(socks)

        if self.client_conn in socks:
            messages = self.client_conn.recv_json()
            self.client_conn.send_json([])
            return messages

        return None

class NetworkClient(Network):
    def __init__(self):
        super(NetworkClient, self).__init__()

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
        self.send(Action_Connect(self.player_name))
        self.send(Action_Connect(self.player_name))

    def _update_network_commands(self, socket, poller, recv_handler):
        socks = dict(poller.poll(10))
        if socket in socks:
            return recv_handler(socket)

        return None

    def update_server_commands(self):
        def recv_json(socket):
            return socket.recv_json()

        return self._update_network_commands(self.server,
                                             self.server_poller,
                                             recv_json)

    def send(self, action):
        self.message_queue.append(action.toJSON())

    def update(self):
        if self.message_queue:
            self.server.send_json(self.message_queue)
        self.message_queue = []

        self.update_server_commands()