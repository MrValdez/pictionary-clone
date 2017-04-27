# Packet commands
CONNECT             = 0
WAIT                = 1
STATE_CHANGE        = 2
ACK                 = 3
DRAW                = 4
ROOM_INFO           = 5
ACK_CONNECT         = 6
SELECT_ANSWER_INFO  = 7
SEND_ANSWER         = 8
SEND_CORRECT_ANSWER = 9
RESULTS             = 10
DRAWING_INFO        = 11
GUESS_INFO          = 12
REQUEST_RESULTS     = 13
ANSWER_FOUND        = 14
REQUEST_NEXT_STAGE  = 15

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

SELECT_ANSWER_data = {
    "Choices": [],
    "Drawing": [],
}

SEND_CORRECT_ANSWER_data = {
    "Correct Answer": "",
}

RESULTS_data = {
    "Current points": 0,
    "Time remaining": 0,
    "Message": "",
}

DRAWING_INFO_data = {
    "Drawing answer": "42",
    "Time remaining": 9 * 1000,
    "Player points": 0,
}

GUESS_INFO_data = {
    "Choices": [],
    "Drawing": [],
    "Time remaining": 9 * 1000,
    "Player points": 0,
}