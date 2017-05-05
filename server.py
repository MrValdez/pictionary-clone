import engine
import view
import network
import pygame

network = network.NetworkServer()
server = engine.Engine(network=network)

isRunning = True
while isRunning:
    try:
        server.update()
    except KeyboardInterrupt:
        isRunning = False
