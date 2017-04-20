import json
import zmq
import packets

server_port = 667
broadcast_port = 668

addr = "tcp://localhost:"


class client:
    def __init__(self):
        context = zmq.Context()
        sock = context.socket(zmq.SUB)
        sock.setsockopt_string(zmq.SUBSCRIBE, "")
        sock.connect(addr + str(broadcast_port))

        server = context.socket(zmq.REQ)
        server.connect(addr + str(server_port))

        poller = zmq.Poller()
        poller.register(sock, zmq.POLLIN)
        poller.register(server, zmq.POLLIN)

        server.send_json([packets.CONNECT])
        self.current_game_state = server.recv_json()

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
        self.server.send_json([packets.DRAW, data])
        self.server.recv()
