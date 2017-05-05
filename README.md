# Game introduction

This game is a combination of Pictionary, Pictomania, and Drawful (from You don't know Jack) with my own additional game design additions.

To play the game, the server should be running. The first player to join will become the *Drawing Player*. Other players can join to become *Guessers*. The Drawing Player will receive a phrase to draw. The Guessers will try to figure out what the Drawing Player is drawing.

After a certain amount of time, the server will randomize who will be the next Drawing Player from the current player pool.

Points are given for the following events:

Event | Points for Drawing Player | Points for guesser
---- | ---- | ----
A guesser sent a wrong answer | 0 | 1
Someone guessed the Drawing Player's phrase correctly | 30 | 10
No one correctly guessed the Drawing Player's phrase | 0 |  -20


# Game Programming architecture

This game was developed for learning [ZeroMQ library](zguide.zeromq.org) and the [Flux programming pattern](https://facebook.github.io/flux/docs/in-depth-overview.html#content).

## ZeroMQ
ZeroMQ is a networking library used for quickly creating a messaging pipeline between programs in a network.

## Flux design pattern

Flux is a design pattern developed by Facebook. This tries to solve the problem of managing the code for multiple "actions" or commands that have different effects on the system.

The example Facebook uses is the unread notifications; with their previous MVC pattern, it was not easy to clear the unread notifications since Facebook have multiple messaging applications (or views) such as the pop-up message box, stand-alone full-view message app, or the mobile facebook messaging app. Each of these applications have their own code flow and each one have to add custom code to clear the unread notification.

Flux aims to solve this by separating the program into three: the Dispatch, Store and View. The "Action" command will act as the code that will modify the state of the application. Actions can be commands such as "send chat message" or "like post". Actions can send additional Actions such as "clear unread notifications".

The Dispatch module is responsible for sending the Action over the network, different calculating nodes or even different applications within the system.

The Store module is responsible for executing the Actions.

The View module takes the data (or state) from the Store and generate an interface for the user (or even for an automated test)

## ZeroMQ observations
Based on my experience in this project, ZeroMQ may not be the perfect choice for game programming.

In game programming, the game engine should have control on which specific packets are important (guranteed sent), can be dropped (low priority messages such as timer updates; since the client can be expected to update their own time), takes priority (commands that most be moved up higher in case latency spikes causes a message queue to be delayed), and so on.

ZeroMQ is not built for this. With ZeroMQ, the programmer will send a packet with no way of customizing the packet queue. The design of the library is to fire and forget; with the library resending the packet in case the connection is broken.

For this project, I've assumed that each packet I'll send will be sent in order. This affected the game design.

Based on my experiments, I find ZeroMQ is a good network library as long as you are not doing game programmming. I like the broadcast sockets and I never needed to work directly on network sockets during development.

## Flux observations
Since I have a background on game programming, I've mapped the following Flux terms into their game programming equivalent (at least, based on how I understand Flux).

Flux term | Game equivalent
---- | ----
Dispatch | Engine
Store | Game
View | View

I've noticed that the Action paradigm is equivalent to game design patterns for events. In game programming, there is an event manager that handles events. For example, in a baseball game, the player can press a button to swing a bat. This "swing bat event" will be sent to an event manager for processing. The game will update the next frame and process all the events. 

With an event manager, it is possible to make delayed events such as having a "idle animation event" that is sent to the event manager, but with a flag to execute after 5 seconds.

During development of this game, I've been forced to access the dispatch, store, and view from inside each compartment, breaking the coupling rules. However, as I grow more comfortable with Flux, I've noticed areas that can be de-coupled.

With a little more development, I believe it is possible to create an entire game with a generic Flux game engine, and have the entire game run on Actions.

# Security issue

1. The server-client network structure uses player id to authenticate the player. To mitigate hackers from randomly guessing and hijacking a player, the player's socket info (ip address, ip port, etc) should also be used.

# Bugs

1. Some variables should be "server-side only" such as the correct answer. Currently, this is being broadcast to everyone.

# Nice to have

1. The actions list can be automatically populated (either via metaprogramming or a register command).
2. Automatic awards:

| Award | How to detect |
| ---- | ---- |
| Least energetic to draw | broad strokes |
| Least used of ink | left click durations can be tracked |
| Attention to detail | Tiny movement of mouse during drawings |
| A lot of erasures | erasures can be tracked |
| Tries to cheat with letters! | A neural network to look for letters? |

3. More refactoring to farther decouple the dispatch, view, and store
4. More polish
5. Development logs to keep track (and visualize?) how the flux messaging flows between components
6. Code to handle players leaving
7. The addition of game rooms
8. Graceful handling of Server crashes

# Answers

Answer.txt contains the answers. These were taken from [tvtropes's indexes](http://tvtropes.org/pmwiki/index_report.php) (warning: TvTropes).