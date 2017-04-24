# Game introduction

This game is a combination of Pictionary, Pictomania, and Drawful (from You don't know Jack) with my own additional game design additions.


# Stages
1. Drawing stage
1.a. Bonus points for finishing earlier
2. Guessing with choices (with timer)
2.a. Multiplier for every correct guess
3. Manual award (to be shown at awarding ceremony)
4. Automatic award.
5. Awarding ceremony.

# Automatic awards
Least energetic to draw
    broad strokes
Least used of ink
    Small number of ink used
Attention to detail
    Tiny movement of drawing
A lot of erasures
Tries to cheat with letters!    (-10pts)

# Backlog

| Item | Description | Estimated cost (1-5) | Actual Cost |
| ---- | ---- | ----: |
| Drawing interface | | 3 | 2 |
| Stream drawing to other clients | | 5 |
| Send initial drawing to connecting clients | | 3 | 2 |
| Connect multiple pygame clients to one server | | 4 | 4 |
| Wait for other players | | 2 |  |
| Game state manager | | 3 |
| Stage 1 timer | | 2 |
| Word animations | | 3 |
| Send word choices (with correct word) to other clients | | 3 |
| Manual awards | | 3 |
| Awarding ceremony animations | | 4 |
| Automatic awards | | 5 |
| Polish | | 5 |

# Network commands
| Name | Sender | Description |
| ---- | ---- | :---- |
| CONNECT | CLIENT | Server will send the game room and its game state to the client. The server will also send the client's id and needs to be sent for every succeeding client connections |
| GAMESTATE | SERVER | Client will receive the game state. It is up to the client to update its personal game state |
| ACK | SERVER | Sent by the server to acknowledge receiving a client's packet |
| DRAW | CLIENT | Server will parse the position the client draws. All connected clients will be updated of the new game state |
| DRAW_UPDATE | SERVER | Client will receive a list of changes other clients have done. |


# Security issue

1. The server-client network structure uses player id to authenticate the player. To mitigate hackers from randomly guessing and hijacking a player, the player's socket info (ip address, ip port, etc) should also be used. The fix is to change from ZeroMQ's REQ/REP network architecture to something else; probably PUSH/PULL?