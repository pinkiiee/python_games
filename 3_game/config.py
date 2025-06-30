""" Все конфигурации игры """
import pygame
import os

# основные настройки экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

class GameAssets:
    # ленивая загрузка, при загрузке данные не загружаются сразу
    def __init__(self):
        self._font = None
        self._level_settings = None
        self._speed_settings = None

    @property  # превращает метод в атрибут, который можно читать как обычное поле | декоратор
    def FONT(self):
        if self._font is None:
            self._init_font()
        return self._font

    @property
    def LEVEL_SETTINGS(self):
        if self._level_settings is None:
            self._load_level_settings()
        return self._level_settings

    @property
    def SPEED_SETTINGS(self):
        if self._speed_settings is None:
            self._load_speed_settings()
        return self._speed_settings

    def initialize(self):  # инициализация всех рес-ов
        self._init_font()
        self._load_level_settings()
        self._load_speed_settings()

    def _init_font(self):
        pygame.font.init()
        try:  # пробуем загрузить шрифт
            self._font = pygame.font.Font('assets/font.ttf', 24)
        except:  # если не получилось, загружаем Arial
            self._font = pygame.font.SysFont('Arial', 24)

    def _load_level_settings(self):
        # настройки для моих уровней игры
        self._level_settings = {
            1: {
                'background': self._load_image('assets/background_level_1.png'),
                'player_img': self._load_image('assets/player.png', alpha=True),
                'enemy_img': self._load_image('assets/enemy_level_1.png', alpha=True),
                'bonus_img': self._load_image('assets/bonus.png', alpha=True),
                'time_limit': 30,
                'score_file': 'best_score_level_1.txt',
                'walls': [
                    (200, 50, 10, 200), (200, 350, 10, 200),  # координаты стен (x, y, width, height)
                    (600, 50, 10, 200), (600, 350, 10, 200),
                    (100, 150, 200, 10), (500, 150, 200, 10),
                    (100, 450, 200, 10), (500, 450, 200, 10)
                ]
            },
            2: {
                'background': self._load_image('assets/background_level_2.png'),
                'player_img': self._load_image('assets/player.png', alpha=True),
                'enemy_img': self._load_image('assets/enemy_level_2.png', alpha=True),
                'bonus_img': self._load_image('assets/bonus.png', alpha=True),
                'time_limit': 45,
                'score_file': 'best_score_level_2.txt',
                'walls': [
                    (200, 150, 10, 100), (200, 350, 10, 100),
                    (600, 150, 10, 100), (600, 350, 10, 110),
                    (200, 150, 100, 10), (500, 150, 100, 10),
                    (200, 450, 100, 10), (500, 450, 100, 10)
                ]
            }
        }

    def _load_speed_settings(self):
        self._speed_settings = {
            'player_range': [4, 5, 6],  # Допустимые скорости игрока
            'enemy_range': [3, 4, 5, 6],   # Допустимые скорости врага
            # множители в зависимости от скорости игрока\врага
            'multipliers': {
                (4, 5): 1.2,  # player=4, enemy=5
                (4, 6): 1.5,  # player=4, enemy=6
                (5, 6): 1.2   # player=5, enemy=6
                # все остальные комбинации дают множитель 1.0
            }
        }

    def _load_image(self, path, alpha=False):
        try:
            img = pygame.image.load(path)
            return img.convert_alpha() if alpha else img.convert()
        except:
            # заглушка, если изображение не загрузилось
            surf = pygame.Surface((40, 40), pygame.SRCALPHA if alpha else 0)
            surf.fill((255, 0, 255) if not alpha else (255, 0, 255, 128))
            return surf

assets = GameAssets()