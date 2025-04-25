from constants import *


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

    @staticmethod
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
