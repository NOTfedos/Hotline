import sys
import pygame
import os


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class GameModeArena:

    PLAYER_FULL_HP = [200, 150, 100, 50]
    PLAYER_DAMAGE = [100, 75, 75, 50]
    MAX_ENEMY_COUNT = [10, 15, 20, 30]

    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.player = Player(game_sprite, self.PLAYER_FULL_HP[difficulty], self.PLAYER_DAMAGE[difficulty])
        self.enemy_list = []
        self.spawn_enemies()

    def spawn_enemies(self):
        pass


class Button(pygame.sprite.Sprite):
    def __init__(self, group, image_name, x, y, func):
        super().__init__(group)
        self.add(button_sprite)
        self.image_name = image_name
        self.image = load_image(image_name)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.func = func
        self.focused = False
        self.to_return = False

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, arrow_sprite):
            self.focused = True
        else:
            self.focused = False

        if self.focused and not(self.image_name.endswith("_focused")):
            self.image_name = self.image_name + "_focused"
            self.image = load_image(self.image_name)

        if not self.focused and self.image_name.endswith("_focused"):
            self.image_name = self.image_name[:-8]
            self.image = load_image(self.image_name)

        if self.focused and (True in args):
            self.to_return = self.func(self)


class Arrow(pygame.sprite.Sprite):
    def __init__(self, group, image_name):
        super().__init__(group)
        self.add(arrow_sprite)
        self.image = load_image(image_name)
        self.rect = self.image.get_rect()

    def update(self, *args):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, group, full_hp, damage):
        super().__init__(group)
        self.add(player_sprite)
        self.image = load_image("player.png")
        self.rect = self.image.get_rect()
        self.x = screen.get_width() // 2
        self.y = screen.get_height() // 2
        self.hp = full_hp
        self.damage = damage

    def update(self):
        if self.hp <= 0:
            game_over_screen()
            return
        col_dict = pygame.sprite.spritecollide(self, enemy_sprite, False, False)
        for enemy in col_dict[self]:
            if self.hp >= enemy.hp:
                self.hp -= enemy.hp
                enemy.hp = 0
            else:
                self.hp = 0


def enemy_action(enemy, pl):
    dx = pl.x - enemy.x
    dy = pl.y - enemy.y

    if dx > 0:
        enemy.x += round(enemy.max_velocity / (1 + abs(dy / dx)) ** 0.5)
    else:
        enemy.x -= round(enemy.max_velocity / (1 + abs(dy / dx)) ** 0.5)

    if dy > 0:
        enemy.y += round(enemy.max_velocity / (1 + abs(dx / dy)) ** 0.5)
    else:
        enemy.y += round(enemy.max_velocity / (1 + abs(dx / dy)) ** 0.5)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.add(enemy_sprite)
        self.image = load_image("enemy.png")
        self.rect = self.image.get_rect()
        self.hp = 100
        self.damage = 10
        self.counter = 0
        self.shoot = 0
        self.max_velocity

    def update(self):
        self.shoot += 1
        if self.hp <= 0:
            if self.get_animation_died():
                self.kill()

        enemy_action(self, current_game_mode.player)

    def get_animation_died(self):
        self.counter += 1
        if self.counter > 60:
            return True
        return False


def label_func():
    return True


def start_screen():

    loc_pressed = False

    global menu_background, screen

    menu_sprite = pygame.sprite.Group()
    menu_arrow_sprite = pygame.sprite.Group()

    arrow = Arrow(menu_arrow_sprite, "menu_arrow.png")
    button_new_game = Button(menu_sprite, "new_game.png",
                             screen.get_width() // 2,
                             round(screen.get_height() * 0.8),
                             label_func)
    button_options = Button(menu_sprite, "options.png",
                            screen.get_width() // 2,
                            round(screen.get_height() * 0.85), options_screen)
    button_quit = Button(menu_sprite, "quit.png",
                         screen.get_width() // 2,
                         round(screen.get_height() * 0.9),
                         ready_quit_screen)
    lbl_start = Button(menu_sprite, "start.png", 0, 0, label_func)
    lbl_start.rect.x = (screen.get_width() - lbl_start.rect.w) // 2
    lbl_start.rect.y = round(screen.get_height() * 0.3)

    while True:
        for loc_event in pygame.event.get():
            if loc_event.type == pygame.QUIT:
                ready_quit_screen()
            if loc_event.type == pygame.MOUSEBUTTONDOWN:
                loc_pressed = True
            else:
                loc_pressed = False
            if loc_event.type == pygame.MOUSEMOTION:
                arrow.rect.x = event.pos[0]
                arrow.rect.y = event.pos[1]
            if loc_event.type == pygame.KEYDOWN:
                if loc_event.key == pygame.K_ESCAPE:
                    ready_quit_screen()

        screen.blit(pygame.transform.scale(menu_background,
                                           (screen.get_width(),
                                            screen.get_height())), 0, 0)

        if button_new_game.to_return:
            reset_sprites(button_new_game,
                          button_options,
                          button_quit,
                          arrow,
                          lbl_start)
            if not (setup_game_screen()):
                return
        if button_quit.to_return:
            reset_sprites(button_new_game,
                          button_options,
                          button_quit,
                          arrow,
                          lbl_start)
            return

        menu_sprite.update(loc_pressed)
        menu_sprite.draw(screen)

        menu_arrow_sprite.update()
        menu_arrow_sprite.draw(screen)

        pygame.display.flip()


def setup_game_screen():

    loc_pressed = False

    global menu_background, screen, current_game_mode

    menu_sprite = pygame.sprite.Group()
    menu_arrow_sprite = pygame.sprite.Group()

    current_game_mode = GameModeArena()

    arrow = Arrow(menu_arrow_sprite, "menu_arrow.png")
    button_options = Button(menu_sprite, "options.png",
                            screen.get_width() // 2,
                            round(screen.get_height() * 0.85),
                            options_screen)
    button_back = Button(menu_sprite, "back.png",
                         round(screen.get_width() * 2 / 3),
                         round(screen.get_height() * 0.9),
                         start_screen)

    button_game_mode = Button(menu_sprite, "press_to_select_gm.png",
                              screen.get_width() // 3,
                              round(screen.get_height() * 0.7),
                              change_gm)

    button_difficulty = Button(menu_sprite, "press_to_select_df.png",
                               round(screen.get_width() * 2 / 3),
                               round(screen.get_height() * 0.7),
                               change_df)

    button_quit = Button(menu_sprite, "quit.png",
                         screen.get_width() // 2,
                         round(screen.get_height() * 0.9),
                         ready_quit_screen)

    button_next = Button(menu_sprite, "next.png",
                         round(screen.get_width() * 1.5),
                         round(screen.get_height() * 0.85),
                         label_func)

    while True:
        for loc_event in pygame.event.get():
            if loc_event.type == pygame.QUIT:
                ready_quit_screen()
            if loc_event.type == pygame.MOUSEBUTTONDOWN:
                loc_pressed = True
            else:
                loc_pressed = False
            if loc_event.type == pygame.MOUSEMOTION:
                arrow.rect.x = event.pos[0]
                arrow.rect.y = event.pos[1]
            if loc_event.type == pygame.KEYDOWN:
                if loc_event.key == pygame.K_ESCAPE:
                    ready_quit_screen()

        screen.blit(pygame.transform.scale(menu_background,
                                           (screen.get_width(),
                                            screen.get_height())), 0, 0)

        if button_back.to_return:
            reset_sprites(arrow,
                          button_back,
                          button_quit,
                          button_options,
                          button_difficulty,
                          button_game_mode)
            return True
        if button_next.to_return:
            reset_sprites(arrow,
                          button_back,
                          button_quit,
                          button_options,
                          button_difficulty,
                          button_game_mode)
            return False

        menu_sprite.update(loc_pressed)
        menu_sprite.draw(screen)

        menu_arrow_sprite.update()
        menu_arrow_sprite.draw(screen)

        pygame.display.flip()


def ready_quit_screen():

    loc_pressed = False

    global menu_background, screen

    menu_sprite = pygame.sprite.Group()
    menu_arrow_sprite = pygame.sprite.Group()

    arrow = Arrow(menu_arrow_sprite, "menu_arrow.png")

    lbl_ready = Button(menu_sprite, "ready_quit.png",
                       screen.get_width() // 2,
                       round(screen.get_height() * 0.3),
                       label_func)

    button_yes = Button(menu_sprite, "yes.png",
                        round(screen.get_width() * 2 / 3),
                        round(screen.get_height() * 0.85),
                        terminate)

    button_no = Button(menu_sprite, "no.png",
                       round(screen.get_width() / 3),
                       round(screen.get_height() * 0.85),
                       label_func)

    while True:
        for loc_event in pygame.event.get():
            if loc_event.type == pygame.MOUSEBUTTONDOWN:
                loc_pressed = True
            else:
                loc_pressed = False
            if loc_event.type == pygame.MOUSEMOTION:
                arrow.rect.x = event.pos[0]
                arrow.rect.y = event.pos[1]
            if loc_event.type == pygame.KEYDOWN:
                if loc_event.key == pygame.K_ESCAPE:
                    reset_sprites(arrow,
                                  lbl_ready,
                                  button_yes,
                                  button_no)
                    return

        screen.blit(pygame.transform.scale(menu_background,
                                           (screen.get_width(),
                                            screen.get_height())), 0, 0)

        if button_no.to_return:
            reset_sprites(arrow,
                          lbl_ready,
                          button_yes,
                          button_no)
            return

        menu_sprite.update(loc_pressed)
        menu_sprite.draw(screen)

        menu_arrow_sprite.update()
        menu_arrow_sprite.draw(screen)

        pygame.display.flip()


def menu_screen():

    loc_pressed = True

    global screen, menu_background

    menu_sprite = pygame.sprite.Group()
    menu_arrow_sprite = pygame.sprite.Group()

    arrow = Arrow(menu_arrow_sprite, "menu_arrow.png")
    button_quit = Button(menu_sprite, "quit.png",
                         screen.get_width() // 2,
                         round(screen.get_height() * 0.9),
                         ready_quit_screen)
    button_back = Button(menu_sprite, "back.png",
                         round(screen.get_width() * 2 / 3),
                         round(screen.get_height() * 0.9),
                         label_func)
    button_options = Button(menu_sprite, "options.png",
                            screen.get_width() // 2,
                            round(screen.get_height() * 0.85),
                            options_screen)
    button_new_game = Button(menu_sprite, "new_game.png",
                             screen.get_width() // 2,
                             round(screen.get_height() * 0.8),
                             setup_game_screen)
    lbl_pause = Button(menu_sprite, "pause.png",
                       screen.get_width() // 2,
                       round(screen.get_height() * 0.3),
                       label_func)

    while True:
        for loc_event in pygame.event.get():
            if loc_event.type == pygame.MOUSEBUTTONDOWN:
                loc_pressed = True
            else:
                loc_pressed = False
            if loc_event.type == pygame.MOUSEMOTION:
                arrow.rect.x = event.pos[0]
                arrow.rect.y = event.pos[1]
            if loc_event.type == pygame.KEYDOWN:
                if loc_event.key == pygame.K_ESCAPE:
                    reset_sprites(arrow,
                                  lbl_pause,
                                  button_quit,
                                  button_back,
                                  button_options,
                                  button_new_game)
                    return

        screen.blit(pygame.transform.scale(menu_background,
                                           (screen.get_width(),
                                            screen.get_height())), 0, 0)

        if button_back.to_return:
            reset_sprites(arrow,
                          lbl_pause,
                          button_quit,
                          button_back,
                          button_options,
                          button_new_game)
            return

        menu_sprite.update(loc_pressed)
        menu_sprite.draw(screen)

        menu_arrow_sprite.update()
        menu_arrow_sprite.draw(screen)

        pygame.display.flip()


def game_over_screen():
    loc_pressed = True

    global screen, menu_background

    menu_sprite = pygame.sprite.Group()
    menu_arrow_sprite = pygame.sprite.Group()

    arrow = Arrow(menu_arrow_sprite, "menu_arrow.png")
    lbl_game_over = Button(menu_sprite, "pause.png",
                           screen.get_width() // 2,
                           round(screen.get_height() * 0.3),
                           label_func)
    button_quit = Button(menu_sprite, "quit.png",
                         screen.get_width() // 2,
                         round(screen.get_height() * 0.9),
                         ready_quit_screen)
    button_new_game = Button(menu_sprite, "new_game.png",
                             screen.get_width() // 2,
                             round(screen.get_height() * 0.8),
                             setup_game_screen)

    while True:
        for loc_event in pygame.event.get():
            if loc_event.type == pygame.MOUSEBUTTONDOWN:
                loc_pressed = True
            else:
                loc_pressed = False
            if loc_event.type == pygame.MOUSEMOTION:
                arrow.rect.x = event.pos[0]
                arrow.rect.y = event.pos[1]
            if loc_event.type == pygame.KEYDOWN:
                if loc_event.key == pygame.K_ESCAPE:
                    reset_sprites(arrow,
                                  lbl_game_over,
                                  button_quit,
                                  button_new_game)
                    return

        screen.blit(pygame.transform.scale(menu_background,
                                           (screen.get_width(),
                                            screen.get_height())), 0, 0)

        if button_new_game.to_return:
            reset_sprites(button_new_game,
                          button_quit,
                          arrow,
                          lbl_game_over)
            if not (setup_game_screen()):
                return

        menu_sprite.update(loc_pressed)
        menu_sprite.draw(screen)

        menu_arrow_sprite.update()
        menu_arrow_sprite.draw(screen)

        pygame.display.flip()


def options_screen():
    pass


def reset_sprites(*args):
    for el in args:
        el.kill()


def terminate():
    pygame.quit()
    sys.exit()


running = True
lock_fps = True
screen = pygame.display.set_mode((1280, 720))
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

FPS = 60

# GAME_MODES = {'ARENA': arena_action, 'LEVEL': level_action}

game_sprite = pygame.sprite.Group()
enemy_sprite = pygame.sprite.Group()
player_sprite = pygame.sprite.Group()
button_sprite = pygame.sprite.Group()
arrow_sprite = pygame.sprite.Group()
game_arrow_sprite = pygame.sprite.Group()


game_arrow = Arrow(game_arrow_sprite, "game_arrow.png")

current_game_mode = None

start_screen()

menu_background = load_image("menu_background.png")
background = load_image("background_game.png")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu_screen()  # open menu
        if event.type == pygame.MOUSEBUTTONDOWN:
            current_game_mode.is_pushed(event.pos)
        if event.type == pygame.MOUSEMOTION:
            game_arrow.rect.x = event.pos[0]
            game_arrow.rect.y = event.pos[1]

    screen.blit(pygame.transform.scale(background,
                                       (screen.get_width(),
                                        screen.get_height())), (0, 0))

    current_game_mode.next()

    game_sprite.update()
    game_sprite.draw(screen)

    game_arrow_sprite.update()
    game_arrow_sprite.draw(screen)

    pygame.display.flip()

    if lock_fps:
        clock.tick(FPS)

terminate()
