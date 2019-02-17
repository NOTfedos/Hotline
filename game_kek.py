import pygame
import game_screens

if __name__ == '__main__':

    pygame.init()
    running = True

    screen = pygame.display.set_mode((1280, 720))
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    current_game_mode = None

    game_screens.start_screen(current_game_mode, screen)

    while running:
        current_game_mode.parse_events(pygame.event.get())
        current_game_mode.update()
        if current_game_mode.is_end():
            game_screens.game_over_screen(current_game_mode, screen)
        current_game_mode.draw()
        pygame.display.flip()

    game_screens.terminate()
