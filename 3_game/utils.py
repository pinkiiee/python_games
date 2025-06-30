"""Доп утилиты"""
import pygame
import random
import os
from config import SCREEN_WIDTH, SCREEN_HEIGHT

def draw_text(text, font, color, surface, x, y):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

def find_valid_start_position(walls, player_img):
    # поиск валидной стартовой позиции без коллизий со стенами
    for _ in range(100):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 50)
        temp = pygame.sprite.Sprite()
        temp.image = player_img
        temp.rect = temp.image.get_rect(center=(x, y))
        if not pygame.sprite.spritecollideany(temp, walls):
            return (x, y)
    return (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)  # возвращаем центр, если не нашли

def save_best_score(score, filename):
    # сохранение рекорда в txt файл
    try:
        with open(filename, 'w') as f:
            f.write(str(score))
    except IOError as e:
        print(f"Ошибка сохранения счета: {e}")

def load_best_score(filename):
    # загрузка рекорда из файла
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return int(f.read())
    except (IOError, ValueError) as e:
        print(f"Ошибка загрузки счета: {e}")
    return 0  # возвращаем 0, если файла нет или ошибка