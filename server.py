import flux_engine as engine
import flux_view as view
import flux_network as network
import pygame

network = network.NetworkServer()
server = engine.Engine(network=network)

isRunning = True
while isRunning:
    try:
        server.update()
    except KeyboardInterrupt:
        isRunning = False