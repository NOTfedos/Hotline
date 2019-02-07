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


class Button(pygame.sprite.Sprite):
    def __init__(self, group, image_name, x, y, func):
        super().__init__(group)
        self.add(button_sprite)
        self.image = load_image(image_name)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.func = func

    def update(self):
        if pygame.sprite.spritecollideany(self, arrow_sprite):
            self.image = load_image(image_name + "_focused")


class Arrow(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.add(arrow_sprite)
        self.image = load_image("arrow.png")
        self.rect = self.image.get_rect()

    def update(self):
        btn = pygame.sprite.spritecollideany(self, button_sprite)
        btn.func()


class Player(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.add(player_sprite)
        self.image = load_image("player.png")
        self.rect = self.image.get_rect()
        self.hp = 100
        self.damage = 50

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


class Enemy(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.add(enemy_sprite)
        self.image = load_image("enemy.png")
        self.rect = self.image.get_rect()
        self.hp = 100
        self.damage = 10

    def update(self):
        if self.hp <= 0:
            if self.get_animation():
                self.kill()

        action(self, player)


def terminate():
    pygame.quit()
    sys.exit()


running = True
game_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

FPS = 60

GAME_MODES = {'ARENA': arena_action, 'LEVEL': level_action}

start_screen()

game_sprite = pygame.sprite.Group()
enemy_sprite = pygame.sprite.Group()
player_sprite = pygame.sprite.Group()
button_sprite = pygame.sprite.Group()
arrow_sprite = pygame.sprite.Group()

background = load_image("background_game.png")

restart_game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu_screen()
    game_screen.blit(pygame.transform.scale(background,
                                            (game_screen.get_width(),
                                             game_screen.get_height())), 0, 0)

    game_sprite.draw(game_screen)
    GAME_MODES[CURRENT_GAME_MODE]()
    game_sprite.update()
    pygame.display.flip()
    if lock_fps:
        clock.tick(fps)

terminate()
