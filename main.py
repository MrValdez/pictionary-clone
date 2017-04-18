import os
import pygame

os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.init()

resolution = [1024, 768]
screen = pygame.display.set_mode(resolution)
pygame.display.set_caption("Pictionary clone")
clock = pygame.time.Clock()

isRunning = True
while isRunning:
    screen.fill([255, 255, 255])
    pygame.display.update()
    clock.tick(60)

    for event in pygame.event.get():
        if (event.type == pygame.QUIT or
           (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
            pygame.quit()
            isRunning = False
