import os
import sys
import pygame


def load_image(name, colorkey=None):
    fullname = 'images/' + name
    if not os.path.isfile(fullname):
        print(f'Файл с изображением "{fullname}" не найден')
        sys.exit()

    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()  # оптимизирует формат изображения и ускоряет отрисовку
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()  # используется для добавления прозрачности к изображению
    return image


def music_crash_asteroid(flag=None, thing=None):
    if thing == "Asteroid":
        if flag == 1:
            pygame.mixer.Sound("sounds/Crash_ston.mp3").play()
        if flag == 0:
            pygame.mixer.Sound("sounds/hit_asteroid.mp3").play()
    if thing == "buff":
        pygame.mixer.Sound("sounds/buff_blue.mp3").play()
    if thing == "level_up":
        pygame.mixer.Sound("sounds/level_up.mp3").play()
