import os
import pygame
import flux_game

button_back_color = [255, 128, 255]
button_width = 50
timer_to_next_question = 1000


class View:
    def __init__(self):
        self.engine = None
        self.screen = None

    def attach_engine(self, engine):
        self.engine = engine

    def send_action(self, action, data):
        self.engine.apply(action)

    def draw(self):
        if self.screen is None:
            return

        self.engine.gamestate.draw(self.screen)

    def update(self):
        pass

class BaseView(View):
    pass

class ClientView(View):
    """
    This is handles the input and output from the client
    """

    def __init__(self):
        super(ClientView, self).__init__()
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.font.init()

        self.resolution = [1024, 768]
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption("Pictionary clone")

        self.NormalText = pygame.font.Font(None, 25)
        self.ui_points_pos = [970, 700]

        self.prev_mouse_down = pygame.mouse.get_pressed()

        self.buttons = []

    def draw(self):
        super(ClientView, self).draw()

        screen = self.screen
        screen.fill([255, 255, 255])

        self.engine.gamestate.main_pad.draw(screen)

        if not self.engine.gamestate.is_current_active_player():
            self.generate_buttons(start_pos=[600, 30], max_width=self.resolution[0])
            self.draw_answers(screen)

        self.draw_messages(screen, pos_y=600)
        self.draw_points(screen)

        pygame.display.update()

    def update(self):
        mouse_down = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if any(mouse_down):
            data = {"mouse_down": mouse_down,
                    "pos": mouse_pos}
            action = flux_game.Action_Draw(data)
            self.send_action(action, data)

        self.prev_mouse_down = mouse_down

    def draw_messages(self, screen, pos_y):
        for message in self.engine.gamestate.messages:
            output = self.NormalText.render(message, True, [0, 0, 0])
            screen.blit(output, [40, pos_y])
            pos_y += output.get_height() + 10

    def draw_points(self, screen):
        points = self.engine.gamestate.points
        points_text = self.NormalText.render(
            "{} pts".format(points), True, [0, 0, 0])
        pygame.draw.circle(screen,
                           [255, 128, 128],
                           self.ui_points_pos,
                           points_text.get_width() + 10)
        points_pos = points_text.get_rect()
        points_pos.center = self.ui_points_pos
        screen.blit(points_text,  points_pos)


    # Stage_select_word
    def generate_buttons(self, start_pos, max_width, padding=10):
        self.button_renders = []

        answers = self.engine.gamestate.choices
        current_x, current_y = start_pos
        max_height = 0
        for answer in answers:
            output = self.NormalText.render(answer, True, [0, 0, 0])
            pos = [current_x, current_y]
            rect = (output.get_rect()
                    .move(*pos)
                    .inflate(button_width, button_width / 2))
            max_height = max(max_height, rect.height + padding)

            if rect.right >= max_width:
                current_x = start_pos[0]
                current_y += max_height
                rect.move_ip(-pos[0], -pos[1])
                rect.move_ip(current_x, current_y)
                pos = [current_x, current_y]
                max_height = 0

            self.button_renders.append([output, rect, pos])
            current_x += rect.width + padding

    def draw_answers(self, screen):
        for output, rect, pos in self.button_renders:
            pygame.draw.rect(screen,
                             button_back_color,
                             rect)
            screen.blit(output, pos)
