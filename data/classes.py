import math
import random
from data.functions import load_image
import pygame
from random import choice
import pygame_menu

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
        self.paused = False
        self.score = 0
        self.in_game = True

    def run_game(self):

        # Создание астероидов, турели, списка пуль
        for i in range(5):
            self.asteroids.append(Asteroid(self.screen))

        font = pygame.font.Font(None, 36)

        # Кнопка паузы
        pause_button_text = font.render("||", True, white)
        pause_button_rect = pause_button_text.get_rect(topright=(width - 10, 20))

        # Создание меню паузы
        self.menu = pygame_menu.Menu("Пауза", 200, 200, theme=pygame_menu.themes.THEME_BLUE)
        self.menu.add.button("Продолжить", self.resume_game)
        self.menu.add.button("Выйти", self.exit_game)
        self.menu.disable()  # Изначально меню паузы скрыто


        # Главный цикл игры
        running = True
        clock = pygame.time.Clock()
        while running:
            if self.in_game is False:
                return 'menu'
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return running
                if not self.paused:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if pause_button_rect.collidepoint(event.pos):
                            self.paused = True
                            self.menu.enable()
                            self.menu.mainloop(self.screen)

            if not self.paused:
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

                # Проверка столкновений
                for bullet in self.bullets[:]:
                    for asteroid in self.asteroids[:]:
                        distance = math.dist((bullet.x, bullet.y), (asteroid.x, asteroid.y))
                        if distance < asteroid.size:
                            self.asteroids.remove(asteroid)
                            self.bullets.remove(bullet)
                            self.score += 1
                            break

                # Отрисовка
                # Прямоугольник для счета
                font_score = pygame.font.Font(None, 74)
                text_score = font.render(f"Счёт: {self.score}", True, (100, 100, 100))
                rect_score = text_score.get_rect(topright=(width - 50, 20))

                self.screen.fill(black)
                for asteroid in self.asteroids:
                    asteroid.draw()
                self.turret.draw()
                for bullet in self.bullets:
                    bullet.draw()
                self.screen.blit(text_score, rect_score)  # Вывод количества очков
                self.screen.blit(pause_button_text, pause_button_rect)  # Вывод кнопки паузы
                pygame.display.flip()  # Обновление экрана
                clock.tick(60)
            else:
                if not self.menu.is_enabled():
                    self.screen.blit(pause_button_text, pause_button_rect)  # Вывод кнопки паузы
                    pygame.display.flip()

                # Задержка для контроля FPS
            pygame.time.Clock().tick(60)

    def resume_game(self):
        self.paused = False
        self.menu.disable()

    def exit_game(self):
        self.in_game = False
        self.menu.disable()


class StartWindow:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 36)

    def draw_button(self, text, x, y, width, height):
        pygame.draw.rect(self.screen, 'gray', (x, y, width, height))
        pygame.draw.rect(self.screen, 'black', (x, y, width, height), 3)

        label = self.font.render(text, True, 'black')
        text_rect = label.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(label, text_rect)

    def main_menu(self):
        running = True
        while True:
            self.screen.fill('white')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return running
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_pos = pygame.mouse.get_pos()
                    if play_button.collidepoint(mouse_pos):
                        return "game"

            play_button = pygame.Rect(width // 2 - 150, height // 2 - 50, 300, 50)
            records_button = pygame.Rect(width // 2 - 150, height // 2 + 20, 300, 50)
            self.draw_button("Играть", play_button.x, play_button.y, play_button.width, play_button.height)
            self.draw_button("Рекорды", records_button.x, records_button.y, records_button.width, records_button.height)

            pygame.display.update()


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
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
        if 20 <= self.size < 30:
            self.screen.blit(load_image("asteroids/size_25/Круглый астреоид на белом фоне_25.png", colorkey=-1), (self.x, self.y))
        if 30 <= self.size < 40:
            self.screen.blit(load_image("asteroids/size_35/Астероид в космосе_35.jpg", colorkey=-1), (self.x, self.y))
        if 40 <= self.size <= 50:
            self.screen.blit(load_image("asteroids/size_45/Астероид из блэндера_45.jpg", colorkey=-1), (self.x, self.y))

    def damage(self, dam):
        self.health = self.health - dam


class Turret:
    def __init__(self, screen):
        self.screen = screen
        self.x = width // 2
        self.y = height - 50
        self.angle = 90  # Начальный угол
        self.speed = 5  # Скорость перемещения турели
        self.keys = keys = pygame.key.get_pressed()
        self.flag_turret = 1
        self.img_turret = "starships/size_45/white_level1 100x57-no-bg-preview (carve.photos).png"

    def update(self, dx):
        self.x += dx * self.speed  # Изменение координаты x
        self.x = max(0, min(self.x, width))  # Ограничение движения по ширине экрана

    def draw(self):
        if self.flag_turret == 0:
            # Рисуем турель (простая линия)
            pygame.draw.line(self.screen, white, (self.x, self.y),
                             (self.x + 50 * math.cos(math.radians(self.angle)),
                              self.y - 50 * math.sin(math.radians(self.angle))), 5)
            pygame.draw.circle(self.screen, white, (self.x, self.y), 10)  # Основа турели
        elif self.flag_turret == 1:
            self.screen.blit(load_image(self.img_turret), (self.x, self.y))
        # Управление турелью
        if self.keys[pygame.K_9]:
            print("change startship - okey)")
            self.img_turret = "starships/size_150/white_level1 100x57-no-bg-preview (carve.photos).png"


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, screen, force):
        super().__init__()
        self.force = force
        self.screen = screen
        self.x = x + 50
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
