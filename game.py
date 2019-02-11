import sys
import pygame
import os
import random
import math


def load_image(name, colorkey=None):
    fullname = os.path.join('data\sprites', name)
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
    PLAYER_DAMAGE = [120, 100, 75, 50]
    PLAYER_VELOCITY = [350, 340, 330, 320]
    MAX_ENEMY_COUNT = [3, 5, 7, 15]
    ENEMY_FULL_HP = [150, 150, 175, 200]
    MISSILE_MAX_VELO = [400, 420, 440, 460]

    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.player = Player(game_sprite, self.PLAYER_FULL_HP[difficulty], self.PLAYER_DAMAGE[difficulty])
        self.enemy_list = []
        self.spawn_enemies(self.MAX_ENEMY_COUNT[difficulty])
        self.missile_list = []

    def spawn_enemies(self, count):
        for k in range(count):
            self.enemy_list.append(Enemy(game_sprite,
                                         random.choice(list(range(200)) + list(range(1000, 1200))),
                                         random.choice(list(range(200)) + list(range(500, 700))), self))
            self.enemy_list[k].hp = self.ENEMY_FULL_HP[self.difficulty]

    def is_pushed(self, pos):
        dx = pos[0] - self.player.x
        dy = pos[1] - self.player.y
        self.missile_list.append(Missile(game_sprite, self.player.x, self.player.y,
                                         self.MISSILE_MAX_VELO[self.difficulty],
                                         dx, dy, self.PLAYER_DAMAGE[self.difficulty]))

        self.missile_list[-1].move()

    def move(self, direction):
        if 'N' in direction:
            for enemy in self.enemy_list:
                enemy.y += round(self.PLAYER_VELOCITY[self.difficulty] / FPS)
            # for i in range(len(self.missile_list)):
                # self.missile_list[i].y += round(self.PLAYER_VELOCITY[self.difficulty] / FPS)

            for missile in self.missile_list:
                missile.y += round(self.PLAYER_VELOCITY[self.difficulty] / FPS)
        if 'S' in direction:
            for enemy in self.enemy_list:
                enemy.y -= round(self.PLAYER_VELOCITY[self.difficulty] / FPS)
            for missile in self.missile_list:
                missile.y -= round(self.PLAYER_VELOCITY[self.difficulty] / FPS)
        if 'W' in direction:
            for enemy in self.enemy_list:
                enemy.x += round(self.PLAYER_VELOCITY[self.difficulty] / FPS)
            for missile in self.missile_list:
                missile.x += round(self.PLAYER_VELOCITY[self.difficulty] / FPS)
        if 'E' in direction:
            for enemy in self.enemy_list:
                enemy.x -= round(self.PLAYER_VELOCITY[self.difficulty] / FPS)
            for missile in self.missile_list:
                missile.x -= round(self.PLAYER_VELOCITY[self.difficulty] / FPS)

    def next(self):

        for missile in self.missile_list:
            if missile.destruct:
                self.missile_list.remove(missile)

        for enemy in self.enemy_list:
            if enemy.to_destruct:
                self.enemy_list.remove(enemy)
                self.spawn_enemies(1)

        for enemy in self.enemy_list:
            enemy.image, enemy.rect = rot_center(load_image(enemy.name_image), enemy.rect,
                                                 get_angle(enemy, (self.player.x, self.player.y)))

        self.player.image, self.player.rect = rot_center(load_image('player.png'),
                                                         self.player.rect,
                                                         get_angle(self.player, (game_arrow.rect.x, game_arrow.rect.y)))

    def is_end(self):
        if self.player.hp <= 0:
            return True
        return False


def get_angle(obj, pos):
    dx = pos[0] - obj.x
    dy = pos[1] - obj.y

    gip = dx ** 2 + dy ** 2

    angle = math.asin(dx ** 2 / gip)

    if dx < 0:
        angle *= -1

    if dy > 0:
        angle += math.pi
    else:
        angle *= -1

    return math.degrees(angle)

    # obj.image = pygame.transform.rotate(obj.image, math.degrees(math.atan(dy / dx)))
    # obj.rect = obj.image.get_rect()
    # obj.set_coords()


def rot_center(image, rect, angle):
    """rotate an image while keeping its center"""
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image, rot_rect


class Button(pygame.sprite.Sprite):
    def __init__(self, group, image_name, x, y, func, label=False):
        super().__init__(group)
        self.add(button_sprite)
        self.image_name = image_name
        self.image = load_image(image_name, -1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.func = func
        self.focused = False
        self.to_return = False
        self.label = label
        self.sound = pygame.mixer.Sound("data\Music\sound_click.wav")

    def update(self, *args):
        if self.rect.collidepoint((args[1].rect.x, args[1].rect.y)):
            self.focused = True
        else:
            self.focused = False
        if not self.label:
            if self.focused and not(self.image_name.endswith("_focused.png")):
                self.play_sound()
                self.image_name = self.image_name[:-4] + "_focused.png"
                self.image = load_image(self.image_name, -1)
                self.rect.x -= 50

            if not self.focused and self.image_name.endswith("_focused.png"):
                self.image_name = self.image_name[:-12] + '.png'
                self.image = load_image(self.image_name)
                self.rect.x += 50

        if self.focused and (True in args):
            self.play_sound()
            self.to_return = self.func(self)

    def play_sound(self):
        # if not self.label:
            # self.sound.play()
        pass


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
        self.set_coords()
        self.hp = full_hp
        self.damage = damage

    def update(self):
        pass

    def set_coords(self):
        self.rect.x = self.x - self.rect.w // 2
        self.rect.y = self.y - self.rect.h // 2


def enemy_action(enemy, pl, gm):

    if enemy.hp >= 0:
        enemy.move()

    dx = pl.x - enemy.x
    dy = pl.y - enemy.y
    if dx > 0:
        x = round(enemy.x + (enemy.rect.w / 2 + 10))
    else:
        x = round(enemy.x - (enemy.rect.w / 2 - 10))
    if dy > 0:
        y = round(enemy.y + (enemy.rect.h / 2 + 10))
    else:
        y = round(enemy.y - (enemy.rect.h / 2 - 10))
    if enemy.shoot > 60:
        gm.missile_list.append(Missile(game_sprite, x, y,
                                       gm.MISSILE_MAX_VELO[gm.difficulty],
                                       dx, dy, gm.PLAYER_DAMAGE[gm.difficulty]))
        enemy.shoot = 0


class Enemy(pygame.sprite.Sprite):
    def __init__(self, group, x, y, game_mode):
        super().__init__(group)
        self.add(enemy_sprite)
        self.name_image = 'enemy.png'
        self.image = load_image(self.name_image)
        self.rect = self.image.get_rect()
        self.hp = 100
        self.damage = 10
        self.counter = 0
        self.shoot = 0
        self.max_velocity = 320
        self.x = x
        self.y = y
        self.to_destruct = False
        self.gm = game_mode
        self.set_coords()
        self.sin = 1
        self.cos = 0

    def update(self):
        self.shoot += 1
        if self.hp <= 0:
            self.name_image = 'enemy_killed.png'
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

        self.rect.x = self.x - (self.rect.w // 2)
        self.rect.y = self.y - (self.rect.h // 2)

    def move(self):
        dx = self.gm.player.x - self.x
        dy = self.gm.player.y - self.y

        gip = (dx ** 2 + dy ** 2) ** 0.5

        self.cos = dx / gip
        self.sin = dy / gip

        self.x += round(self.max_velocity / FPS * self.cos)
        self.y += round(self.max_velocity / FPS * self.sin)

        self.set_coords()


class Missile(pygame.sprite.Sprite):

    global FPS

    def __init__(self, group, x, y, max_velo, dx, dy, damage):
        super().__init__(group)
        self.add(missile_sprite)
        self.image = load_image("missile.png", -1)
        self.rect = self.image.get_rect()
        self.x, self.y = x, y
        self.max_velocity = max_velo
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.destruct = False
        self.image, self.rect = rot_center(self.image, self.rect, get_angle(self, (x + dx, y + dy)))
        gip = (dx ** 2 + dy ** 2) ** 0.5
        self.cos = dx / gip
        self.sin = dy / gip
        self.x += round((self.rect.w + current_game_mode.player.rect.w) * self.cos / 2)
        self.y += round((self.rect.h + current_game_mode.player.rect.h) * self.sin / 2)
        self.set_coords()

    def move(self):

        self.x += round(self.max_velocity / FPS * self.cos)
        self.y += round(self.max_velocity / FPS * self.sin)

        self.set_coords()

    def update(self, *args):

        self.move()

        target_dict = pygame.sprite.spritecollide(self, enemy_sprite, False, False)

        for target in target_dict:
            target.hp -= self.damage
            self.destruct = True

        target_player = pygame.sprite.spritecollideany(self, player_sprite)

        if target_player is not None:
            if self.rect.collidepoint((target_player.x, target_player.y)):
                target_player.hp -= self.damage
                self.destruct = True

        if abs(self.x - current_game_mode.player.x) > 1000:
            self.destruct = True

        if abs(self.y - current_game_mode.player.y) > 1000:
            self.destruct = True

        if self.destruct:
            self.kill()

    def set_coords(self):
        self.rect.x = self.x - (self.rect.w // 2)
        self.rect.y = self.y - (self.rect.h // 2)


def label_func(*args):
    return True


def start_screen(*args):

    pygame.mixer.music.stop()
    pygame.mixer.music.load("data\Music\menu_soundtrack.wav")
    pygame.mixer.music.play(-1, 0.0)

    loc_pressed = False

    global menu_background, screen

    menu_sprite = pygame.sprite.Group()
    menu_arrow_sprite = pygame.sprite.Group()

    arrow = Arrow(menu_arrow_sprite, "menu_arrow.png")
    button_new_game = Button(menu_sprite, "new_game.png",
                             screen.get_width() // 2,
                             round(screen.get_height() * 0.7),
                             setup_game_screen)
    button_options = Button(menu_sprite, "options.png",
                            screen.get_width() // 2,
                            round(screen.get_height() * 0.8), options_screen)
    button_quit = Button(menu_sprite, "quit.png",
                         screen.get_width() // 2,
                         round(screen.get_height() * 0.9),
                         ready_quit_screen)
    lbl_start = Button(menu_sprite, "start.png", 0, 0, label_func, True)
    lbl_start.rect.x = (screen.get_width() - 30) // 2
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
                arrow.rect.x = loc_event.pos[0]
                arrow.rect.y = loc_event.pos[1]
            if loc_event.type == pygame.KEYDOWN:
                if loc_event.key == pygame.K_ESCAPE:
                    ready_quit_screen()

        screen.blit(pygame.transform.scale(menu_background,
                                           (screen.get_width(),
                                            screen.get_height())), (0, 0))

        if button_new_game.to_return:
            reset_sprites(button_new_game,
                          button_options,
                          button_quit,
                          arrow,
                          lbl_start)
            pygame.mixer.music.stop()
            return

        menu_sprite.update(loc_pressed, arrow)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("data\Music\menu_soundtrack.wav")
            pygame.mixer.music.play(-1, 0.0)
        loc_pressed = False
        menu_sprite.draw(screen)

        menu_arrow_sprite.update()
        menu_arrow_sprite.draw(screen)

        pygame.display.flip()


def change_gm():
    pass


def change_df(btn):
    if current_game_mode.difficulty == 3:
        current_game_mode.difficulty = 0
    else:
        current_game_mode.difficulty += 1

    btn.image = load_image("difficulty_" + str(current_game_mode.difficulty) + ".png")


def setup_game_screen(*args):

    pygame.mixer.music.stop()
    pygame.mixer.music.load("data\Music\menu_soundtrack.wav")
    pygame.mixer.music.play(-1, 0.0)

    loc_pressed = False

    global menu_background, screen, current_game_mode, game_sprite

    game_sprite = pygame.sprite.Group()
    menu_sprite = pygame.sprite.Group()
    menu_arrow_sprite = pygame.sprite.Group()

    current_game_mode = GameModeArena(1)

    arrow = Arrow(menu_arrow_sprite, "menu_arrow.png")
    button_options = Button(menu_sprite, "options.png",
                            screen.get_width() // 2,
                            round(screen.get_height() * 0.8),
                            options_screen)
    button_back = Button(menu_sprite, "back.png",
                         round(screen.get_width() * 2 / 3),
                         round(screen.get_height() * 0.9),
                         label_func)

    button_game_mode = Button(menu_sprite, "press_to_select_gm.png",
                              screen.get_width() // 3,
                              round(screen.get_height() * 0.7),
                              change_gm, True)

    button_difficulty = Button(menu_sprite, "press_to_select_df.png",
                               round(screen.get_width() * 2 / 3),
                               round(screen.get_height() * 0.7),
                               change_df, True)

    button_quit = Button(menu_sprite, "quit.png",
                         screen.get_width() // 2,
                         round(screen.get_height() * 0.9),
                         ready_quit_screen)

    button_next = Button(menu_sprite, "next.png",
                         round(screen.get_width() * 2 / 3),
                         round(screen.get_height() * 0.8),
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
                arrow.rect.x = loc_event.pos[0]
                arrow.rect.y = loc_event.pos[1]
            if loc_event.type == pygame.KEYDOWN:
                if loc_event.key == pygame.K_ESCAPE:
                    ready_quit_screen()

        screen.blit(pygame.transform.scale(menu_background,
                                           (screen.get_width(),
                                            screen.get_height())), (0, 0))

        if button_back.to_return:
            reset_sprites(arrow,
                          button_back,
                          button_quit,
                          button_options,
                          button_difficulty,
                          button_game_mode)
            pygame.mixer.music.stop()
            return False
        if button_next.to_return:
            reset_sprites(arrow,
                          button_back,
                          button_quit,
                          button_options,
                          button_difficulty,
                          button_game_mode)
            pygame.mixer.music.stop()
            return True

        menu_sprite.update(loc_pressed, arrow)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("data\Music\menu_soundtrack.wav")
            pygame.mixer.music.play(-1, 0.0)
        loc_pressed = False
        menu_sprite.draw(screen)

        menu_arrow_sprite.update()
        menu_arrow_sprite.draw(screen)

        pygame.display.flip()


def ready_quit_screen(*args):

    pygame.mixer.music.stop()
    pygame.mixer.music.load("data\Music\menu_soundtrack.wav")
    pygame.mixer.music.play(-1, 0.0)

    loc_pressed = False

    global menu_background, screen

    menu_sprite = pygame.sprite.Group()
    menu_arrow_sprite = pygame.sprite.Group()

    arrow = Arrow(menu_arrow_sprite, "menu_arrow.png")

    lbl_ready = Button(menu_sprite, "ready_quit.png",
                       screen.get_width() // 2,
                       round(screen.get_height() * 0.3),
                       label_func, True)

    lbl_ready.rect.x -= lbl_ready.rect.w // 2 - 50

    button_yes = Button(menu_sprite, "yes.png",
                        round(screen.get_width() * 2 / 3),
                        round(screen.get_height() * 0.8),
                        terminate)

    button_no = Button(menu_sprite, "no.png",
                       round(screen.get_width() / 3),
                       round(screen.get_height() * 0.8),
                       label_func)

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
                                  lbl_ready,
                                  button_yes,
                                  button_no)
                    pygame.mixer.music.stop()
                    return

        screen.blit(pygame.transform.scale(menu_background,
                                           (screen.get_width(),
                                            screen.get_height())), (0, 0))

        if button_no.to_return:
            reset_sprites(arrow,
                          lbl_ready,
                          button_yes,
                          button_no)
            pygame.mixer.music.stop()
            return

        menu_sprite.update(loc_pressed, arrow)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("data\Music\menu_soundtrack.wav")
            pygame.mixer.music.play(-1, 0.0)
        menu_sprite.draw(screen)

        menu_arrow_sprite.update()
        menu_arrow_sprite.draw(screen)

        pygame.display.flip()


def menu_screen(*args):

    pygame.mixer.music.stop()
    pygame.mixer.music.load("data\Music\menu_soundtrack.wav")
    pygame.mixer.music.play(-1, 0.0)

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
                            round(screen.get_height() * 0.8),
                            options_screen)
    button_new_game = Button(menu_sprite, "new_game.png",
                             screen.get_width() // 2,
                             round(screen.get_height() * 0.7),
                             setup_game_screen)
    lbl_pause = Button(menu_sprite, "pause.png",
                       screen.get_width() // 2,
                       round(screen.get_height() * 0.3),
                       label_func, True)

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
                                  lbl_pause,
                                  button_quit,
                                  button_back,
                                  button_options,
                                  button_new_game)
                    return

        screen.blit(pygame.transform.scale(menu_background,
                                           (screen.get_width(),
                                            screen.get_height())), (0, 0))

        if button_back.to_return:
            reset_sprites(arrow,
                          lbl_pause,
                          button_quit,
                          button_back,
                          button_options,
                          button_new_game)
            pygame.mixer.music.stop()
            return

        if button_new_game.to_return:
            reset_sprites(arrow,
                          lbl_pause,
                          button_quit,
                          button_back,
                          button_options,
                          button_new_game)
            pygame.mixer.music.stop()
            return

        menu_sprite.update(loc_pressed, arrow)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("data\Music\menu_soundtrack.wav")
            pygame.mixer.music.play(-1, 0.0)
        loc_pressed = False
        menu_sprite.draw(screen)

        menu_arrow_sprite.update()
        menu_arrow_sprite.draw(screen)

        pygame.display.flip()


def game_over_screen(*args):

    pygame.mixer.music.stop()
    pygame.mixer.music.load("data\Music\menu_soundtrack.wav")
    pygame.mixer.music.play(-1, 0.0)
    loc_pressed = True

    global screen, menu_background

    menu_sprite = pygame.sprite.Group()
    menu_arrow_sprite = pygame.sprite.Group()

    arrow = Arrow(menu_arrow_sprite, "menu_arrow.png")
    lbl_game_over = Button(menu_sprite, "game_over.png",
                           screen.get_width() // 2,
                           round(screen.get_height() * 0.3),
                           label_func, True)
    # lbl_game_over.rect.x -= lbl_game_over.rect.w // 2
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

        if button_new_game.to_return:  # next
            reset_sprites(button_new_game,
                          button_quit,
                          arrow,
                          lbl_game_over)
            pygame.mixer.music.stop()
            return

        menu_sprite.update(loc_pressed, arrow)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("data\Music\menu_soundtrack.wav")
            pygame.mixer.music.play(-1, 0.0)
        loc_pressed = False
        menu_sprite.draw(screen)

        menu_arrow_sprite.update()
        menu_arrow_sprite.draw(screen)

        pygame.display.flip()


def options_screen(*args):
    pass


def reset_sprites(*args):
    for el in args:
        el.kill()


def terminate(*args):
    pygame.mixer.quit()
    pygame.quit()
    sys.exit()


pygame.init()
running = True
lock_fps = True


pygame.mixer.init()
pygame.mixer.music.load("data\Music\soundtrack_3.wav")
pygame.mixer.music.play(-1, 0.0)

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
menu_background = load_image("menu_background.png")

current_game_mode = None

start_screen()
background = load_image("background_game.png")

dirs = ['', '', '', '']

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ready_quit_screen()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu_screen()  # open menu
            if event.key == pygame.K_a:
                dirs[0] = 'W'
            if event.key == pygame.K_d:
                dirs[1] = 'E'
            if event.key == pygame.K_w:
                dirs[2] = 'N'
            if event.key == pygame.K_s:
                dirs[3] = 'S'
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                menu_screen()  # open menu
            if event.key == pygame.K_a:
                dirs[0] = ''
            if event.key == pygame.K_d:
                dirs[1] = ''
            if event.key == pygame.K_w:
                dirs[2] = ''
            if event.key == pygame.K_s:
                dirs[3] = ''
        if event.type == pygame.MOUSEBUTTONDOWN:
            current_game_mode.is_pushed(event.pos)
        if event.type == pygame.MOUSEMOTION:
            game_arrow.rect.x = event.pos[0]
            game_arrow.rect.y = event.pos[1]

    screen.blit(pygame.transform.scale(background,
                                       (screen.get_width(),
                                        screen.get_height())), (0, 0))

    # print(pygame.mixer.music.get_busy())

    current_game_mode.move(dirs)
    current_game_mode.next()

    if current_game_mode.is_end():
        game_over_screen()

    game_sprite.update()
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("data\Music\soundtrack_3.wav")
        pygame.mixer.music.play(-1, 0.0)
    game_sprite.draw(screen)

    game_arrow_sprite.update()
    game_arrow_sprite.draw(screen)

    pygame.display.flip()

    if lock_fps:
        clock.tick(FPS)

terminate()
