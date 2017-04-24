import engine
import pygame

game = engine.GameEngine()

isRunning = True
while isRunning:
    game.draw()
    game.update()

    for event in pygame.event.get():
        if (event.type == pygame.QUIT or
           (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
            pygame.quit()
            isRunning = False
