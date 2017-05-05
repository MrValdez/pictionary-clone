# Game introduction

This game is a combination of Pictionary, Pictomania, and Drawful (from You don't know Jack) with my own additional game design additions.

The game engine uses the [Flux programming pattern](https://facebook.github.io/flux/docs/in-depth-overview.html#content).

Flux term | Game equivalent
---- | ----
Dispatch | Engine
Store | Game
View | View

I've noticed that the Action paradigm is equivalent to game design patterns for events.

# Security issue

1. The server-client network structure uses player id to authenticate the player. To mitigate hackers from randomly guessing and hijacking a player, the player's socket info (ip address, ip port, etc) should also be used. The fix is to change from ZeroMQ's REQ/REP network architecture to something else; probably PUSH/PULL?

# Bugs

1. Some variables should be "server-side only" such as the correct answer. Currently, this is being broadcast to everyone.

# Nice to have

1. The actions list can be automatically populated (either via metaprogramming or a register command).
2. Automatic awards:

| Award | How to detect |
| Least energetic to draw | broad strokes |
| Least used of ink | left click durations can be tracked |
| Attention to detail | Tiny movement of mouse during drawings |
| A lot of erasures | erasures can be tracked |
| Tries to cheat with letters! | A neural network to look for letters? |

3. More refactoring to farther decouple the dispatch, view, and store
4. More polish
5. Development logs to keep track (and visualize?) how the flux messaging flows between components.

# Answers

Answer.txt contains the answers. These were taken from [tvtropes's indexes](http://tvtropes.org/pmwiki/index_report.php) (warning: TvTropes).