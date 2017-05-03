import packets
from flux_game import Action_Connect
import zmq

server_port = 667


class Network:
    def __init__(self, isServer):
        self.message_queue = []
        self.isServer = isServer

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

        self.message_queue = []
        print("Server ready")

    def __del__(self):
        self.poller.unregister(self.client_conn)

    def update(self):
        socks = self.poller.poll(10)
        socks = dict(socks)

        if self.client_conn in socks:
            messages = self.client_conn.recv_json()
            self.client_conn.send_json(self.message_queue)
            self.message_queue = []
            return messages

        return None

    def send(self, action):
        self.message_queue.append(action.toJSON())

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
        self.send(Action_Connect(data))

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
        if can_send and self.message_queue:
            self.server.send_json(self.message_queue)
            self.message_queue = []

        return self.update_receive_commands()