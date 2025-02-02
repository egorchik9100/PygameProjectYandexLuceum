
import math
import random
import sqlite3
import time

import pygame
from random import choice
import pygame_menu

from data.functions import load_image, music_crash_asteroid, parse_json, load_db, get_res

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
width, height = 800, 600
num_of_ship = 0


class MainScene:
    def __init__(self, screen):
        self.asteroids = []
        self.color = "green"
        self.turret = Turret(screen)
        self.bullets = []
        self.buffs_white = []  # список зелий, которые уничтожают астероиды на экране;
        self.buffs_blue = []  # список зелий, которые пополняют опыт;
        self.buffs_red = []  # список зелий, которые восстанавливают здоровье;
        self.can_shoot = True
        self.shoot_delay = 400
        self.last_shot_time = 0
        self.screen = screen
        self.paused = False
        self.score_music_level = 0  # Флаг для проигрывания музыки при повышении уровня;
        self.score = 0
        self.buff_flag = 0
        self.score_flag = True  # для переключения на 9 корабль, при достижении 112 очков;
        self.in_game = True
        self.level = 0  # текущий левел;
        self.life = 100
        self.asteroid_chance = 0.05
        self.time = 0
        self.game_over = False  # Флаг для отслеживания окончания игры

    def run_game(self):
        self.time = time.time()  # время запуска раунда;
        # Создание астероидов, турели, списка пуль
        for i in range(5):
            self.asteroids.append(Asteroid(self.screen, self.level))

        font = pygame.font.Font(None, 36)

        # Кнопка паузы
        pause_button_text = font.render("||", True, white)
        pause_button_rect = pause_button_text.get_rect(topright=(width - 10, 20))

        # Создание меню паузы
        self.menu = pygame_menu.Menu("Пауза", 200, 200, theme=pygame_menu.themes.THEME_BLUE)
        self.menu.add.button("Продолжить", self.resume_game)
        self.menu.add.button("Выйти", self.exit_game)
        self.menu.disable()  # Изначально меню паузы скрыто

        self.finish_menu = pygame_menu.Menu("Вы врезались в астероид", 500, 500, theme=pygame_menu.themes.THEME_BLUE)
        scores = self.finish_menu.add.label(f'Очки: {self.score}')
        times = self.finish_menu.add.label(f'ВРЕМЯ - {self.time}')
        place = self.finish_menu.add.label(f'ВРЕМЯ - {self.time}')
        place1 = self.finish_menu.add.label(f'ВРЕМЯ - {self.time}')
        one_more = self.finish_menu.add.button("Сыграть еще раз", self.play_one_more)
        exits = self.finish_menu.add.button("Выйти", self.exit_game)

        self.finish_menu.disable()

        # Главный цикл игры
        pygame.mixer.music.load("sounds/For_game.mp3")
        pygame.mixer.music.play(-1)
        running = True
        clock = pygame.time.Clock()
        while running:
            if self.in_game is False:
                pygame.mixer.music.stop()
                return 'menu'
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return running
                if not self.paused and not self.game_over:  # Если игра не на паузе и не окончена
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if pause_button_rect.collidepoint(event.pos):
                            self.paused = True
                            self.menu.enable()
                            self.menu.mainloop(self.screen)

            if not self.paused and not self.game_over:  # если игра не на паузе и не окончена
                global num_of_ship
                # Управление турелью
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.turret.update(-1)
                if keys[pygame.K_RIGHT]:
                    self.turret.update(1)

                # Чит-коды
                if keys[pygame.K_9]:  # при нажимании кнопки 9, текущий корабль сменяется на 9;
                    num_of_ship = 9
                if keys[pygame.K_1]:  # при нажимании кнопки 9, текущий корабль сменяется на 1(начальный);
                    num_of_ship = 1
                if keys[pygame.K_8]:  # при нажимании кнопки 9, текущий корабль сменяется на 8;
                    num_of_ship = 8
                if self.score >= 112 and self.score_flag:  # когда игрок достигает 112 очков и больше, его корабль сменяется на 9;
                    num_of_ship = 9
                    self.score_flag = False

                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE] and self.can_shoot and current_time - self.last_shot_time > self.shoot_delay:  # обработка стрельбы;
                    self.bullets.append(Bullet(self.turret.x,
                                               self.turret.y,
                                               self.turret.angle, self.screen, 1, self.level))
                    self.can_shoot = False  # Запрещаем стрельбу;
                    self.last_shot_time = current_time  # Обновляем время последнего выстрела;

                # Проигрываем музыку при повышении уровня;
                if 1 <= self.level <= 20 and self.level > self.score_music_level:
                    self.score_music_level = self.level  # алгоритм позволяющий проигрывать музыку 1 раз;
                    music_crash_asteroid(thing="level_up")

                # Разрешаем стрельбу;
                if not self.can_shoot and current_time - self.last_shot_time > self.shoot_delay:
                    self.can_shoot = True

                # Обновление астероидов и удаление тех, которые вышли за экран;
                for asteroid in self.asteroids[:]:
                    if asteroid.update():
                        self.asteroids.remove(asteroid)

                # Обновление зелий и удаление тех, которые вышли за экран;
                for buff_b in self.buffs_blue[:]:
                    if buff_b.update():
                        self.buffs_blue.remove(buff_b)
                for buff_w in self.buffs_white[:]:
                    if buff_w.update():
                        self.buffs_white.remove(buff_w)
                for buff_r in self.buffs_red[:]:
                    if buff_r.update():
                        self.buffs_red.remove(buff_r)

                # Добавляем новые астероиды и зелья (для постоянной игры);
                if random.random() < self.asteroid_chance:
                    self.asteroids.append(Asteroid(self.screen, self.level))
                if self.score > 10 and self.buff_flag <= 0:
                    if random.random() < 0.0002:
                        self.buff_flag = 5
                        self.buffs_white.append(BuffWhite(self.screen))
                    if random.random() < 0.0002:
                        self.buff_flag = 5
                        self.buffs_red.append(BuffRed(self.screen))
                    if random.random() < 0.0002:
                        self.buff_flag = 5
                        self.buffs_blue.append(BuffBlue(self.screen))
                if self.buff_flag > 0 and random.random() < 0.008:
                    self.buff_flag -= 1

                # Новый уровень
                if self.score // 50 > self.level:
                    self.level += 1
                    self.asteroid_chance += parse_json('asteroid', 'chance')


                # Обновление и отрисовка пуль
                for bullet in self.bullets[:]:
                    bullet.update()
                    if bullet.is_off_screen():
                        self.bullets.remove(bullet)

                # проверка столкновений турели с астероидом
                for asteroid in self.asteroids[:]:
                    if pygame.sprite.collide_rect(self.turret, asteroid) and not self.game_over and self.life <= 0:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load('sounds/Crash.mp3')
                        pygame.mixer.music.play(-1)
                        for num in range(4):
                            self.turret.crash(num + 1)
                            pygame.display.flip()
                            time.sleep(0.5)
                        pygame.mixer.music.stop()
                        self.finish_menu.remove_widget(scores)
                        self.finish_menu.remove_widget(one_more)
                        self.finish_menu.remove_widget(exits)
                        self.finish_menu.remove_widget(times)
                        self.finish_menu.remove_widget(place)
                        self.finish_menu.remove_widget(place1)
                        self.time = time.time() - self.time
                        scores = self.finish_menu.add.label(f'СЧЕТ - {self.score}')
                        text = str(self.time).split('.')[0]
                        load_db(self.score, int(text), self.level)
                        times = self.finish_menu.add.label(f'ВРЕМЯ - {text} сек')
                        place = self.finish_menu.add.label('ВАШЕ МЕСТО В ТАБЛИЦЕ:')
                        a = str(get_res(self.score, text))
                        print(a, self.score, text)
                        place1 = self.finish_menu.add.label(a)
                        one_more = self.finish_menu.add.button("Сыграть еще раз", self.play_one_more)
                        exits = self.finish_menu.add.button("Выйти", self.exit_game)
                        self.game_over = True
                        self.paused = True
                        self.finish_menu.enable()
                        self.finish_menu.mainloop(self.screen)  # Отображаем меню finish'''
                        self.time = time.time()
                    if pygame.sprite.collide_rect(self.turret, asteroid) and not self.game_over and self.life > 0:
                        self.life -= 1

                # Проверка столкновений;
                for bullet in self.bullets[:]:
                    for asteroid in self.asteroids[:]:
                        distance = math.dist((bullet.x, bullet.y), (asteroid.x, asteroid.y))
                        if distance < asteroid.size:
                            asteroid_hp = asteroid.health
                            self.score += 0.5
                            if asteroid_hp - bullet.damage <= 0:
                                music_crash_asteroid(flag=1, thing="Asteroid")
                                self.asteroids.remove(asteroid)
                                self.score += 2
                            else:
                                music_crash_asteroid(flag=0, thing="Asteroid")
                                asteroid.health -= bullet.damage
                            self.bullets.remove(bullet)
                            break

                    for buff_w in self.buffs_white[:]:
                        distance = math.dist((bullet.x, bullet.y), (buff_w.x, buff_w.y))
                        if distance < buff_w.size:
                            try:
                                music_crash_asteroid(thing="buff")
                                self.score += len(self.asteroids) * 4  # добавление к счету количества очков за все астероиды;
                                self.asteroids.clear()  # удаление всех астероидов при попадании в белое зелье;
                                self.buff_flag = False
                                self.buffs_white.remove(buff_w)
                                self.bullets.remove(bullet)
                            except Exception as er:
                                print(er)
                            break

                    for buff_r in self.buffs_red[:]:
                        distance = math.dist((bullet.x, bullet.y), (buff_r.x, buff_r.y))
                        if distance < buff_r.size:
                            if self.life + 200 <= 512:
                                self.life += 200  # начисление 200 процентов к кораблю;
                            elif self.life <= 512:
                                self.life += 512 - self.life
                            try:
                                music_crash_asteroid(thing="buff")
                                self.buff_flag = False
                                self.buffs_red.remove(buff_r)
                                self.bullets.remove(bullet)
                            except Exception as er:
                                print(er)
                            break

                    for buff_b in self.buffs_blue[:]:
                        distance = math.dist((bullet.x, bullet.y), (buff_b.x, buff_b.y))
                        if distance < buff_b.size:
                            self.score += 100
                            try:
                                music_crash_asteroid(thing="buff")
                                self.buff_flag = False
                                self.buffs_blue.remove(buff_b)
                                self.bullets.remove(bullet)
                            except Exception as er:
                                print(er)
                            break

                # Отрисовка;
                # Прямоугольник для счета;
                text_score = font.render(f"Счёт: {int(self.score)}", True, (100, 100, 100))
                rect_score = text_score.get_rect(topright=(width - 50, 20))

                # Проверка уровня жизни;
                if 80 < self.life <= 512:
                    self.color = "green"
                if 50 < self.life <= 80:
                    self.color = "yellow"
                if 20 < self.life <= 50:
                    self.color = "orange"
                if 0 <= self.life <= 20:
                    self.color = "red"
                # Прямоугольник для жизни;
                text_life = font.render(f"HP Starship: {int(self.life)}%", True, self.color)
                rect_life = text_life.get_rect(topright=(width - 200, 20))

                # Прямоугольник для уровня;
                text_level = font.render(f"Уровень: {int(self.level)}", True, (100, 100, 100))
                rect_level = text_score.get_rect(topright=(110, 20))

                self.screen.fill(black)
                self.screen.blit(load_image('Без имени-1.jpg'), (0, 0))
                for asteroid in self.asteroids:
                    asteroid.draw()
                self.turret.draw()
                for buff_w in self.buffs_white:
                    buff_w.draw()
                for buff_r in self.buffs_red:
                    buff_r.draw()
                for buff_b in self.buffs_blue:
                    buff_b.draw()
                for bullet in self.bullets:
                    bullet.draw()
                self.screen.blit(text_life, rect_life)  # Вывод количества здоровья;
                self.screen.blit(text_score, rect_score)  # Вывод количества очков;
                self.screen.blit(text_level, rect_level)  # Вывод текущего уровня;
                self.screen.blit(pause_button_text, pause_button_rect)  # Вывод кнопки паузы;
                pygame.display.flip()  # Обновление экрана;
                clock.tick(60)
            else:
                if not self.menu.is_enabled() and not self.finish_menu.is_enabled():
                    self.screen.blit(pause_button_text, pause_button_rect)  # Вывод кнопки паузы;
                    pygame.display.flip()

                # Задержка для контроля FPS;
            pygame.time.Clock().tick(60)

    def resume_game(self):
        self.paused = False
        self.menu.disable()

    def exit_game(self):
        self.in_game = False
        self.menu.disable()
        self.finish_menu.disable()

    def play_one_more(self):
        self.game_over = False
        self.paused = False
        self.score = 0
        self.life = 101
        self.score_flag = True
        self.level = 0
        self.asteroids.clear()
        for i in range(5):
            self.asteroids.append(Asteroid(self.screen, self.level))
        self.finish_menu.disable()
        pygame.mixer.music.load("sounds/For_game.mp3")
        pygame.mixer.music.play(-1)


class StartWindow:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 36)

    def draw_button(self, text, x, y, width, height):
        pygame.draw.rect(self.screen, 'blue', (x, y, width, height))
        pygame.draw.rect(self.screen, 'black', (x, y, width, height), 3)

        label = self.font.render(text, True, 'white')
        text_rect = label.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(label, text_rect)

    def main_menu(self):
        running = True
        self.menu = pygame_menu.Menu("Справка об игре", 600, 600, theme=pygame_menu.themes.THEME_DARK)
        self.menu.add.label('Управление:', 'green')
        self.menu.add.label("'<' : '>' - управление турелью")
        self.menu.add.label("'space' - стрельба")
        self.menu.add.label('АВТОРЫ:')
        self.menu.add.label('Советов Е, Челноков Е, Беляков А')
        self.menu.add.label('Проект на GitHub:')
        self.menu.add.label('https://clck.ru/3G62aD')
        self.menu.add.button("OK", self.skip_menu)
        self.menu.disable()  # Изначально меню паузы скрыто
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
                    if spravka_button.collidepoint(mouse_pos):
                        self.menu.enable()
                        self.menu.mainloop(self.screen)
                    if records_button.collidepoint(mouse_pos):
                        return "records"

            self.screen.blit(load_image('space.jpg'), (0, 0))
            font = pygame.font.Font(None, 36)
            main_text = font.render("Добро пожаловать в GALLA SPACE!", True, white)
            main_rect = main_text.get_rect(topright=(625, 100))
            self.screen.blit(main_text, main_rect)
            play_button = pygame.Rect(width // 2 - 150, height // 2 - 50, 300, 50)
            records_button = pygame.Rect(width // 2 - 150, height // 2 + 20, 300, 50)
            spravka_button = pygame.Rect(width // 2 - 150, height // 2 + 90, 300, 50)
            self.draw_button("Играть", play_button.x, play_button.y, play_button.width, play_button.height)
            self.draw_button("Рекорды", records_button.x, records_button.y, records_button.width, records_button.height)
            self.draw_button("Об игре", spravka_button.x, spravka_button.y, spravka_button.width, spravka_button.height)

            pygame.display.update()

    def skip_menu(self):
        self.menu.disable()


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, screen, level):
        super().__init__()
        self.screen = screen
        self.size = random.randint(20, 50)
        self.x = random.randint(0, width - self.size)
        self.y = -self.size
        self.speed = random.randint(2, 5) + parse_json('asteroid', 'speed') * level
        self.health = random.choice([10, 20, 30, 40]) + parse_json('asteroid', 'hp') * level
        self.max_health = self.health
        self.rect = pygame.Rect(self.x, self.y, self.size - 10, self.size - 10)


    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        if self.y > height:
            return True  # Удаляем астероид, если он вышел за экран
        return False

    def draw(self):
        if 20 <= self.size < 30:
            self.screen.blit(load_image("asteroids/size_25/Круглый астреоид на белом фоне_25.png", colorkey=-1),
                             (self.rect.x, self.rect.y))
        if 30 <= self.size < 40:
            self.screen.blit(load_image("asteroids/size_35/Астероид в космосе_35_new.png", colorkey=-1),
                             (self.rect.x, self.rect.y))
        if 40 <= self.size <= 50:
            self.screen.blit(load_image("asteroids/size_45/Астероид из блэндера_45_new.png", colorkey=-1),
                             (self.rect.x, self.rect.y))
        cords = (self.rect.x, self.rect.y - 5, self.health / self.max_health * self.size, 5)

        if self.max_health - self.health in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            pygame.draw.rect(self.screen, "yellow", cords)
        if self.max_health - self.health in [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
            pygame.draw.rect(self.screen, "orange", cords)
        if self.max_health - self.health in [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]:
            pygame.draw.rect(self.screen, (193, 97, 68), cords)
        if self.max_health != 10 and self.health == 10:
            pygame.draw.rect(self.screen, "red", cords)
        if self.max_health - self.health == 0:
            pygame.draw.rect(self.screen, "green", cords)

    def damage(self, dam):
        self.health = self.health - dam


class BuffBlue(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen
        self.size = 20
        self.x = random.randint(0, width - self.size)
        self.y = -self.size
        self.speed = 3
        self.health = 10

    def update(self):
        self.y += self.speed
        if self.y > height:
            return True  # Удаляем зелье, если оно вышло за экран
        return False

    def draw(self):
       self.screen.blit(load_image("buffs/blue_expir 20x32.png", colorkey=-1), (self.x, self.y))


class BuffRed(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen
        self.size = 21
        self.x = random.randint(0, width - self.size)
        self.y = -self.size
        self.speed = 4
        self.health = 10

    def update(self):
        self.y += self.speed
        if self.y > height:
            return True  # Удаляем зелье, если оно вышло за экран
        return False

    def draw(self):
       self.screen.blit(load_image("buffs/red_hp 20x28.png", colorkey=-1), (self.x, self.y))


class BuffWhite(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen
        self.size = 17
        self.x = random.randint(0, width - self.size)
        self.y = -self.size
        self.speed = 3.5
        self.health = 10

    def update(self):
        self.y += self.speed
        if self.y > height:
            return True  # Удаляем зелье, если оно вышло за экран
        return False

    def draw(self):
        self.screen.blit(load_image("buffs/white_alldamage 17x70.png", colorkey=-1), (self.x, self.y))


class Turret(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen
        self.x = width // 2
        self.y = height - 60
        self.angle = 90  # Начальный угол;
        self.speed = 8  # Скорость перемещения турели;
        self.rect = pygame.Rect(self.x, self.y, 40, 40)

    def update(self, dx):
        if num_of_ship == 8:
            if dx < 0:
                self.x += dx * self.speed - 3# Изменение координаты x, есди пользователь нажал кнопку <-;
            else:
                self.x += dx * self.speed + 3 # Изменение координаты x, есди пользователь нажал кнопку ->;
            self.x = max(0, min(self.x, 736))  # Ограничение движения по ширине экрана;
        if num_of_ship == 0 or num_of_ship == 1:
            self.x += dx * self.speed
            self.x = max(0, min(self.x, 741))  # Ограничение движения по ширине экрана;
        if num_of_ship == 9:
            self.x += dx * self.speed
            self.x = max(0, min(self.x, 755))  # Ограничение движения по ширине экрана;
        self.rect.x = self.x

    def draw(self):
        global num_of_ship
        if num_of_ship == 9:
            self.screen.blit(load_image("starships/size_45/yellow 45x41.png"), (self.x, self.y))
        if num_of_ship == 8:
            self.screen.blit(load_image("starships/size_45/white_level11 60x60.png"), (self.x, self.y))
        if num_of_ship == 1:
            self.screen.blit(load_image("starships/size_45/white_level1 56x55-no-bg-preview.png"), (self.x, self.y))
        if num_of_ship == 0:
            self.screen.blit(load_image("starships/size_45/white_level1 56x55-no-bg-preview.png"), (self.x, self.y))

    def crash(self, num):
        self.screen.blit(load_image(f"starships/crash/crash{num}.png"), (self.x - 20, self.y - 50))

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, screen, force, level):
        super().__init__()
        self.force = force
        self.screen = screen

        global num_of_ship
        if num_of_ship == 9:
            self.x = x + 22  # для испускания пуль из центра кораблей;
        elif num_of_ship == 8:
            self.x = x + 26
        else:
            self.x = x + 28.5
        self.y = y
        self.angle = math.radians(angle)  # Преобразование угла в радианы;
        if num_of_ship == 8:
            self.speed = 20 + parse_json('bullet', 'speed') * level
        else:
            self.speed = 10 + parse_json('bullet', 'speed') * level
        if num_of_ship == 9:
            self.damage = 20 + parse_json('bullet', 'damage') * level
        else:
            self.damage = 10 + parse_json('bullet', 'damage') * level

    def update(self):
        if num_of_ship == 8:
            self.y -= self.speed * math.sin(self.angle) + 18 # Y убывает вверх;
        else:
            self.y -= self.speed * math.sin(self.angle)  # Y убывает вверх;
        self.x += self.speed * math.cos(self.angle)

    def draw(self):
        if num_of_ship == 8:
            if 0 <= self.y <= 39:  # проверка пули на отдaленность от турели, если от 0 до 39, то изображение круглой;
                self.screen.blit(load_image("bullet/bullet_new_after 9x16.png"), (self.x, self.y))
            else:  # иначе более вытянутая, благодаря этому переходу кажется, что пуля увеличивает скорость(но уверяю, это не так);
                self.screen.blit(load_image("bullet/bullet_before 9x25.png"), (self.x, self.y))
        elif num_of_ship == 9:
            pygame.draw.circle(self.screen, "yellow", (int(self.x), int(self.y)), 2)
        else:
            pygame.draw.circle(self.screen, "white", (int(self.x), int(self.y)), 2)

    def is_off_screen(self):
        return self.x < 0 or self.x > width or self.y < 0 or self.y > height


class RecordsWindow:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 36)

    def get_top_scores(self):
        conn = sqlite3.connect('db/database.sqlite')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT score, time, level FROM data
            ORDER BY score DESC, time ASC, level DESC
            LIMIT 10
        ''')
        data = cursor.fetchall()
        conn.close()
        return data

    def display_highscores(self):
        scores = self.get_top_scores()
        self.screen.fill((0, 0, 0))
        y_offset = 10
        title = self.font.render("Топ-10 рекордов", True, (255, 255, 255))
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, y_offset))
        y_offset += 50

        headers = ["Место", "Score", "Time", "Level"]
        header_x = [50, 250, 450, 650]  # Позиции по горизонтали для каждого столбца
        for i, header in enumerate(headers):
            header_text = self.font.render(header, True, (255, 255, 255))
            self.screen.blit(header_text, (header_x[i], y_offset))
        y_offset += 50

        for index, (score, time, level) in enumerate(scores, start=1):
            place_text = self.font.render(str(index), True, (255, 255, 255))
            score_text = self.font.render(str(score), True, (255, 255, 255))
            time_text = self.font.render(str(time), True, (255, 255, 255))
            level_text = self.font.render(str(level), True, (255, 255, 255))
            self.screen.blit(place_text, (header_x[0], y_offset))
            self.screen.blit(score_text, (header_x[1], y_offset))
            self.screen.blit(time_text, (header_x[2], y_offset))
            self.screen.blit(level_text, (header_x[3], y_offset))
            y_offset += 40

        back_button = pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() - 60, 200, 50)
        pygame.draw.rect(self.screen, 'blue', back_button)
        pygame.draw.rect(self.screen, (21, 51, 74), back_button, 3)
        back_text = self.font.render("Назад", True, (255, 255, 255))
        self.screen.blit(back_text, (back_button.x + 55, back_button.y + 5))
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return running
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        running = 'menu'
                        return running
