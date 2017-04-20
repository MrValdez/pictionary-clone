# Packet commands
CONNECT = 0
DRAW    = 1
ACK     = 2



# CONNECT structure
CONNECT_data = {
    "Player number": -1,            # a number used to identify player in broadcast
    "Player ID": "",                # a unique identifier used by player to authenticate to server
    "Player name": "",
    "Room ID": "",
    "History": [],
}