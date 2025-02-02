import pygame
from data.classes import MainScene, StartWindow, RecordsWindow


def main():
    pygame.init()

    # Размеры окна
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Galla")
    current_scene = "menu"
    running = True
    while running:
        if current_scene == "menu":
            start_window = StartWindow(screen)
            running = start_window.main_menu()
            if running == "game":
                current_scene = "game"
            elif running == "records":
                current_scene = "records"
        elif current_scene == "game":
            main_scene = MainScene(screen)
            running = main_scene.run_game()
            if running == "menu":
                current_scene = "menu"
            elif running == "records":
                current_scene = "records"
        elif current_scene == "records":
            records_scene = RecordsWindow(screen)
            running = records_scene.display_highscores()
            if running == "game":
                current_scene = "game"
            elif running == "menu":
                current_scene = "menu"
    pygame.quit()
    '''except Exception as er:
        print(f"In main.py -> {er}")'''


if __name__ == '__main__':
    main()

