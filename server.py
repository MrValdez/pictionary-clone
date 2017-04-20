import json
import random
import zmq
import packets
import network
import gamestate

server = network.Server()

room = gamestate.Room(server)

print("Server ready")
while True:
    try:
        packet, data = server.update()
        if packet == packets.CONNECT:
            print("New client connected")

            name = data[0]
            newPlayer = room.addPlayer(name)
            server.players_in_room.append(newPlayer.id)

            data = packets.CONNECT_data.copy()
            data["Player name"] = newPlayer.name
            data["Player ID"] = newPlayer.id
            data["History"] = newPlayer.history
            server.client_conn.send_json(data)

        if packet == packets.DRAW:
            server.client_conn.send(bytes([packets.ACK]))
            player_id = data[0]
            mouse_down, pos = data[1]
            room.update_history(player_id, mouse_down, pos)

#        data = [1,
#                [True, False, False],
#                [random.randint(0, 2000), random.randint(0, 2000)]]
#        send_broadcast(room_id, data)
    except KeyboardInterrupt:
        break
