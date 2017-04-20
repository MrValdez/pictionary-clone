import json
import zmq
import packets

server_port = 667
broadcast_port = 668


class client:
    def __init__(self, player_name):
        addr = "tcp://localhost:"

        context = zmq.Context()
        sock = context.socket(zmq.SUB)
        sock.setsockopt_string(zmq.SUBSCRIBE, "")
        sock.connect(addr + str(broadcast_port))

        server = context.socket(zmq.REQ)
        server.connect(addr + str(server_port))

        poller = zmq.Poller()
        poller.register(sock, zmq.POLLIN)
        poller.register(server, zmq.POLLIN)

        server.send_json([packets.CONNECT, [player_name]])
        self.current_game_state = server.recv_json()
        self.id = self.current_game_state["Player ID"]
        self.player_number = self.current_game_state["Player number"]
        print(self.player_number)

        self.context = context
        self.sock = sock
        self.server = server
        self.poller = poller

    def recv_subs_json(self):
        msg = self.sock.recv_string()
        msg = msg[msg.find(" "):].strip()
        return json.loads(msg)

    def update(self):
        socks = dict(self.poller.poll(10))
        if self.sock in socks:
            return self.recv_subs_json()

        return None

    def send_draw_command(self, mouse_down, position):
        data = [mouse_down, position]
        self.send(packets.DRAW, data)

    def send(self, packet_type, data):
        self.server.send_json([packet_type, self.id, data])
        self.server.recv()


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

    def send_broadcast(self, room_id, player, data):
        player_number = player.number
        data = [player_number, *data]
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