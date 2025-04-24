
import sys
import pygame as pg
import random
from constants import *
# from game_objects import Fruit, Fire, Coin
# from snake import Snake, SpriteSheet, SnakeSkin
# from utils import draw_border, generate_walls, handle_keys


class GameObject:
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


class AnimatedObject(GameObject):
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


class SnakeSkin:
    def __init__(self, sprite_sheet):
        self.head_up = sprite_sheet.get_sprite(3, 0)
        self.head_down = sprite_sheet.get_sprite(3, 1)
        self.head_right = sprite_sheet.get_sprite(4, 0)
        self.head_left = sprite_sheet.get_sprite(4, 1)
        self.tail_up = sprite_sheet.get_sprite(1, 1)
        self.tail_down = sprite_sheet.get_sprite(0, 0)
        self.tail_right = sprite_sheet.get_sprite(0, 1)
        self.tail_left = sprite_sheet.get_sprite(1, 0)
        self.body_vertical = sprite_sheet.get_sprite(2, 0)
        self.body_horizontal = sprite_sheet.get_sprite(2, 1)
        self.body_tr = sprite_sheet.get_sprite(5, 0)
        self.body_tl = sprite_sheet.get_sprite(6, 1)
        self.body_br = sprite_sheet.get_sprite(5, 1)
        self.body_bl = sprite_sheet.get_sprite(6, 0)


class Snake:
    def __init__(self, skin, occupied):
        self.skin = skin
        self.occupied = occupied
        self.body = []
        self.reset()
        self.grow_next_move = False

    def reset(self):
        x, y = GRID_WIDTH // 2, GRID_HEIGHT // 2
        for pos in self.get_body_positions():
            self.occupied.discard(pos)
        self.direction = RIGHT
        self.body = [(x, y), (x - 1, y), (x - 2, y)]

    def get_body_positions(self):
        return set(self.body)

    def update_head(self):
        if self.direction == UP:
            self.head = self.skin.head_up
        elif self.direction == DOWN:
            self.head = self.skin.head_down
        elif self.direction == RIGHT:
            self.head = self.skin.head_right
        elif self.direction == LEFT:
            self.head = self.skin.head_left

    def update_direction(self, next_direction):
        if (self.direction == UP and next_direction != DOWN) or \
                (self.direction == DOWN and next_direction != UP) or \
                (self.direction == LEFT and next_direction != RIGHT) or \
                (self.direction == RIGHT and next_direction != LEFT):
            self.direction = next_direction

    def get_corner_type(self, prev_block, current_block, next_block):
        dx_prev = prev_block[0] - current_block[0]
        dy_next = next_block[1] - current_block[1]

        # Up-left
        if dx_prev < 0 and dy_next < 0:
            return 'tl'
        # Down-left
        elif dx_prev < 0 and dy_next > 0:
            return 'bl'
        # Up-right
        elif dx_prev > 0 and dy_next < 0:
            return 'tr'
        # Down-right
        elif dx_prev > 0 and dy_next > 0:
            return 'br'
        return None

    def draw(self, screen):
        self.update_head()

        for index, block in enumerate(self.body):
            x, y = block
            pos = (x * GRID_SIZE, y * GRID_SIZE)

            if index == 0:
                # Draw head
                screen.blit(self.head, pos)
            elif index == len(self.body) - 1:
                # Draw tail
                tail_direction = (x - self.body[-2][0], y - self.body[-2][1])
                if tail_direction == UP:
                    screen.blit(self.skin.tail_up, pos)
                elif tail_direction == DOWN:
                    screen.blit(self.skin.tail_down, pos)
                elif tail_direction == LEFT:
                    screen.blit(self.skin.tail_left, pos)
                elif tail_direction == RIGHT:
                    screen.blit(self.skin.tail_right, pos)
            else:
                prev_block = self.body[index + 1]
                next_block = self.body[index - 1]
                dx = next_block[0] - prev_block[0]
                dy = next_block[1] - prev_block[1]

                if dx == 0:
                    screen.blit(self.skin.body_vertical, pos)
                elif dy == 0:
                    screen.blit(self.skin.body_horizontal, pos)
                else:
                    if (prev_block[0] < x and next_block[1] < y) or (next_block[0] < x and prev_block[1] < y):
                        screen.blit(self.skin.body_tl, pos)
                    elif (prev_block[0] < x and next_block[1] > y) or (next_block[0] < x and prev_block[1] > y):
                        screen.blit(self.skin.body_bl, pos)
                    elif (prev_block[0] > x and next_block[1] < y) or (next_block[0] > x and prev_block[1] < y):
                        screen.blit(self.skin.body_tr, pos)
                    elif (prev_block[0] > x and next_block[1] > y) or (next_block[0] > x and prev_block[1] > y):
                        screen.blit(self.skin.body_br, pos)

    def move(self, is_obstacle):
        if not is_obstacle:
            next_head = self.get_next_head()
            self.body.insert(0, next_head)
            self.occupied.add(next_head)
            if not self.grow_next_move:
                tail = self.body.pop()
                self.occupied.discard(tail)
            else:
                self.grow_next_move = False

    def get_head(self):
        return self.body[0]

    def get_next_head(self):
        head_x, head_y = self.get_head()
        dx, dy = self.direction
        return head_x + dx, head_y + dy


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


def generate_walls_positions(surface, occupied):
    cols = surface.get_width() // GRID_SIZE
    rows = surface.get_height() // GRID_SIZE
    walls = []

    while len(walls) < NUM_WALLS:
        length = random.randint(MIN_WALLS, MAX_WALLS)
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


def draw_walls(surface, walls, image):
    for wall in walls:
        for position in wall:
            pixel_position = (position[0] * GRID_SIZE, position[1] * GRID_SIZE)
            wall_block = GameObject(pixel_position, image)
            wall_block.draw(surface)


def draw_border(surface, image, occupied):
    cols = surface.get_width() // GRID_SIZE
    rows = surface.get_height() // GRID_SIZE

    border_block = GameObject((0, 0), image)

    for x in range(cols):
        border_block.pixel_position = (x * GRID_SIZE, 0)
        border_block.draw(surface)
        occupied.add((x, 0))
        border_block.pixel_position = (x * GRID_SIZE, (rows - 1) * GRID_SIZE)
        border_block.draw(surface)
        occupied.add((x, rows - 1))

    for y in range(rows):
        border_block.pixel_position = (0, y * GRID_SIZE)
        border_block.draw(surface)
        occupied.add((0, y))
        border_block.pixel_position = ((cols - 1) * GRID_SIZE, y * GRID_SIZE)
        border_block.draw(surface)
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


def main():
    pg.init()
    pg.mixer.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    pg.display.set_caption('Snake Game')
    clock = pg.time.Clock()
    pg.font.init()
    font = pg.font.SysFont('Arial', 24)

    occupied_positions = set()
    # Occupy positions for initial snake in the middle
    x, y = GRID_WIDTH // 2, GRID_HEIGHT // 2
    occupied_positions.add((x, y))
    occupied_positions.add((x - 1, y))
    occupied_positions.add((x - 2, y))

    score = 0
    coins = 0

    # Download images
    bush_image = pg.image.load("./images/bush.png").convert_alpha()
    wall_image = pg.image.load("./images/wall.png").convert_alpha()
    apple_image = pg.image.load("./images/apple.png").convert_alpha()
    fire_sheet = SpriteSheet("./images/CampFireFinished.png", 64)
    coin_sheet = SpriteSheet("./images/coin_sheet.png", 128)
    snake_sheet = SpriteSheet("./images/snake_sheet.png", 40)
    snake_skin = SnakeSkin(snake_sheet)

    rows = SCREEN_WIDTH // GRID_SIZE
    cols = SCREEN_HEIGHT // GRID_SIZE

    scoreboard_surface = pg.Surface((SCREEN_WIDTH, SCOREBOARD_HEIGHT))
    game_surface = pg.Surface((SCREEN_WIDTH, (SCREEN_HEIGHT - SCOREBOARD_HEIGHT)))

    walls = generate_walls_positions(game_surface, occupied_positions)

    fires = []
    for _ in range(NUM_FIRES):
        fire = AnimatedObject(
            get_random_pixel_position(game_surface, occupied_positions),
            fire_sheet, 5, 40)
        fires.append(fire)

    apple = GameObject(get_random_pixel_position(game_surface, occupied_positions), apple_image)

    coin = None
    last_coin_time = pg.time.get_ticks()

    snake = Snake(snake_skin, occupied_positions)

    while True:
        screen.fill((0, 0, 0))
        scoreboard_surface.fill((30, 30, 30))
        game_surface.fill(BOARD_BACKGROUND_COLOR)
        handle_keys(snake)

        is_obstacle = False
        snake_head = snake.get_head()
        next_head = snake.get_next_head()

        current_time = pg.time.get_ticks()
        apple_state = apple.update_lifetime(current_time)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        text = font.render(f"Score: {score} Coins: {coins}", True, (255, 255, 255))
        scoreboard_surface.blit(text, (10, 25))

        # Check collisions
        out_of_bounds = (
            next_head[0] < 1 or
            next_head[0] >= GRID_WIDTH - 1 or
            next_head[1] < 1 or
            next_head[1] >= GRID_HEIGHT - OFFSET_Y // GRID_SIZE - 1
        )
        hits_wall = any(next_head in wall for wall in walls)
        bites_self = next_head in list(snake.body)[1:]

        if out_of_bounds or hits_wall or bites_self:
            is_obstacle = True
            if out_of_bounds or bites_self:
                pg.mixer.Sound("./sounds/GameOver.mp3").play()
                snake.reset()
                occupied_positions.discard(apple.grid_position)
                apple = GameObject(get_random_pixel_position(game_surface, occupied_positions), apple_image)
            else:
                pg.mixer.Sound("./sounds/rock_break.mp3").play()
                score = max(0, score - 1)

        if not is_obstacle:
            snake.move(is_obstacle)

        if apple.grid_position == snake_head:
            pg.mixer.Sound("./sounds/apple_bite.mp3").play()
            snake.grow_next_move = True
            occupied_positions.discard(apple.grid_position)
            apple = GameObject(get_random_pixel_position(game_surface, occupied_positions), apple_image)
            score += 1

        if coin and coin.grid_position == snake_head:
            pg.mixer.Sound("./sounds/shimmer.mp3").play()
            coins += 1
            occupied_positions.discard(coin.grid_position)
            coin = None
            last_coin_time = current_time

        for fire in fires:
            if snake_head == fire.grid_position:
                if coins > 0:
                    pg.mixer.Sound("./sounds/alarme.mp3").play()
                    coins -= 1
                else:
                    pg.mixer.Sound("./sounds/GameOver.mp3").play()
                    snake.reset()
                    occupied_positions.discard(apple.grid_position)
                    apple = GameObject(get_random_pixel_position(game_surface, occupied_positions), apple_image)

        draw_border(game_surface, bush_image, occupied_positions)
        draw_walls(game_surface, walls, wall_image)

        for fire in fires:
            fire.update()
            fire.draw(game_surface)

        if apple_state == 'expired':
            if apple.grid_position in occupied_positions:
                occupied_positions.discard(apple.grid_position)
            new_position = get_random_pixel_position(game_surface, occupied_positions)
            apple = GameObject(new_position, apple_image)

        if apple.visible:
            apple.draw(game_surface)

        if coin is None and current_time - last_coin_time >= COIN_COOLDOWN:
            coin = AnimatedObject(get_random_pixel_position(game_surface, occupied_positions),
                                  coin_sheet, 8, 1)
            last_coin_time = current_time

        if coin:
            if coin.update_lifetime(current_time) == 'expired':
                occupied_positions.discard(coin.grid_position)
                coin = None
            else:
                coin.update()
                coin.draw(game_surface)

        snake.draw(game_surface)

        screen.blit(scoreboard_surface, (0, 0))
        screen.blit(game_surface, (0, SCOREBOARD_HEIGHT))

        pg.display.flip()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
