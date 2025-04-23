
import sys
import pygame as pg
from constants import *
from game_objects import Fruit, Fire, Coin
from snake import Snake, SpriteSheet, SnakeSkin
from utils import draw_border, generate_walls, handle_keys


def main():
    pg.init()
    pg.mixer.init()
    clock = pg.time.Clock()
    pg.display.set_caption('Snake Game')
    pg.font.init()
    font = pg.font.SysFont('Arial', 24)
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    occupied_positions = set()

    # Download images
    bush_image = pg.image.load("../images/bush.png").convert_alpha()
    wall_image = pg.image.load("../images/wall.png").convert_alpha()
    apple_image = pg.image.load("../images/apple.png").convert_alpha()
    fire_sheet = SpriteSheet("../images/CampFireFinished.png", 64)
    coin_sheet = SpriteSheet("../images/coin_sheet.png", 128)
    snake_sheet = SpriteSheet("../images/snake_sheet.png", 40)
    snake_skin = SnakeSkin(snake_sheet)

    # Create a snake
    snake = Snake(snake_skin)
    occupied_positions.update(snake.get_body_positions())

    # Create walls
    walls = generate_walls(
        num_walls=NUM_WALLS,
        min_len=WALL_MIN,
        max_len=WALL_MAX,
        wall_image=wall_image,
        occupied_positions=occupied_positions
    )
    wall_positions = []
    for wall in walls:
        occupied_positions.update(wall.get_brick_positions())
        for brick in list(wall.get_brick_positions()):
            wall_positions.append(brick)

    # Create an apple
    apple = Fruit(apple_image, occupied_positions)
    occupied_positions.update(apple.get_position())

    # Create fire
    fires = []
    for _ in range(5):
        fire = Fire(
            sheet=fire_sheet,
            frame_count=5,
            occupied_positions=occupied_positions,
            row=0,
            frame_duration=40
        )
        occupied_positions.update(fire.get_position())
        fires.append(fire)

    coin = None
    last_coin_time = pg.time.get_ticks()
    score = 0
    coins = 0

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        is_obstacle = False
        current_time = pg.time.get_ticks()

        snake_head = snake.get_head()
        next_head = snake.get_next_head()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        # Check collisions
        out_of_bounds = (
            next_head[0] < 1 or
            next_head[0] >= (GRID_WIDTH - 1) or
            next_head[1] < (OFFSET // GRID_SIZE) or
            next_head[1] >= (GRID_HEIGHT - 1 - OFFSET // GRID_SIZE)
        )
        hits_wall = next_head in wall_positions
        bites_self = next_head in list(snake.body)[1:]

        if out_of_bounds or hits_wall or bites_self:
            is_obstacle = True
            if out_of_bounds or bites_self:
                pg.mixer.Sound("../sounds/GameOver.mp3").play()
                snake.reset()
                occupied = snake.get_body_positions()
                apple = Fruit(apple_image, occupied)
                occupied.update(apple.get_position())
            else:
                pg.mixer.Sound("../sounds/rock_break.mp3").play()
                score = max(0, score - 1)
        snake.move(is_obstacle)

        # Apple
        if apple.get_position() == snake_head:
            pg.mixer.Sound("../sounds/apple_bite.mp3").play()
            snake.grow_next_move = True
            occupied = snake.get_body_positions()
            apple = Fruit(apple_image, occupied)
            occupied.update(apple.get_position())
            score += 1

        if coin and coin.get_position() == snake_head:
            pg.mixer.Sound("../sounds/shimmer.mp3").play()
            coins += 1
            coin = None
            last_coin_time = current_time

        # Check apple and coin lifetime
        if coin is None and current_time - last_coin_time >= COIN_COOLDOWN:
            occupied = snake.get_body_positions()
            occupied.update(wall_positions)
            for fire in fires:
                occupied.add(fire.get_position())
            occupied.add(apple.get_position())

            coin = Coin(
                sheet=coin_sheet,
                frame_count=8,
                occupied_positions=occupied,
                row=0,
                frame_duration=20
            )
            last_coin_time = current_time

        if apple.update_lifetime(current_time) == 'expired':
            occupied = snake.get_body_positions()
            occupied.update(wall_positions)
            for fire in fires:
                occupied.add(fire.get_position())
            if coin:
                occupied.add(coin.get_position())
            apple = Fruit(apple_image, occupied)

        screen.fill(BOARD_BACKGROUND_COLOR)

        pg.draw.rect(screen, (0, 0, 0), pg.Rect(0, 0, SCREEN_WIDTH, OFFSET))
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        coins_text = font.render(f"Coins: {coins}", True, (255, 215, 0))
        screen.blit(score_text, (20, 10))
        screen.blit(coins_text, (20 + score_text.get_width() + 20, 10))

        draw_border(screen, bush_image)
        for wall in walls:
            wall.draw(screen)
        apple.draw(screen)
        snake.draw(screen)

        for fire in fires:
            fire.update()
            fire.draw(screen)

            if snake_head == fire.get_position():
                if coins > 0:
                    pg.mixer.Sound("../sounds/alarme.mp3").play()
                    coins -= 1
                else:
                    pg.mixer.Sound("../sounds/GameOver.mp3").play()
                    snake.reset()
                    occupied = snake.get_body_positions()
                    apple = Fruit(apple_image, occupied)
                    occupied.update(apple.get_position())

        if coin:
            if coin.update_lifetime(current_time) == 'expired':
                coin = None
            else:
                coin.update()
                coin.draw(screen)

        pg.display.update()


if __name__ == '__main__':
    main()
