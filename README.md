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
| Game state manager | | 3 |
| Connect multiple pygame clients to one server | | 4 |
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
| CONNECT | CLIENT | Server will send the game room and its game state to the client. |
| GAMESTATE | SERVER | Client will receive the game state. It is up to the client to update its personal game state |
| DRAW | CLIENT | Server will parse the position the client draws. All connected clients will be updated of the new game state |
| DRAW_UPDATE | SERVER | Client will receive a list of changes other clients have done. |
