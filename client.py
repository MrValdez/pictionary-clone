import zmq
import json

addr = "tcp://localhost:667"

context = zmq.Context()
sock = context.socket(zmq.SUB)
sock.setsockopt_string(zmq.SUBSCRIBE, "1")
sock.connect(addr)

poller = zmq.Poller()
poller.register(sock, zmq.POLLIN)

#sock.send(b"Hello")
#sock.send_json([1,2,3])

while True:
    try:
        socks = dict(poller.poll(1000))
        
        if sock in socks:
            msg = sock.recv_string()
            msg = msg[msg.find(" "):].strip()
            msg_json = json.loads(msg)
            print(type(msg_json))
            print(msg_json)
    except KeyboardInterrupt:
        break

poller.unregister(sock)
