import os
import pygame

os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.init()

resolution = [1024, 768]
screen = pygame.display.set_mode(resolution)
pygame.display.set_caption("Pictionary clone")
clock = pygame.time.Clock()

pen_color = [0, 0, 0]
drawing_pad_color = [255, 255, 155]

drawing_size = [500, 500]
drawing_pad = pygame.Surface(drawing_size)
drawing_pad.fill(drawing_pad_color)
drawing_pad_pos = [40, 40]

isRunning = True
while isRunning:
    screen.fill([255, 255, 255])

    pygame.draw.rect(screen,
                     [0, 0, 0],
                     drawing_pad.get_rect().move(drawing_pad_pos),
                     10)  # draw border
    screen.blit(drawing_pad, drawing_pad_pos)

    mouse_down = pygame.mouse.get_pressed()
    if mouse_down[0] or mouse_down[2]:
        color = pen_color if mouse_down[0] else drawing_pad_color
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
