import json
import zmq
import packets

addr = "tcp://localhost:667"


class client:
    def __init__(self):
        self.init_client()

    def init_client(self):
        context = zmq.Context()
        sock = context.socket(zmq.SUB)
        sock.setsockopt_string(zmq.SUBSCRIBE, "")
        sock.connect(addr)

        poller = zmq.Poller()
        poller.register(sock, zmq.POLLIN)
        #sock.send(packets.CONNECT)

        self.context = context
        self.sock = sock
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
