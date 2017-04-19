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

while True:
    try:
        socks = poller.poll(10)
        socks = dict(socks)

        if broadcast in socks:
            if socks[broadcast] == zmq.POLLIN:
                message = broadcast.recv()

                #parse messages
                if message == packets.CONNECT:
                    print("Connected")

        if server in socks:
            message = server.recv()
            if message == packets.CONNECT:
                print("New client connected")
                server.send_json(history)

        room_id = 1
        data = [random.randint(0, 2000), random.randint(0, 2000)]
        broadcast.send_string("{} {}".format(room_id, json.dumps(data)))

        history.append(data)

    except KeyboardInterrupt:
        break

poller.unregister(broadcast)
