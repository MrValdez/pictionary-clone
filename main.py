import os
import pygame

os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.init()

resolution = [1024, 768]
screen = pygame.display.set_mode(resolution)
pygame.display.set_caption("Pictionary clone")
clock = pygame.time.Clock()

drawing_size = [500, 500]
drawing_pad = pygame.Surface(drawing_size)
drawing_pad.fill([255, 255, 155])
drawing_pad_pos = [40, 40]

isRunning = True
while isRunning:
    screen.fill([255, 255, 255])

    pygame.draw.rect(screen,
                     [0, 0, 0],
                     drawing_pad.get_rect().move(drawing_pad_pos),
                     10)  # draw border
    screen.blit(drawing_pad, drawing_pad_pos)

    if pygame.mouse.get_pressed()[0]:
        color = [0, 0, 0]
        mouse_pos = pygame.mouse.get_pos()

        # offset mouse position by the drawing area
        mouse_pos = [mouse_pos[0] - drawing_pad_pos[0],
                     mouse_pos[1] - drawing_pad_pos[1]]

        pygame.draw.circle(drawing_pad,
                           color,
                           mouse_pos,
                           10)
        mouse_movements = pygame.mouse.get_rel()
        print(mouse_movements)

    pygame.display.update()
    clock.tick(60)
    for event in pygame.event.get():
        if (event.type == pygame.QUIT or
           (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
            pygame.quit()
            isRunning = False
