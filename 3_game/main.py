"""Файл для запуска игры"""
import pygame
from game import Game

def main():
    try:
        game = Game()  # экземпляр игры
        game.run()  # запуск основного игрового цикла
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()