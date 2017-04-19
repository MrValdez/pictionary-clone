import json
import random
import zmq
import packets

addr = "tcp://*:667"

context = zmq.Context()
sock = context.socket(zmq.PUB)
sock.bind(addr)

poller = zmq.Poller()
poller.register(sock, zmq.POLLIN)

while True:
    try:
        socks = poller.poll(10)
        socks = dict(socks)

        if sock in socks:
            if socks[sock] == zmq.POLLIN:
                message = sock.recv()

                #parse messages
                if message == packets.CONNECT:
                    print("Connected")

        room_id = 1
        data = [random.randint(0, 2000), random.randint(0, 2000)]
        sock.send_string("{} {}".format(room_id, json.dumps(data)))

    except KeyboardInterrupt:
        break

poller.unregister(sock)
