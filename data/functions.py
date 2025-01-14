import os
import sys
import pygame


def load_image(name, size, colorkey=None):
    if size == 25:
        fullname = os.path.join('images/asteroids/size_25', name)
    if size == 35:
        fullname = os.path.join('images/asteroids/size_35', name)
    if size == 45:
        fullname = os.path.join('images/asteroids/size_45', name)
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


