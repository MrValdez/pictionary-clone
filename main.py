import network
import os
import pygame
from drawingpad import pad

os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.init()

resolution = [1024, 768]
screen = pygame.display.set_mode(resolution)
pygame.display.set_caption("Pictionary clone")
clock = pygame.time.Clock()

main_pad = pad([40, 40])
p2_pad = pad([700, 40], scale=.45)
p3_pad = pad([700, 300], scale=.45)

drawing_delta = 0

client = network.client()

for history in client.current_game_state:
    mouse_down, pos = history
    p2_pad.update(mouse_down, pos, use_screen_pos=False)

isRunning = True
while isRunning:
    screen.fill([255, 255, 255])

    main_pad.draw(screen)
    p2_pad.draw(screen)
    p3_pad.draw(screen)

    mouse_down = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    main_pad.update(mouse_down, mouse_pos)

    network_data = client.update()
    if network_data:
        mouse_down, mouse_pos = network_data
        p2_pad.update(mouse_down, mouse_pos, use_screen_pos=False)

    pygame.display.update()
    clock.tick(60)
    for event in pygame.event.get():
        if (event.type == pygame.QUIT or
           (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
            pygame.quit()
            isRunning = False
