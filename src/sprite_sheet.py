import pygame as pg
from constants import GRID_SIZE


class SpriteSheet:
    def __init__(self, file, sprite_size):
        self.sheet = pg.image.load(file).convert_alpha()
        self.sprite_size = sprite_size

    def get_sprite(self, frame_x, frame_y):
        rect = pg.Rect(
            frame_x * self.sprite_size,
            frame_y * self.sprite_size,
            self.sprite_size,
            self.sprite_size
        )
        sprite = pg.Surface((self.sprite_size, self.sprite_size), pg.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), rect)
        return pg.transform.scale(sprite, (GRID_SIZE, GRID_SIZE))
