import random
import pygame as pg
from constants import *


class GameObject:
    def __init__(self, position, image):
        self.position = (position[0], position[1])
        self.image = pg.transform.scale(image, (GRID_SIZE, GRID_SIZE))
        self.visible = True
        self.appear_time = pg.time.get_ticks()

    def draw(self, screen):
        screen.blit(self.image, self.position)

    def get_position(self):
        return (
            self.position[0] // GRID_SIZE,
            (self.position[1]) // GRID_SIZE
        )

    @staticmethod
    def get_random_pixel_position(occupied_positions):
        while True:
            grid_position = (
                random.randint(1, GRID_WIDTH - 2),
                random.randint(OFFSET // GRID_SIZE + 1, GRID_HEIGHT - 1 - OFFSET // GRID_SIZE)
            )
            print(grid_position)
            if grid_position not in occupied_positions:
                return (
                    grid_position[0] * GRID_SIZE,
                    grid_position[1] * GRID_SIZE
                )

    def update_lifetime(self, current_time):
        lifetime = 20000
        blink_start = 10000

        time_alive = current_time - self.appear_time

        if time_alive > lifetime:
            return 'expired'
        elif time_alive > blink_start:
            self.visible = (current_time // 150) % 2 == 0
        else:
            self.visible = True
        return 'ok'


class Fruit(GameObject):
    def __init__(self, image, occupied_positions):
        pixel_position = self.get_random_pixel_position(occupied_positions)
        super().__init__(pixel_position, image)

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, self.position)


class Brick(GameObject):
    def __init__(self, x, y, image):
        pixel_position = (x * GRID_SIZE, y * GRID_SIZE)
        super().__init__(pixel_position, image)


class Wall:
    def __init__(self, x, y, length, is_horizontal, image):
        self.bricks = []

        if is_horizontal:
            for i in range(length):
                self.bricks.append(Brick(x + i, y, image))
        else:
            for i in range(length):
                self.bricks.append(Brick(x, y + i, image))

    def draw(self, screen):
        for brick in self.bricks:
            brick.draw(screen)

    def get_brick_positions(self):
        return {brick.get_position() for brick in self.bricks}


class AnimatedObject(GameObject):
    def __init__(self, sheet, frame_count, occupied_positions, row=0, frame_duration=80):
        self.sheet = sheet
        self.frame_count = frame_count
        self.row = row
        self.current_frame = 0
        self.frame_duration = frame_duration
        self.last_update = pg.time.get_ticks()
        pixel_position = self.get_random_pixel_position(occupied_positions)
        first_frame = self.sheet.get_sprite(0, self.row, self.sheet.sprite_size, self.sheet.sprite_size)
        super().__init__(pixel_position, first_frame)

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % self.frame_count
            new_image = self.sheet.get_sprite(
                self.current_frame, self.row,
                self.sheet.sprite_size,
                self.sheet.sprite_size
            )
            self.image = new_image


class Fire(AnimatedObject):
    pass


class Coin(AnimatedObject):
    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, self.position)
    # @staticmethod
    # def should_appear(current_time, last_coin_time, coin_exists):
    #     return not coin_exists and (current_time - last_coin_time > 60000)

