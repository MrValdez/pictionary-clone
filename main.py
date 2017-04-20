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

player_name = "Sir Lancelot the Brave"
client = network.client(player_name)

main_pad = pad([40, 40], network_connection=client)
p2_pad = pad([700, 40], scale=.45)
p3_pad = pad([700, 300], scale=.45)


def update_drawing_pad(pad_id, mouse_down, mouse_pos):
    pad_to_update = None
    if pad_id == 0:
        pad_to_update = p2_pad
    if pad_id == 1:
        pad_to_update = p3_pad

    if pad_to_update:
        pad_to_update.update(mouse_down, mouse_pos, use_screen_pos=False)

for pad_id, history in enumerate(client.current_game_state["History"]):
    for draw_command in history:
        mouse_down, pos = draw_command
        update_drawing_pad(pad_id, mouse_down, pos)

isRunning = True
while isRunning:
    screen.fill([255, 255, 255])

    main_pad.draw(screen)
    p2_pad.draw(screen)
    p3_pad.draw(screen)

    mouse_down = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    main_pad.update(mouse_down, mouse_pos)

    while True:
        network_data = client.update()
        if not network_data:
            break

        pad_id, mouse_down, mouse_pos = network_data
        update_drawing_pad(pad_id, mouse_down, mouse_pos)

    pygame.display.update()
    clock.tick(60)
    for event in pygame.event.get():
        if (event.type == pygame.QUIT or
           (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
            pygame.quit()
            isRunning = False
