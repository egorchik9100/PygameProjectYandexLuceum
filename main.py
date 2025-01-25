import pygame
from data.classes import MainScene, StartWindow


def main():
    pygame.init()

    # Размеры окна
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Турель против астероидов")
    current_scene = "menu"
    running = True
    while running:
        if current_scene == "menu":
            start_window = StartWindow(screen)
            running = start_window.main_menu()
            if running == "game":
                current_scene = "game"
        elif current_scene == "game":
            main_scene = MainScene(screen)
            running = main_scene.run_game()
            if running == "menu":
                current_scene = "menu"
    pygame.quit()


if __name__ == '__main__':
    main()

