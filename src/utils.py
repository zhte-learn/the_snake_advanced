import pygame as pg
import random
from game_objects import Wall, GameObject
from constants import *


def draw_border(screen, image):
    border_block = GameObject((0, 0), image)

    for x in range(SCREEN_WIDTH // GRID_SIZE):
        border_block.position = (x * GRID_SIZE, OFFSET)
        border_block.draw(screen)
        border_block.position = (x * GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE)
        border_block.draw(screen)

    for y in range(OFFSET // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE):
        border_block.position = (0, y * GRID_SIZE)
        border_block.draw(screen)
        border_block.position = (SCREEN_WIDTH - GRID_SIZE, y * GRID_SIZE)
        border_block.draw(screen)


def generate_walls(
        num_walls,
        min_len,
        max_len,
        wall_image,
        occupied_positions
):
    walls = []

    while len(walls) < num_walls:
        length = random.randint(min_len, max_len)
        horizontal = random.choice([True, False])

        if horizontal:
            x = random.randint(1, GRID_WIDTH - length - 2)
            y = random.randint(OFFSET // GRID_SIZE + 1, GRID_HEIGHT - 1 - OFFSET // GRID_SIZE)
        else:
            x = random.randint(1, GRID_WIDTH - 2)
            y = random.randint(OFFSET // GRID_SIZE + 1, (GRID_HEIGHT - 1 - OFFSET // GRID_SIZE) - length)

        wall = Wall(x, y, length, horizontal, wall_image)
        wall_positions = wall.get_brick_positions()

        if wall_positions.isdisjoint(occupied_positions):
            walls.append(wall)
            occupied_positions.update(wall_positions)

    return walls


def upload_and_scale_image(image_url):
    return pg.transform.scale(
        pg.image.load(image_url).convert_alpha(),
        (GRID_SIZE, GRID_SIZE))


def handle_keys(game_object):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.update_direction(UP)
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.update_direction(DOWN)
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.update_direction(LEFT)
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.update_direction(RIGHT)
            elif event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit


def is_out_of_bounds(next_head):
    return next_head[0] < 0 or next_head[0] >= GRID_WIDTH or next_head[1] < 0 or next_head[1] >= GRID_HEIGHT
