if __name__ == '__main__':
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
    # game_arrow_sprite = pygame.sprite.Group()


    # game_arrow = Arrow(game_arrow_sprite, "game_arrow.png")
    menu_background = load_image("menu_background.png")

    current_game_mode = None

    start_screen()
    background = load_image("background_game.png")

    dirs = [-1, -1, -1, -1]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ready_quit_screen()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_screen()  # open menu
                if event.key == pygame.K_a:
                    dirs[0] = 2
                if event.key == pygame.K_d:
                    dirs[1] = 3
                if event.key == pygame.K_w:
                    dirs[2] = 0
                if event.key == pygame.K_s:
                    dirs[3] = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    menu_screen()  # open menu
                if event.key == pygame.K_a:
                    dirs[0] = -1
                if event.key == pygame.K_d:
                    dirs[1] = -1
                if event.key == pygame.K_w:
                    dirs[2] = -1
                if event.key == pygame.K_s:
                    dirs[3] = -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_game_mode.is_pushed(event.pos)
            if event.type == pygame.MOUSEMOTION:
                current_game_mode.update_arrow(event.pos)

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

        # game_arrow_sprite.update()
        # game_arrow_sprite.draw(screen)

        pygame.display.flip()

        if lock_fps:
            clock.tick(FPS)
