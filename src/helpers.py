import random
from constants import *


def generate_bricks_positions(grid_position, length, is_horizontal):
    bricks_position = set()
    x, y = grid_position[0], grid_position[1]
    if is_horizontal:
        for i in range(length):
            bricks_position.add((x + i, y))
    else:
        for i in range(length):
            bricks_position.add((x, y + i))
    return bricks_position


def generate_walls_positions(surface, occupied, number_of_walls):
    cols = surface.get_width() // GRID_SIZE
    rows = surface.get_height() // GRID_SIZE
    walls = []

    while len(walls) < number_of_walls:
        length = random.randint(MIN_WALL_LENGTH, MAX_WALL_LENGTH)
        horizontal = random.choice([True, False])

        if horizontal:
            x = random.randint(1, cols - length - 2)
            y = random.randint(1, rows - 2)
        else:
            x = random.randint(1, cols - 2)
            y = random.randint(1, rows - length - 2)

        wall = generate_bricks_positions((x, y), length, horizontal)
        if wall.isdisjoint(occupied):
            walls.append(wall)
            occupied.update(wall)
    return walls


def draw_border(surface, block, occupied):
    cols = surface.get_width() // GRID_SIZE
    rows = surface.get_height() // GRID_SIZE

    for x in range(cols):
        block.pixel_position = (x * GRID_SIZE, 0)
        block.draw(surface)
        occupied.add((x, 0))
        block.pixel_position = (x * GRID_SIZE, (rows - 1) * GRID_SIZE)
        block.draw(surface)
        occupied.add((x, rows - 1))

    for y in range(rows):
        block.pixel_position = (0, y * GRID_SIZE)
        block.draw(surface)
        occupied.add((0, y))
        block.pixel_position = ((cols - 1) * GRID_SIZE, y * GRID_SIZE)
        block.draw(surface)
        occupied.add((cols - 1, y))


def get_random_pixel_position(surface, occupied_positions):
    cols = surface.get_width() // GRID_SIZE
    rows = surface.get_height() // GRID_SIZE

    while True:
        grid_position = (
            random.randint(1, cols - 2),
            random.randint(1, rows - 2)
        )
        if grid_position not in occupied_positions:
            occupied_positions.add(grid_position)
            return grid_position[0] * GRID_SIZE, grid_position[1] * GRID_SIZE


def generate_time_string(current_time, start_time):
    time_seconds = (current_time - start_time) // 1000
    minutes = time_seconds // 60
    seconds = time_seconds % 60
    return f"{minutes:02}:{seconds:02}"
