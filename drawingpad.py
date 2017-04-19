import pygame

pen_color = [0, 0, 0]
drawing_pad_color = [255, 255, 155]

class pad:
    def __init__(self):

        drawing_size = [500, 500]
        self.surface = pygame.Surface(drawing_size)
        self.surface.fill(drawing_pad_color)
        self.pos = [40, 40]

    def draw(self, screen):
        pygame.draw.rect(screen,
                         [0, 0, 0],
                         self.surface.get_rect().move(self.pos),
                         10)  # draw border
        screen.blit(self.surface, self.pos)

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
