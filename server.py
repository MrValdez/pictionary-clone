import json
import random
import zmq
import packets
import network
import gamestate

server = network.Server()
room = gamestate.Room(server)

# AI_player = room.addPlayer("LEONARDO")


def update_AI():
    mouse_down = [True, False, False]
    pos = [random.randint(0, 2000), random.randint(0, 2000)]
    room.update_history(AI_player.id, mouse_down, pos)


print("Server ready")
while True:
    try:
        packet, data = server.update()
        if packet == packets.CONNECT:
            print("New client connected")

            name = data[0]
            newPlayer = room.addPlayer(name)

            data = packets.CONNECT_data.copy()
            data["Player number"] = newPlayer.number
            data["Player name"] = newPlayer.name
            data["Player ID"] = newPlayer.id

            server.client_conn.send_json(data)

        if packet == packets.ACK_CONNECT:
            data = packets.ROOM_info.copy()
            data["Time remaining"] = room.time_remaining

            # get the history of each players, sorted by player number
            players = sorted(room.players.values(),
                             key=lambda x: x.number)
            data["History"] = [player.history
                               for player in players
                               if len(player.history)]

            server.client_conn.send_json(data)

        if packet == packets.DRAW:
            server.client_conn.send_json(packets.ACK)

            player_id = data[0]
            mouse_down, pos = data[1]
            room.update_history(player_id, mouse_down, pos)

#        update_AI()
        room.update()
    except KeyboardInterrupt:
        break
