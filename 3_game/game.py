"""Основной класс игры"""
import pygame
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, assets
from sprites import Player, Enemy, Bonus, Wall
from utils import draw_text, find_valid_start_position, save_best_score, load_best_score
from menus import MainMenu, GameOverMenu, LevelCompleteMenu, SpeedSelectMenu


class Game:
    def __init__(self):
        # инициализация pygame и создание окна
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Игра: Побег от одногруппниц")
        # инициализация игровых ресурсов
        assets.initialize()

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"
        self.level = 1
        self.score = 0
        self.score_multiplier = 1.0
        self.best_scores = {  # загрузка рекордов
            1: load_best_score(assets.LEVEL_SETTINGS[1]['score_file']),
            2: load_best_score(assets.LEVEL_SETTINGS[2]['score_file'])
        }
        # настройки скорости по дефолту
        self.player_speed = 4
        self.enemy_speed = 4

        self.main_menu = MainMenu(self)
        self.speed_select_menu = SpeedSelectMenu(self)
        self.game_over_menu = GameOverMenu(self)
        self.level_complete_menu = LevelCompleteMenu(self)
        # игровые объекты (инициализируются при загрузке уровня)
        self.player = None
        self.enemy = None
        self.beer_bonus = None
        self.walls = None
        self.all_sprites = None
        self.level_complete_time = 0

    def load_level(self, level):  # загрузка указанного уровня
        # проверка на максимальный уровень
        if level > len(assets.LEVEL_SETTINGS):
            level = len(assets.LEVEL_SETTINGS)

        self.level = level
        level_data = assets.LEVEL_SETTINGS[level]
        # создание групп спрайтов
        self.walls = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        # создание стен
        for wall in level_data['walls']:
            wall_sprite = Wall(*wall)
            self.walls.add(wall_sprite)
            self.all_sprites.add(wall_sprite)
        # создание игрока
        player_pos = find_valid_start_position(self.walls, level_data['player_img'])
        self.player = Player(level_data['player_img'], player_pos)
        self.player.base_speed = self.player_speed
        self.player.speed = self.player_speed
        self.player.game = self  # ссылка на игру
        self.all_sprites.add(self.player)
        # создание врага
        enemy_img = pygame.transform.scale(level_data['enemy_img'], (35, 35))
        enemy_pos = self._find_enemy_position(player_pos)
        self.enemy = Enemy(self.player, enemy_img, self.enemy_speed)
        self.enemy.rect.center = enemy_pos
        self.all_sprites.add(self.enemy)
        # создание бонуса
        self.beer_bonus = Bonus(level_data['bonus_img'])
        self.all_sprites.add(self.beer_bonus)
        # сброс параметров игры
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.level_complete_time = 0

    def _find_enemy_position(self, player_pos):
        min_distance = 250  # минимальное расстояние от игрока
        for _ in range(100):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            # проверка расстояния до игрока
            distance = ((x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2) ** 0.5
            if distance < min_distance:
                continue  # слишком близко к игроку
            # проверка коллизий со стенами
            temp_rect = pygame.Rect(x - 20, y - 20, 40, 40)
            if any(temp_rect.colliderect(wall.rect) for wall in self.walls):
                continue  # пересекается со стеной

            return (x, y)
        return (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def run(self):
        while self.running:
            self.clock.tick(FPS)  # ограничение фпс
            self._handle_events()
            self._update()
            self._render()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == "menu":
                self.main_menu.handle_event(event)
            elif self.state == "speed_select":
                self.speed_select_menu.handle_event(event)
            elif self.state == "game_over":
                self.game_over_menu.handle_event(event)
            elif self.state == "level_complete":
                self.level_complete_menu.handle_event(event)

    def _update(self):  # обновление игрового состояния, проверки
        if self.state != "playing":
            return

        current_time = pygame.time.get_ticks()
        self.player.update(self.walls)

        if self.player.stationary_time >= self.player.max_stationary_time:
            self.state = "game_over"
            return

        self.enemy.update(self.walls)

        if pygame.sprite.collide_rect(self.player, self.beer_bonus):
            self.player.activate_beer_bonus()
            self.beer_bonus.reset_position()

        if pygame.sprite.collide_rect(self.player, self.enemy):
            self.state = "game_over"
            return

        elapsed_time = (current_time - self.start_time) / 1000
        if elapsed_time >= assets.LEVEL_SETTINGS[self.level]['time_limit']:
            self._complete_level()

        if current_time % 5 == 0:  # увеличение счета (каждые 5 мс)
            self.score += int(1 * self.score_multiplier)

    def _complete_level(self):  # завершение текущего уровня
        self.level_complete_time = pygame.time.get_ticks()
        # обновление рекорда
        self.best_scores[self.level] = max(self.score, self.best_scores[self.level])
        save_best_score(self.best_scores[self.level],
                        assets.LEVEL_SETTINGS[self.level]['score_file'])
        # переход в состояние завершения уровня
        self.state = "level_complete"

    def _render(self):  # отрисовка игры
        if self.state == "playing":
            level_data = assets.LEVEL_SETTINGS[self.level]
            self.screen.blit(level_data['background'], (0, 0))  # фон
            self.all_sprites.draw(self.screen)  # все спрайты
            # расчёт времени
            current_time = (pygame.time.get_ticks() - self.start_time) / 1000
            time_limit = assets.LEVEL_SETTINGS[self.level]['time_limit']
            # отрисовка интерфейса
            draw_text(f"Уровень: {self.level}", assets.FONT, (255, 255, 255), self.screen, 20, 20)
            draw_text(f"Счёт: {self.score}", assets.FONT, (255, 255, 255), self.screen, 20, 50)
            draw_text(f"Множитель: x{self.score_multiplier}", assets.FONT, (200, 255, 200), self.screen, 20, 80)
            # время (краснеет при малом остатке)
            draw_text(f"Время: {int(current_time)}/{time_limit}", assets.FONT,
                      (255, 150, 150) if current_time > time_limit - 10 else (255, 255, 255),
                      self.screen, SCREEN_WIDTH - 150, 20)
            # бонусы (краснеет при сборе 2+)
            draw_text(f"Бонус: {self.player.beer_count}/3", assets.FONT,
                      (255, 50, 50) if self.player.beer_count >= 2 else (200, 200, 200),
                      self.screen, SCREEN_WIDTH - 150, 50)
            # таймер бездействия (краснеет при малом остатке)
            remaining_time = max(0, (self.player.max_stationary_time - self.player.stationary_time) // 1000)
            draw_text(f"АФК лимит: {remaining_time} сек", assets.FONT,
                      (255, 50, 50) if remaining_time < 3 else (200, 200, 200),
                      self.screen, SCREEN_WIDTH - 150, 80)

        elif self.state == "menu":
            self.main_menu.draw(self.screen)
        elif self.state == "speed_select":
            self.speed_select_menu.draw(self.screen)
        elif self.state == "game_over":
            self.game_over_menu.draw(self.screen)
        elif self.state == "level_complete":
            self.level_complete_menu.draw(self.screen)
        # обновление экрана
        pygame.display.flip()