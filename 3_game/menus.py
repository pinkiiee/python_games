"""Файл с менюшкой игры"""
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, assets
from utils import draw_text


class Button:
    def __init__(self, x, y, width, height, text, action=None):  # магический метод, дандер метод
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.colors = {  # цвета для разных состояний
            'normal': (70, 70, 70),  # просто кнопка
            'hover': (100, 100, 100),  # при наведении на кнопку
            'border': (150, 150, 150)  # рамка
        }
        self.current_color = self.colors['normal']
        self.border_radius = 5  # скругление углов
        self.border_width = 2  # толщина рамки

    def draw(self, surface):
        # отрисовка кнопки
        pygame.draw.rect(
            surface,
            self.colors['border'],
            self.rect,
            border_radius=self.border_radius,
            width=self.border_width
        )
        pygame.draw.rect(
            surface,
            self.current_color,
            self.rect,
            border_radius=self.border_radius
        )
        text_surf = assets.FONT.render(self.text, True, (255, 255, 255)) # цвет текста на кнопках
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # изменение цвета при наведении
            self.current_color = self.colors['hover' if self.rect.collidepoint(event.pos) else 'normal']
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return self.action  # возвращаем действие при клике
        return None


class MainMenu:
    def __init__(self, game):
        self.game = game
        center_x = SCREEN_WIDTH // 2
        self.buttons = [  # кнопки менюшки
            Button(center_x - 100, 250, 200, 50, "Начать игру", "speed_select"),
            Button(center_x - 100, 320, 200, 50, "Выйти", "exit")
        ]

    def draw(self, surface):
        surface.blit(assets.LEVEL_SETTINGS[1]['background'], (0, 0))  # фон менюшки

        title = assets.FONT.render("ПОБЕГ ОТ ОДНОГРУППНИЦ", True, (255, 50, 50))
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))
        # отображение рекордов из txt файлов
        best1 = assets.FONT.render(f"Рекорд 1 лвл: {self.game.best_scores[1]}", True, (255, 255, 255))
        best2 = assets.FONT.render(f"Рекорд 2 лвл: {self.game.best_scores[2]}", True, (255, 255, 255))
        surface.blit(best1, (SCREEN_WIDTH // 2 - best1.get_width() // 2, 180))
        surface.blit(best2, (SCREEN_WIDTH // 2 - best2.get_width() // 2, 210))

        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event):
        for button in self.buttons:
            action = button.handle_event(event)
            if action == "speed_select":  # переход к менюшке с выбором скорости
                self.game.state = "speed_select"
            elif action == "exit":
                self.game.running = False  # выход из игры


class SpeedSelectMenu:
    def __init__(self, game):
        self.game = game
        self.selected_player_speed = 0  # индекс скорости по умолчанию (4)
        self.selected_enemy_speed = 0  # индекс скорости по умолчанию (4)

        center_x = SCREEN_WIDTH // 2
        self.buttons = [  # кнопки менюшки с выбором скорости
            Button(center_x - 150, 400, 300, 50, "Начать игру", "start"),
            Button(center_x - 150, 470, 300, 50, "Назад", "back"),
            Button(center_x - 200, 250, 40, 40, "<", "player_speed_down"),
            Button(center_x + 160, 250, 40, 40, ">", "player_speed_up"),
            Button(center_x - 200, 300, 40, 40, "<", "enemy_speed_down"),
            Button(center_x + 160, 300, 40, 40, ">", "enemy_speed_up")
        ]

    def draw(self, surface):
        surface.blit(assets.LEVEL_SETTINGS[1]['background'], (0, 0))

        title = assets.FONT.render("Выберите сложность", True, (255, 255, 255)) # цвет текста
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))
        # получение текущих скоростей и множителя
        player_speed = assets.SPEED_SETTINGS['player_range'][self.selected_player_speed]
        enemy_speed = assets.SPEED_SETTINGS['enemy_range'][self.selected_enemy_speed]
        multiplier = assets.SPEED_SETTINGS['multipliers'].get((player_speed, enemy_speed), 1.0)
        # отрисовка текста
        player_text = assets.FONT.render(f"Скорость игрока: {player_speed}", True, (200, 200, 255))
        enemy_text = assets.FONT.render(f"Скорость врага: {enemy_speed}", True, (255, 200, 200))
        bonus_text = assets.FONT.render(f"Множитель очков: x{multiplier}", True, (200, 255, 200))

        surface.blit(player_text, (SCREEN_WIDTH // 2 - player_text.get_width() // 2, 250))
        surface.blit(enemy_text, (SCREEN_WIDTH // 2 - enemy_text.get_width() // 2, 300))
        surface.blit(bonus_text, (SCREEN_WIDTH // 2 - bonus_text.get_width() // 2, 350))

        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event):
        for button in self.buttons:
            action = button.handle_event(event)
            if action == "start":
                # установка выбранных скоростей и множителя
                self.game.player_speed = assets.SPEED_SETTINGS['player_range'][self.selected_player_speed]
                self.game.enemy_speed = assets.SPEED_SETTINGS['enemy_range'][self.selected_enemy_speed]
                speeds = (self.game.player_speed, self.game.enemy_speed)
                self.game.score_multiplier = assets.SPEED_SETTINGS['multipliers'].get(speeds, 1.0)
                self.game.state = "playing"  # начало игры
                self.game.load_level(1)  # загрузка первого уровня
            elif action == "back":
                self.game.state = "menu"  # возврат в главное меню
            elif action == "player_speed_down":
                self.selected_player_speed = max(0, self.selected_player_speed - 1)
            elif action == "player_speed_up":
                self.selected_player_speed = min(len(assets.SPEED_SETTINGS['player_range']) - 1,
                                                 self.selected_player_speed + 1)
            elif action == "enemy_speed_down":
                self.selected_enemy_speed = max(0, self.selected_enemy_speed - 1)
            elif action == "enemy_speed_up":
                self.selected_enemy_speed = min(len(assets.SPEED_SETTINGS['enemy_range']) - 1,
                                                self.selected_enemy_speed + 1)

class GameOverMenu:
    def __init__(self, game):
        self.game = game
        center_x = SCREEN_WIDTH // 2
        self.buttons = [  # кнопки менюшки проигрыша
            Button(center_x - 100, 350, 200, 50, "Повторить", "retry"),
            Button(center_x - 100, 420, 200, 50, "Выйти", "exit")
        ]
        if self.game.level > 1:
            # добавляем кнопку для 1 уровня, если играли не на первом
            self.buttons.insert(1, Button(center_x - 100, 385, 200, 50, "Уровень 1", "level1"))

    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        title = assets.FONT.render("ИГРА ОКОНЧЕНА", True, (255, 0, 0))
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))

        # определение причины проигрыша
        if self.game.player.beer_count >= 3:
            reason = "Вам поплохело. Не нужно было столько пить! (3/3)!"
        elif self.game.player.stationary_time >= 7000:
            reason = "Вы были АФК слишком долго!"
        else:
            reason = "Вас поймала одногруппница!"

        reason_text = assets.FONT.render(reason, True, (255, 255, 255))
        surface.blit(reason_text, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, 180))
        # статистика игры
        stats = [
            f"Уровень: {self.game.level}",
            f"Счёт: {self.game.score}",
            f"Собрано бонусов: {self.game.player.beer_count}/3"
        ]

        for i, stat in enumerate(stats):
            text = assets.FONT.render(stat, True, (255, 255, 255))
            surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 230 + i * 40))

        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event):
        for button in self.buttons:
            action = button.handle_event(event)
            if action == "retry":
                self.game.state = "playing"  # повтор уровня
                self.game.load_level(self.game.level)
            elif action == "level1":
                self.game.state = "playing"  # переход на 1 уровень
                self.game.load_level(1)
            elif action == "exit":
                self.game.running = False  # выход из игры


class LevelCompleteMenu:
    def __init__(self, game):
        self.game = game
        center_x = SCREEN_WIDTH // 2
        self.buttons = [  # кнопки менюшки выигрыша
            Button(center_x - 150, 350, 300, 50, "Следующий уровень", "next_level"),
            Button(center_x - 150, 420, 300, 50, "Повторить уровень", "retry"),
            Button(center_x - 150, 490, 300, 50, "Выйти в меню", "menu")
        ]

    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        title = assets.FONT.render("УРОВЕНЬ ПРОЙДЕН!", True, (0, 200, 0))
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))

        # статистика уровня
        finish_time = (self.game.level_complete_time - self.game.start_time) / 1000

        stats = [
            f"Уровень: {self.game.level}",
            f"Финальный счёт: {self.game.score}",
            f"Множитель: x{self.game.score_multiplier}",
            f"Время прохождения: {int(finish_time)} сек",
            f"Бонусов собрано: {self.game.player.beer_count}/3"
        ]

        for i, stat in enumerate(stats):
            text = assets.FONT.render(stat, True, (255, 255, 255))
            surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 180 + i * 35))

        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event):
        for button in self.buttons:
            action = button.handle_event(event)
            if action == "next_level":
                self.game.load_level(self.game.level + 1)  # cледующий уровень
                self.game.state = "playing"
            elif action == "retry":
                self.game.load_level(self.game.level)  # повтор уровня
                self.game.state = "playing"
            elif action == "menu":
                self.game.state = "menu"  # выход в главное меню