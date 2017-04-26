import json
import random
import zmq
import packets
import network
import gamestate

USE_AI = False

server = network.Server()
room = gamestate.Room(server)

if USE_AI:
    AI_player = room.addPlayer("LEONARDO")


def update_AI():
    if not USE_AI:
        return

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
            data["Drawing answer"] = newPlayer.drawing_answer

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

        if packet == packets.SEND_ANSWER:
            playerID = data[0]
            question_idx, player_choice = data[1]

            to_send = packets.SEND_CORRECT_ANSWER_data.copy()
            to_send["Correct Answer"] = room.all_correct_answers[question_idx]
            server.client_conn.send_json(to_send)

        update_AI()
        room.update()
    except KeyboardInterrupt:
        break
