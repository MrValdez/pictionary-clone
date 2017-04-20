import json
import random
import zmq
import packets
import network
import gamestate

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
room = gamestate.Room()

def send_broadcast(room, data):
    broadcast.send_string("{} {}".format(room.id, json.dumps(data)))

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

                data = message[1]
                name = data[0]
                newPlayer = room.addPlayer(name)

                data = packets.CONNECT_data.copy()
                data["Player name"] = newPlayer.name
                data["Player ID"] = newPlayer.id
                data["History"] = history
                server.send_json(data)

            if command == packets.DRAW:
                server.send(bytes([packets.ACK]))
                playerID = message[1]
                data = message[2]
                data = [2, *data]
                send_broadcast(room, data)

        data = [1,
                [True, False, False],
                [random.randint(0, 2000), random.randint(0, 2000)]]
        send_broadcast(room, data)

        history.append(data)

    except KeyboardInterrupt:
        break

poller.unregister(broadcast)
