import pygame
from data.classes import MainScene, StartWindow


def main():
    # Инициализация Pygame
    pygame.init()

    # Размеры окна
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Турель против астероидов")
    game_scene = StartWindow(screen)
    run = True
    while run:
        run = game_scene.main_menu()
    pygame.quit()


if __name__ == '__main__':
    main()

