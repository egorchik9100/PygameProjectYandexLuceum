import pygame
from data.classes import Asteroid, Turret, Bullet
import math
import random


white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)


def run_game():
    # Инициализация Pygame
    pygame.init()

    # Размеры окна
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Турель против астероидов")

    # Создание астероидов, турели, списка пуль
    asteroids = []
    for i in range(5):
        asteroids.append(Asteroid())
    turret = Turret()
    bullets = []

    # Главный цикл игры
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Управление турелью
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            turret.update(-1)
        if keys[pygame.K_RIGHT]:
            turret.update(1)

        # Стрельба
        if keys[pygame.K_SPACE]:
            bullets.append(Bullet(turret.x + 50 * math.cos(math.radians(turret.angle)),
                                  turret.y - 50 * math.sin(math.radians(turret.angle)),
                                  turret.angle))

        # Обновление астероидов и удаление тех, которые вышли за экран
        for asteroid in asteroids[:]:
            if asteroid.update():
                asteroids.remove(asteroid)
        # Добавляем новые астероиды (для постоянной игры)
        if random.random() < 0.02:
            asteroids.append(Asteroid())

        # Обновление и отрисовка пуль
        for bullet in bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                bullets.remove(bullet)

        # Проверка столкновений (простая проверка)
        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                distance = math.dist((bullet.x, bullet.y), (asteroid.x, asteroid.y))
                if distance < asteroid.size:
                    asteroids.remove(asteroid)
                    bullets.remove(bullet)
                    break

        # Отрисовка
        screen.fill(black)
        for asteroid in asteroids:
            asteroid.draw(screen)
        turret.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    run_game()

