import pygame


class Screen:

    def __init__(self):
        self.widget_list = []
        self.wigets_to_return = []
        self.menu_sprite = pygame.sprite.Group()
        self.arrow_sprite = pygame.sprite.Group()

    def add(self, widget, to_return=False):
        self.widget_list.append(widget)
        if to_return:
            self.wigets_to_return.append(widget)

    def add_arrow(self, widget):
        self.arrow = widget

    def run(self, current_game_mode, screen):
        pygame.mixer.music.stop()
        pygame.mixer.music.load("data\Music\menu_soundtrack.wav")
        pygame.mixer.music.play(-1, 0.0)
        loc_pressed = True

        menu_background = load_image("menu_background.png")

        while True:
            for loc_event in pygame.event.get():
                if loc_event.type == pygame.MOUSEBUTTONDOWN:
                    loc_pressed = True
                else:
                    loc_pressed = False
                if loc_event.type == pygame.MOUSEMOTION:
                    arrow.rect.x = loc_event.pos[0]
                    arrow.rect.y = loc_event.pos[1]
                if loc_event.type == pygame.KEYDOWN:
                    if loc_event.key == pygame.K_ESCAPE:
                        reset_sprites(arrow,
                                      lbl_game_over,
                                      button_quit,
                                      button_new_game)
                        pygame.mixer.music.stop()
                        return

            screen.blit(pygame.transform.scale(menu_background,
                                               (screen.get_width(),
                                                screen.get_height())), (0, 0))
