import pygame
from data.classes import MainScene, StartWindow


def main():
    # Инициализация Pygame
    pygame.init()

    # Размеры окна
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Турель против астероидов")
    start_window = StartWindow(screen)
    main_scene = MainScene(screen)
    current_scene = "menu"
    running = True
    while running:
        if current_scene == "menu":
            running = start_window.main_menu()
            if running == "game":
                current_scene = "game"
        elif current_scene == "game":
            running = main_scene.run_game()
    pygame.quit()


if __name__ == '__main__':
    main()

