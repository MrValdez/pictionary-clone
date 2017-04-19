import pygame

pen_color = [0, 0, 0]
drawing_pad_color = [255, 255, 155]
drawing_size = [500, 500]


class pad:
    def __init__(self, pos, scale=1):
        self.surface = pygame.Surface(drawing_size)
        self.scale = scale
        self.surface.fill(drawing_pad_color)
        self.pos = pos

    def draw(self, screen):
        scaled_size = list(map(lambda x: int(x * self.scale), drawing_size))
        surface = pygame.transform.scale(self.surface, scaled_size)

        # draw border
        pygame.draw.rect(screen,
                         [0, 0, 0],
                         surface.get_rect().move(self.pos),
                         10)

        screen.blit(surface, self.pos)

    def draw_brush(self, pos):
        self.apply_brush(pos, pen_color)

    def erase_brush(self, pos):
        self.apply_brush(pos, drawing_pad_color)

    def apply_brush(self, pos, color):
        # offset mouse position by the drawing area
        pos = [pos[0] - self.pos[0],
               pos[1] - self.pos[1]]

        pygame.draw.circle(self.surface,
                           color,
                           pos,
                           10)
