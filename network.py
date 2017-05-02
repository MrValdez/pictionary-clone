import json
import zmq
import packets

server_port = 667
broadcast_port = 668


class client:
    def __init__(self, player_name, server_address):
        addr = "tcp://{}:".format(server_address)

        context = zmq.Context()
        broadcast = context.socket(zmq.SUB)
        broadcast.setsockopt_string(zmq.SUBSCRIBE, "")
        broadcast.connect(addr + str(broadcast_port))

        server = context.socket(zmq.REQ)
        server.connect(addr + str(server_port))

        client_poller = zmq.Poller()
        client_poller.register(broadcast, zmq.POLLIN)

        server_poller = zmq.Poller()
        server_poller.register(server, zmq.POLLIN)

        self.context = context
        self.broadcast = broadcast
        self.server = server
        self.client_poller = client_poller
        self.server_poller = server_poller

        server.send_json([packets.CONNECT, player_name])

        current_game_state = server.recv_json()
        self.id = current_game_state["Player ID"]
        self.player_number = current_game_state["Player number"]
        self.drawing_answer = current_game_state["Drawing answer"]

        self.send_request_for_stage_info()

    def _update_network_commands(self, socket, poller, recv_handler):
        socks = dict(poller.poll(10))
        if socket in socks:
            return recv_handler(socket)

        return None

    def update_client_commands(self):
        def recv_subs_json(socket):
            msg = socket.recv_string()
            msg = msg[msg.find(" "):].strip()
            return json.loads(msg)

        return self._update_network_commands(self.broadcast,
                                             self.client_poller,
                                             recv_subs_json)

    def update_server_commands(self):
        def recv_json(socket):
            return socket.recv_json()

        return self._update_network_commands(self.server,
                                             self.server_poller,
                                             recv_json)

    def send_request_for_stage_info(self):
        self.send(packets.ACK_CONNECT, [self.id])

    def send_draw_command(self, mouse_down, position):
        data = [mouse_down, position]
        self.send(packets.DRAW, data)

    def send_answer(self, answer_index):
        data = answer_index
        self.send(packets.SEND_ANSWER, data)

    def request_results(self):
        self.send(packets.REQUEST_RESULTS, [])

    def send(self, packet_type, data):
        self.server.send_json([packet_type, self.id, data])


class Server:
    def __init__(self):
        addr = "tcp://*:"

        context = zmq.Context()
        broadcast = context.socket(zmq.PUB)
        broadcast.bind(addr + str(broadcast_port))

        client_conn = context.socket(zmq.REP)
        client_conn.bind(addr + str(server_port))

        poller = zmq.Poller()
        poller.register(broadcast, zmq.POLLIN)
        poller.register(client_conn, zmq.POLLIN)

        self.broadcast = broadcast
        self.client_conn = client_conn
        self.poller = poller

    def __del__(self):
        self.poller.unregister(self.broadcast)
        self.poller.unregister(self.client_conn)

    def read_clients(self):
        return self.client_conn.recv_json()

    def send_broadcast(self, room_id, packet, data):
        data = [packet, *data]
        self.broadcast.send_string("{} {}".format(room_id, json.dumps(data)))

    def update(self):
        socks = self.poller.poll(10)
        socks = dict(socks)

        if self.broadcast in socks:
            if socks[self.broadcast] == zmq.POLLIN:
                message = self.broadcast.recv()

        if self.client_conn in socks:
            message = self.read_clients()

            packet = message[0]
            data = message[1:]
            return packet, data

        return None, None
