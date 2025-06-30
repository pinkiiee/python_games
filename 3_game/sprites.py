""" Классы всех игровых объектов """
import pygame
import random
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT  # константы из config

class Player(pygame.sprite.Sprite):
    def __init__(self, image, start_pos):
        super().__init__() # вызов родительского класса, встроенного в pygame
        self.image = pygame.transform.scale(image, (30, 30))
        self.rect = self.image.get_rect(center=start_pos)  # позиция и хитбокс
        self.base_speed = 4  # Базовая скорость, будет изменяться
        self.speed = self.base_speed  # текущая скорость
        self.bonus_speed = 0
        self.last_movement_time = pygame.time.get_ticks()
        self.stationary_time = 0
        self.max_stationary_time = 7000  # макс время афк
        self.last_position = start_pos
        self.beer_count = 0
        self.max_beer = 3
        self.bonus_active_time = 0
        self.max_bonus_time = 3000

    def update(self, walls):
        # обновление состояния игрока
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        current_speed = self.speed + self.bonus_speed

        # обработка управления (WASD вместо стрелочек)
        if keys[pygame.K_a]: dx -= current_speed
        if keys[pygame.K_d]: dx += current_speed
        if keys[pygame.K_w]: dy -= current_speed
        if keys[pygame.K_s]: dy += current_speed

        # обновление времени афк
        if dx != 0 or dy != 0:
            self.last_movement_time = current_time
            self.stationary_time = 0
        else:
            self.stationary_time = current_time - self.last_movement_time

        self._move(dx, dy, walls)

        # отключение бонуса по истечении времени
        if self.bonus_speed > 0 and current_time - self.bonus_active_time > self.max_bonus_time:
            self.bonus_speed = 0

    def _move(self, dx, dy, walls):
        # движение с проверкой коллизий
        old_pos = self.rect.topleft
        self.rect.x += dx
        if pygame.sprite.spritecollideany(self, walls):
            self.rect.x = old_pos[0]

        self.rect.y += dy
        if pygame.sprite.spritecollideany(self, walls):
            self.rect.y = old_pos[1]

        # ограничение по границам экрана
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

    def activate_beer_bonus(self):
        # активация бонуса
        self.beer_count += 1
        self.bonus_speed = 3
        self.bonus_active_time = pygame.time.get_ticks()

        # если максимум собран, игра завершается
        if self.beer_count >= self.max_beer and hasattr(self, 'game'):
            self.game.state = "game_over"

    def is_stationary_too_long(self):
        return self.stationary_time >= self.max_stationary_time

    def update_speed(self, new_speed):
        self.base_speed = new_speed
        self.speed = new_speed

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player, image, speed=5.0):
        super().__init__()
        self.image = pygame.transform.scale(image, (35, 35))
        self.rect = self.image.get_rect()
        self.player = player
        self.base_speed = speed
        self.speed = speed
        self.path = []
        self.last_update = pygame.time.get_ticks()
        self.last_positions = []  # история позиций
        self.check_corners_time = 0  # время последней проверки углов

    def update(self, walls):
        now = pygame.time.get_ticks()
        # увеличение скорости со временем
        self.speed = self.base_speed * (1 + (now - self.player.game.start_time) / 45000)

        # проверка углов каждую секунду
        if now - self.check_corners_time > 1000:
            self._check_hiding_spots(walls)
            self.check_corners_time = now
        # сохранение позиции для проверки застревания
        self.last_positions.append((self.rect.x, self.rect.y))
        if len(self.last_positions) > 10:
            self.last_positions.pop(0)
        # обновление пути каждые 200 мс или если путь закончился/враг застрял
        if now - self.last_update > 200 or not self.path or self._is_stuck():
            self._update_path(walls)
            self.last_update = now

        if self.path:
            target = self.path[0]
            dx = target[0] - self.rect.centerx
            dy = target[1] - self.rect.centery
            dist = max(1, math.hypot(dx, dy))

            if dist < 5:
                self.path.pop(0)
            else:
                move_x = (dx / dist) * self.speed
                move_y = (dy / dist) * self.speed

                self.rect.x += move_x
                collided = pygame.sprite.spritecollideany(self, walls)
                if collided:
                    self.rect.x -= move_x
                    self._adjust_movement(walls, move_x, move_y, 'x')

                self.rect.y += move_y
                collided = pygame.sprite.spritecollideany(self, walls)
                if collided:
                    self.rect.y -= move_y
                    self._adjust_movement(walls, move_x, move_y, 'y')

        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

    def _is_stuck(self):
        # проверка, застрял ли враг
        if len(self.last_positions) < 5:
            return False
        # суммарное перемещение за последние 5 кадров
        total_movement = sum(
            math.hypot(self.last_positions[i][0] - self.last_positions[i-1][0],
                      self.last_positions[i][1] - self.last_positions[i-1][1])
            for i in range(1, len(self.last_positions)))
        return total_movement < 15  # если мало двигался - значит застрял

    def _check_hiding_spots(self, walls):
        # проверка углов экрана как возможных точек для движения
        hiding_spots = [
            (50, 50),
            (SCREEN_WIDTH - 50, 50),
            (50, SCREEN_HEIGHT - 50),
            (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50)
        ]
        for spot in hiding_spots:
            if not self._check_wall_collision((self.rect.centerx, self.rect.centery), spot, walls):
                self.path.append(spot)
                break

    def _update_path(self, walls):
        # обновление пути к игроку
        start = (self.rect.centerx, self.rect.centery)
        end = (self.player.rect.centerx, self.player.rect.centery)
        # прямой путь без коллизий
        if not self._check_wall_collision(start, end, walls):
            self.path = [end]
            return

        self.path = self._find_complex_path(start, end, walls)
        if not self.path:
            self.path = [(random.randint(50, SCREEN_WIDTH - 50),
                         random.randint(50, SCREEN_HEIGHT - 50))]

    def _find_complex_path(self, start, end, walls):
        key_points = [
            (SCREEN_WIDTH // 2, 50),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50),
            (100, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)
        ]
        random.shuffle(key_points)
        # поиск точки, через которую можно добраться до игрока
        for point in key_points:
            if not self._check_wall_collision(start, point, walls) and \
               not self._check_wall_collision(point, end, walls):
                return [point, end]
        # если не нашли - пробуем случайные точки
        for _ in range(5):
            point = (random.randint(50, SCREEN_WIDTH - 50),
                    random.randint(50, SCREEN_HEIGHT - 50))
            if not self._check_wall_collision(start, point, walls) and \
               not self._check_wall_collision(point, end, walls):
                return [point, end]
        return []

    def _check_wall_collision(self, start, end, walls):
        # проверка коллизии линии со стенами
        steps = max(abs(end[0] - start[0]), abs(end[1] - start[1])) // 5
        if steps == 0:
            return False

        for i in range(steps + 1):
            x = start[0] + (end[0] - start[0]) * i / steps
            y = start[1] + (end[1] - start[1]) * i / steps
            temp_rect = pygame.Rect(x - 15, y - 15, 30, 30)
            if any(temp_rect.colliderect(wall.rect) for wall in walls):
                return True
        return False

    def _adjust_movement(self, walls, move_x, move_y, axis):
        # корректировка движения при столкновении
        for angle in [-30, 30, -60, 60]:  # пробуем разные углы
            rad = math.radians(angle)
            new_x = move_x * math.cos(rad) - move_y * math.sin(rad)
            new_y = move_x * math.sin(rad) + move_y * math.cos(rad)

            if axis == 'x':
                self.rect.x += new_x * 0.8
            else:
                self.rect.y += new_y * 0.8

            if not pygame.sprite.spritecollideany(self, walls):
                return

            if axis == 'x':
                self.rect.x -= new_x * 0.8
            else:
                self.rect.y -= new_y * 0.8

    def update_speed(self, new_speed):
        # обновление скорости
        self.base_speed = new_speed
        self.speed = new_speed

class Bonus(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (25, 25))
        self.rect = self.image.get_rect()
        self.reset_position()  # установка начальной позиции

    def reset_position(self):
        # установка случайной позиции
        self.rect.x = random.randint(50, SCREEN_WIDTH - 50)
        self.rect.y = random.randint(50, SCREEN_HEIGHT - 50)

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((60, 60, 80))  # цвет стен (сейчас серый)
        self.rect = self.image.get_rect(topleft=(x, y))  # позиция и размер