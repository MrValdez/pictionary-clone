import json
import random
import zmq
import packets
import network

addr = "tcp://*:"

context = zmq.Context()
broadcast = context.socket(zmq.PUB)
broadcast.bind(addr + str(network.broadcast_port))

server = context.socket(zmq.REP)
server.bind(addr + str(network.server_port))

poller = zmq.Poller()
poller.register(broadcast, zmq.POLLIN)
poller.register(server, zmq.POLLIN)

history = []
room_id = 1


def send_broadcast(room_id, data):
    broadcast.send_string("{} {}".format(room_id, json.dumps(data)))

print("Server ready")
while True:
    try:
        socks = poller.poll(10)
        socks = dict(socks)

        if broadcast in socks:
            if socks[broadcast] == zmq.POLLIN:
                message = broadcast.recv()

        if server in socks:
            message = server.recv_json()
            command = message[0]

            if command == packets.CONNECT:
                print("New client connected")
                server.send_json(history)

            if command == packets.DRAW:
                server.send(bytes([packets.ACK]))
                data = message[1]
                data = [2, *data]
                send_broadcast(room_id, data)

        data = [1,
                [True, False, False],
                [random.randint(0, 2000), random.randint(0, 2000)]]
        send_broadcast(room_id, data)

        history.append(data)

    except KeyboardInterrupt:
        break

poller.unregister(broadcast)
