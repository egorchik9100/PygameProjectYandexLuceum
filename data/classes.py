import math
import random

import pygame

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
width, height = 800, 600


class MainScene:
    def __init__(self, screen):
        self.asteroids = []
        self.turret = Turret(screen)
        self.bullets = []
        self.can_shoot = True
        self.shoot_delay = 400
        self.last_shot_time = 0
        self.screen = screen

    def run_game(self):

        # Создание астероидов, турели, списка пуль
        for i in range(5):
            self.asteroids.append(Asteroid(self.screen))

        # Главный цикл игры
        running = True
        clock = pygame.time.Clock()
        while running:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return running

            # Управление турелью
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.turret.update(-1)
            if keys[pygame.K_RIGHT]:
                self.turret.update(1)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and self.can_shoot and current_time - self.last_shot_time > self.shoot_delay:
                self.bullets.append(Bullet(self.turret.x + 50 * math.cos(math.radians(self.turret.angle)),
                                           self.turret.y - 50 * math.sin(math.radians(self.turret.angle)),
                                           self.turret.angle, self.screen, 1))
                self.can_shoot = False  # Запрещаем стрельбу
                self.last_shot_time = current_time  # Обновляем время последнего выстрела
            # Разрешаем стрельбу
            if not self.can_shoot and current_time - self.last_shot_time > self.shoot_delay:
                self.can_shoot = True

            # Обновление астероидов и удаление тех, которые вышли за экран
            for asteroid in self.asteroids[:]:
                if asteroid.update():
                    self.asteroids.remove(asteroid)
            # Добавляем новые астероиды (для постоянной игры)
            if random.random() < 0.05:
                self.asteroids.append(Asteroid(self.screen))

            # Обновление и отрисовка пуль
            for bullet in self.bullets[:]:
                bullet.update()
                if bullet.is_off_screen():
                    self.bullets.remove(bullet)

            # Проверка столкновений (простая проверка)
            for bullet in self.bullets[:]:
                for asteroid in self.asteroids[:]:
                    distance = math.dist((bullet.x, bullet.y), (asteroid.x, asteroid.y))
                    if distance < asteroid.size:
                        self.asteroids.remove(asteroid)
                        self.bullets.remove(bullet)
                        break

            # Отрисовка
            self.screen.fill(black)
            for asteroid in self.asteroids:
                asteroid.draw()
            self.turret.draw()
            for bullet in self.bullets:
                bullet.draw()
            pygame.display.flip()
            clock.tick(60)


class Asteroid:
    def __init__(self, screen):
        self.screen = screen
        self.size = random.randint(20, 50)
        self.x = random.randint(0, width - self.size)
        self.y = -self.size
        self.speed = random.randint(2, 5)
        self.health = random.randint(20, 50)

    def update(self):
        self.y += self.speed
        if self.y > height:
            return True  # Удаляем астероид, если он вышел за экран
        return False

    def draw(self):
        pygame.draw.circle(self.screen, red, (self.x, self.y), self.size)


class Turret:
    def __init__(self, screen):
        self.screen = screen
        self.x = width // 2
        self.y = height - 50
        self.angle = 90  # Начальный угол
        self.speed = 5 # Скорость перемещения турели

    def update(self, dx):
        self.x += dx * self.speed # Изменение координаты x
        self.x = max(0, min(self.x, width)) # Ограничение движения по ширине экрана

    def draw(self):
        # Рисуем турель (простая линия)
        pygame.draw.line(self.screen, white, (self.x, self.y),
                         (self.x + 50 * math.cos(math.radians(self.angle)),
                          self.y - 50 * math.sin(math.radians(self.angle))), 5)
        pygame.draw.circle(self.screen, white, (self.x, self.y), 10)  # Основа турели


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, screen, force):
        super().__init__()
        self.force = force
        self.screen = screen
        self.x = x
        self.y = y
        self.angle = math.radians(angle)  # Преобразование угла в радианы
        self.speed = 10

    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y -= self.speed * math.sin(self.angle)  # Y убывает вверх

    def draw(self):
        pygame.draw.circle(self.screen, white, (int(self.x), int(self.y)), 2)

    def is_off_screen(self):
        return self.x < 0 or self.x > width or self.y < 0 or self.y > height

