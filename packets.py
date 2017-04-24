# Packet commands
CONNECT      = 0
WAIT         = 1
STATE_CHANGE = 2
ACK          = 3
DRAW         = 4
ROOM_INFO    = 5
ACK_CONNECT  = 6


# Data structures for packets:

CONNECT_data = {
    "Player number": -1,            # a number used to identify player in broadcast
    "Player ID": "",                # a unique identifier used by player to authenticate to server
    "Player name": "",
    "Room ID": "",
    "Drawing answer": "42",
}

ROOM_info = {
    "History": [],
    "Time remaining": 9 * 1000,     # in milliseconds
}

WAIT_data = {
    "Timer": 0,
}

STATE_CHANGE_data = {
    "New State": 0,
}