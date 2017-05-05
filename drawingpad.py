import pygame

pen_color = [0, 0, 0]
drawing_pad_color = [255, 255, 155]
drawing_size = [500, 500]


class pad:
    def __init__(self, screen_pos, scale=1, network_connection=None):
        self.surface = pygame.Surface(drawing_size)
        self.clear()

        self.scale = scale
        self.screen_pos = screen_pos
        self.drawing_delta = 0
        self.network_connection = network_connection

        self.history = []

    def move(self, new_pos):
        self.screen_pos = new_pos[:]

    def clear(self):
        self.surface.fill(drawing_pad_color)

    def draw(self, screen):
        scaled_size = list(map(lambda x: int(x * self.scale), drawing_size))
        surface = pygame.transform.scale(self.surface, scaled_size)

        # draw border
        pygame.draw.rect(screen,
                         [0, 0, 0],
                         surface.get_rect().move(self.screen_pos),
                         10)

        screen.blit(surface, self.screen_pos)

    def update(self, mouse_down, pos, use_screen_pos=True):
        if not any(mouse_down):
            return

        if use_screen_pos:
            # offset mouse position by the drawing area
            pos = [pos[0] - self.screen_pos[0],
                   pos[1] - self.screen_pos[1]]

        if mouse_down[0]:
            self.draw_brush(pos)

        if mouse_down[2]:
            self.erase_brush(pos)

        if self.network_connection:
            self.network_connection.send_draw_command(mouse_down, pos)

    def draw_brush(self, pad_xy):
        self.apply_brush(pad_xy, pen_color)

    def erase_brush(self, pad_xy):
        self.apply_brush(pad_xy, drawing_pad_color)

    def apply_brush(self, pos, color):
        pygame.draw.circle(self.surface,
                           color,
                           pos,
                           10)
        self.history.append([pos, color])
