import pygame as pg
from constants import *


class Entity:
    def __init__(self, pixel_position, image):
        self.pixel_position = pixel_position
        self.grid_position = (pixel_position[0] // GRID_SIZE, pixel_position[1] // GRID_SIZE)
        self.image = pg.transform.scale(image, (GRID_SIZE, GRID_SIZE))
        self.visible = True
        self.appear_time = pg.time.get_ticks()

    def draw(self, surface):
        surface.blit(self.image, self.pixel_position)

    def update_lifetime(self, current_time):
        time_alive = current_time - self.appear_time

        if time_alive > LIFETIME:
            return 'expired'
        elif time_alive > BLINK_START:
            self.visible = (current_time // 100) % 2 == 0
        else:
            self.visible = True
        return 'ok'


class AnimatedEntity(Entity):
    def __init__(self, pixel_position, sheet, frame_count, frame_duration):
        self.sheet = sheet
        self.frame_count = frame_count
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()
        first_frame = self.sheet.get_sprite(0, 0)
        super().__init__(pixel_position, first_frame)

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update >= self.frame_duration:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.image = self.sheet.get_sprite(self.current_frame, 0)
