import sys
import pygame
import os
import random
import math


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
    PLAYER_VELOCITY = [70, 70, 70, 70]
    MAX_ENEMY_COUNT = [10, 15, 20, 30]
    ENEMY_FULL_HP = [150, 150, 175, 200]
    MISSILE_MAX_VELO = [60, 80, 100, 130]

    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.player = Player(game_sprite, self.PLAYER_FULL_HP[difficulty], self.PLAYER_DAMAGE[difficulty])
        self.enemy_list = []
        self.spawn_enemies(self.MAX_ENEMY_COUNT[difficulty])
        self.missile_list = []

    def spawn_enemies(self, count):
        for i in range(count):
            self.enemy_list.append(Enemy(game_sprite,
                                         random.choice(list(range(200)) + list(range(1000, 1200))),
                                         random.choice(list(range(200)) + list(range(500, 700))), self))
            self.enemy_list[i].hp = self.ENEMY_FULL_HP[self.difficulty]

    def is_pushed(self, pos):
        dx = pos[0] - self.player.x
        dy = pos[1] - self.player.y
        x = round(self.player.x + dx / abs(dx) * (self.player.rect.w / 2 + 10))
        y = round(self.player.y + dy / abs(dy) * (self.player.rect.h / 2 + 10))
        self.missile_list.append(Missile(game_sprite, x, y,
                                         self.MISSILE_MAX_VELO[self.difficulty],
                                         dx, dy, self.PLAYER_DAMAGE[self.difficulty]))

    def move(self, dir):

        if 'N' in dir:
            for enemy in self.enemy_list:
                enemy.rect.y -= self.PLAYER_VELOCITY[self.difficulty] / FPS
        if 'S' in dir:
            for enemy in self.enemy_list:
                enemy.rect.y += self.PLAYER_VELOCITY[self.difficulty] / FPS
        if 'W' in dir:
            for enemy in self.enemy_list:
                enemy.rect.x += self.PLAYER_VELOCITY[self.difficulty] / FPS
        if 'E' in dir:
            for enemy in self.enemy_list:
                enemy.rect.x -= self.PLAYER_VELOCITY[self.difficulty] / FPS

    def next(self):

        for missile in self.missile_list:
            if missile.destruct:
                self.missile_list.remove(missile)

        for enemy in self.enemy_list:
            if enemy.to_destruct:
                self.enemy_list.remove(enemy)
                self.spawn_enemies(1)

        for enemy in self.enemy_list:
            rotate(enemy, (self.player.x, self.player.y))

        rotate(self.player, (game_arrow.rect.x, game_arrow.rect.y))


def rotate(obj, pos):
    dx = pos[0] - obj.x
    dy = pos[1] - obj.y

    gip = dx ** 2 + dy ** 2

    angle = math.asin(dx ** 2 / gip)

    if dy > 0:
        angle += math.pi

    obj.image = pygame.transform.rotate(obj.image, math.degrees(angle))
    obj.rect = obj.image.get_rect()
    obj.set_coords()


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
            self.image = load_image(self.image_name, -1)

        if not self.focused and self.image_name.endswith("_focused"):
            self.image_name = self.image_name[:-8]
            self.image = load_image(self.image_name)

        if self.focused and (True in args):
            self.to_return = self.func(self)


class Arrow(pygame.sprite.Sprite):
    def __init__(self, group, image_name):
        super().__init__(group)
        self.add(arrow_sprite)
        self.image = load_image(image_name, -1)
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

    def set_coords(self):
        self.rect.x = self.x - self.rect.w // 2
        self.rect.y = self.y - self.rect.h // 2


def enemy_action(enemy, pl, gm):
    dx = pl.x - enemy.x
    dy = pl.y - enemy.y

    if dx > 0:
        enemy.x += round(enemy.max_velocity / FPS / (1 + abs(dy / dx)) ** 0.5)
    else:
        enemy.x -= round(enemy.max_velocity / FPS / (1 + abs(dy / dx)) ** 0.5)

    if dy > 0:
        enemy.y += round(enemy.max_velocity / FPS / (1 + abs(dx / dy)) ** 0.5)
    else:
        enemy.y += round(enemy.max_velocity / FPS / (1 + abs(dx / dy)) ** 0.5)

    dx = pl.x - enemy.x
    dy = pl.y - enemy.y
    x = round(enemy.x + dx / abs(dx) * (enemy.rect.w / 2 + 10))
    y = round(enemy.y + dy / abs(dy) * (enemy.rect.h / 2 + 10))
    gm.missile_list.append(Missile(game_sprite, x, y,
                                   gm.MISSILE_MAX_VELO[gm.difficulty],
                                   dx, dy, gm.PLAYER_DAMAGE[gm.difficulty]))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, group, x, y, game_mode):
        super().__init__(group)
        self.add(enemy_sprite)
        self.image = load_image("enemy.png")
        self.rect = self.image.get_rect()
        self.hp = 100
        self.damage = 10
        self.counter = 0
        self.shoot = 0
        self.max_velocity = 50
        self.x = x
        self.y = y
        self.to_destruct = False
        self.gm = game_mode
        self.rect.x, self.rect.y = self.x, self.y

    def update(self):
        self.shoot += 1
        if self.hp <= 0:
            if self.get_animation_died():
                self.to_destruct = True
                self.kill()

        enemy_action(self, current_game_mode.player, self.gm)

        self.rect.x = self.x
        self.rect.y = self.y

    def get_animation_died(self):
        self.counter += 1
        if self.counter > 60:
            return True
        return False

    def set_coords(self):
        self.rect.x = self.x
        self.rect.y = self.y


class Missile(pygame.sprite.Sprite):

    global FPS

    def __init__(self, group, x, y, max_velo, dx, dy, damage):
        super().__init__(group)
        self.add(missile_sprite)
        self.image = load_image("missile.png", -1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x, self.y = x, y
        self.max_velocity = max_velo
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.destruct = False
        rotate(self, (x + dx, y + dy))

    def update(self, *args):
        if self.dx > 0:
            self.rect.x += round(self.max_velocity / FPS / (1 + abs(self.dy / self.dx)) ** 0.5)
        else:
            self.rect.x -= round(self.max_velocity / FPS / (1 + abs(self.dy / self.dx)) ** 0.5)

        if self.dy > 0:
            self.rect.y += round(self.max_velocity / FPS / (1 + abs(self.dx / self.dy)) ** 0.5)
        else:
            self.rect.y += round(self.max_velocity / FPS / (1 + abs(self.dx / self.dy)) ** 0.5)

        target_dict = pygame.sprite.spritecollide(self, enemy_sprite, False, False)

        for target in target_dict[self]:
            target.hp -= self.damage
            self.destruct = True

        target_player = pygame.sprite.spritecollideany(self, player_sprite)

        if target_player is not None:
            target_player.hp -= self.damage
            self.destruct = True

        if self.destruct:
            self.kill()

    def set_coords(self):
        self.rect.x = self.x
        self.rect.y = self.y


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


def change_gm():
    pass


def change_df(btn):
    if current_game_mode.difficulty == 3:
        current_game_mode.difficulty == 0
    else:
        current_game_mode.difficulty += 1

    btn.image = load_image("difficulty_" + current_game_mode.difficulty + ".png")


def setup_game_screen():

    loc_pressed = False

    global menu_background, screen, current_game_mode

    menu_sprite = pygame.sprite.Group()
    menu_arrow_sprite = pygame.sprite.Group()

    current_game_mode = GameModeArena(1)

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
missile_sprite = pygame.sprite.Group()
button_sprite = pygame.sprite.Group()
arrow_sprite = pygame.sprite.Group()
game_arrow_sprite = pygame.sprite.Group()


game_arrow = Arrow(game_arrow_sprite, "game_arrow.png")

current_game_mode = None

start_screen()

menu_background = load_image("menu_background.png")
background = load_image("background_game.png")

while running:

    dirs = ''

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu_screen()  # open menu
            if event.key == pygame.K_a:
                dirs += 'W'
            if event.key == pygame.K_d:
                dirs += 'E'
            if event.key == pygame.K_w:
                dirs += 'N'
            if event.key == pygame.K_s:
                dirs += 'S'
        if event.type == pygame.MOUSEBUTTONDOWN:
            current_game_mode.is_pushed(event.pos)
        if event.type == pygame.MOUSEMOTION:
            game_arrow.rect.x = event.pos[0]
            game_arrow.rect.y = event.pos[1]

    screen.blit(pygame.transform.scale(background,
                                       (screen.get_width(),
                                        screen.get_height())), (0, 0))

    current_game_mode.move(dirs)
    current_game_mode.next()

    game_sprite.update()
    game_sprite.draw(screen)

    game_arrow_sprite.update()
    game_arrow_sprite.draw(screen)

    pygame.display.flip()

    if lock_fps:
        clock.tick(FPS)

terminate()
