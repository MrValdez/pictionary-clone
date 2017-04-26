import network
import gamestate

server = network.Server()
room = gamestate.Room(server)

print("Server ready")
while True:
    try:
        packet, data = server.update()
        room.update_network(packet, data)

        room.update()
    except KeyboardInterrupt:
        break
