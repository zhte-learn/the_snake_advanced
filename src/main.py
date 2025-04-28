
import sys
import pygame as pg

from constants import *
from entity import Entity, AnimatedEntity
from sprite_sheet import SpriteSheet
from snake import Snake, SnakeSkin
from helpers import (
    draw_border,
    generate_walls_positions,
    get_random_pixel_position,
    generate_time_string,
)


def draw_game_over_screen(surface, font, score):
    overlay = pg.Surface(surface.get_size(), pg.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    text_over = font.render("GAME OVER", True, (255, 0, 0))
    text_score = font.render(f"Your score: {score}", True, (255, 255, 255))
    text_again = font.render("Press ENTER to play again", True, (255, 255, 255))
    text_quit = font.render("Press ESC to quit", True, (200, 200, 200))

    surface.blit(overlay, (0, 0))
    surface.blit(text_over, (surface.get_width() // 2 - text_over.get_width() // 2, 200))
    surface.blit(text_score, (surface.get_width() // 2 - text_score.get_width() // 2, 260))
    surface.blit(text_again, (surface.get_width() // 2 - text_again.get_width() // 2, 320))
    surface.blit(text_quit, (surface.get_width() // 2 - text_quit.get_width() // 2, 380))


def handle_keys(game_object, game_over):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if game_over:
                if event.key == pg.K_RETURN:
                    main()
                    return
                elif event.key == pg.K_ESCAPE:
                    pg.quit()
                    raise SystemExit
            else:
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


def draw_scoreboard(scoreboard_surface, font, score, coins, time_str):
    scoreboard_surface.fill((0, 0, 0))

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    coins_text = font.render(f"Coins: {coins}", True, (255, 255, 0))
    time_text = font.render(time_str, True, (180, 255, 180))

    scoreboard_surface.blit(score_text, (20, 35))
    scoreboard_surface.blit(coins_text, (320, 35))
    scoreboard_surface.blit(time_text, (scoreboard_surface.get_width() - 100, 35))


def main_menu():
    pg.init()
    screen = pg.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pg.display.set_caption("Snake Game - Menu")
    font = pg.font.Font("./fonts/PressStart2P-Regular.ttf", 16)

    menu_options = ["Start Game", "Level 1", "Level 2", "Quit"]
    selected = 0
    chosen_level = 1

    while True:
        screen.fill((0, 0, 0))
        for i, option in enumerate(menu_options):
            y_pos = 170 + i * 50
            if option.startswith("Level"):
                level_num = int(option.split()[-1])
                is_selected_level = (chosen_level == level_num)
                color = (0, 255, 0) if is_selected_level else (150, 150, 150)
            else:
                color = (255, 255, 255) if i == selected else (150, 150, 150)

            if i == selected:
                color = (255, 255, 0)

            label = font.render(option, True, color)
            label_rect = label.get_rect(center=(MENU_WIDTH // 2, y_pos))
            screen.blit(label, label_rect)
        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    selected = (selected - 1) % len(menu_options)
                elif event.key == pg.K_DOWN:
                    selected = (selected + 1) % len(menu_options)
                elif event.key == pg.K_RETURN:
                    option = menu_options[selected]
                    if option == "Start Game":
                        return chosen_level
                    elif option == "Quit":
                        pg.quit()
                        sys.exit()
                    elif option.startswith("Level"):
                        chosen_level = int(option.split()[-1])


def main(level=1):
    pg.display.quit()
    pg.display.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pg.init()
    start_game_time = pg.time.get_ticks()
    pg.mixer.init()
    pg.display.set_caption("Snake Game")
    pg.font.init()
    font = pg.font.Font("./fonts/PressStart2P-Regular.ttf", 16)
    clock = pg.time.Clock()
    game_over = False
    game_over_sound_played = False

    speed = 2 if level == 1 else 4
    number_of_fires = 5 if level == 1 else 8
    number_of_walls = 7 if level == 1 else 10

    occupied_positions = set()
    # Occupy positions for initial snake in the middle
    # And all cells to the right
    x, y = GRID_WIDTH // 2, GRID_HEIGHT // 2
    for x_occ in range(x - 2, GRID_WIDTH):
        occupied_positions.add((x_occ, y))

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

    scoreboard_surface = pg.Surface((SCREEN_WIDTH, SCOREBOARD_HEIGHT))
    game_surface = pg.Surface((SCREEN_WIDTH, (SCREEN_HEIGHT - SCOREBOARD_HEIGHT)))

    walls = generate_walls_positions(game_surface, occupied_positions, number_of_walls)

    fires = []
    for _ in range(number_of_fires):
        fire = AnimatedEntity(
            get_random_pixel_position(game_surface, occupied_positions),
            fire_sheet, 5, 40)
        fires.append(fire)

    apple = Entity(get_random_pixel_position(game_surface, occupied_positions), apple_image)

    coin = None
    last_coin_time = pg.time.get_ticks()

    snake = Snake(snake_skin, occupied_positions)

    while True:
        screen.fill((0, 0, 0))
        scoreboard_surface.fill((0, 70, 0))
        game_surface.fill(BOARD_BACKGROUND_COLOR)
        handle_keys(snake, game_over)

        is_obstacle = False
        snake_head = snake.get_head()
        next_head = snake.get_next_head()

        current_time = pg.time.get_ticks()
        apple_state = apple.update_lifetime(current_time)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

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
                if not game_over_sound_played:
                    pg.mixer.Sound("./sounds/GameOver.mp3").play()
                    game_over_sound_played = True
                game_over = True
            else:
                pg.mixer.Sound("./sounds/rock_break.mp3").play()
                score = max(0, score - 1)

        if not is_obstacle and not game_over:
            snake.move(is_obstacle)

        if apple.grid_position == snake_head:
            pg.mixer.Sound("./sounds/apple_bite.mp3").play()
            snake.grow_next_move = True
            occupied_positions.discard(apple.grid_position)
            apple = Entity(get_random_pixel_position(game_surface, occupied_positions), apple_image)
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
                    if not game_over_sound_played:
                        pg.mixer.Sound("./sounds/GameOver.mp3").play()
                        game_over_sound_played = True
                    game_over = True

        border_block = Entity((0, 0), bush_image)
        draw_border(game_surface, border_block, occupied_positions)

        for wall in walls:
            for position in wall:
                pixel_position = (position[0] * GRID_SIZE, position[1] * GRID_SIZE)
                wall_block = Entity(pixel_position, wall_image)
                wall_block.draw(game_surface)

        for fire in fires:
            fire.update()
            fire.draw(game_surface)

        if apple_state == 'expired':
            if apple.grid_position in occupied_positions:
                occupied_positions.discard(apple.grid_position)
            new_position = get_random_pixel_position(game_surface, occupied_positions)
            apple = Entity(new_position, apple_image)

        if apple.visible:
            apple.draw(game_surface)

        if coin is None and current_time - last_coin_time >= COIN_COOLDOWN:
            coin = AnimatedEntity(get_random_pixel_position(game_surface, occupied_positions),
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

        time_str = generate_time_string(current_time, start_game_time)
        draw_scoreboard(scoreboard_surface, font, score, coins, time_str)
        screen.blit(scoreboard_surface, (0, 0))
        screen.blit(game_surface, (0, SCOREBOARD_HEIGHT))

        if game_over:
            draw_game_over_screen(screen, font, score)

        pg.display.flip()
        clock.tick(speed)


if __name__ == '__main__':
    selected_level = main_menu()
    main(selected_level)
