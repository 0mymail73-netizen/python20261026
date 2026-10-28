import math
import random
import sys

import pygame


WIDTH = 900
HEIGHT = 650
FPS = 60

BACKGROUND = (16, 22, 38)
WHITE = (240, 244, 255)
MUTED = (155, 169, 195)
PADDLE_COLOR = (90, 205, 255)
BALL_COLOR = (255, 239, 145)
BRICK_COLORS = (
    (255, 105, 120),
    (255, 164, 92),
    (255, 218, 112),
    (112, 220, 160),
    (101, 178, 255),
)

PADDLE_WIDTH = 360
PADDLE_HEIGHT = 16
BALL_RADIUS = 9
BRICK_COLUMNS = 10
BRICK_ROWS = 5
BRICK_WIDTH = 78
BRICK_HEIGHT = 25
BRICK_GAP = 8
BRICK_TOP = 100
ITEM_SIZE = 18
ITEM_SPEED = 190
BULLET_SPEED = 520
BULLET_COOLDOWN = 250
BULLET_AMMO_PER_ITEM = 5
FEVER_DURATION = 10.0
FEVER_ITEM_THRESHOLD = 0.30
BONUS_ITEM_THRESHOLD = 0.50
RAINBOW_COLORS = (
    (255, 65, 75),
    (255, 145, 55),
    (255, 225, 65),
    (80, 225, 115),
    (65, 195, 255),
    (105, 105, 255),
    (200, 90, 255),
)


class BreakoutGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Breakout")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font(None, 64)
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 23)
        self.reset()

    def reset(self):
        self.paddle = pygame.Rect(
            (WIDTH - PADDLE_WIDTH) // 2,
            HEIGHT - 55,
            PADDLE_WIDTH,
            PADDLE_HEIGHT,
        )
        self.ball_x = float(self.paddle.centerx)
        self.ball_y = float(self.paddle.top - BALL_RADIUS - 1)
        self.ball_vx = 0.0
        self.ball_vy = 0.0
        self.ball_launched = False
        self.score = 0
        self.lives = 3
        self.bullet_ammo = 0
        self.next_bullet_time = 0
        self.items_collected = 0
        self.fever_remaining = 0.0
        self.fever_triggered = False
        self.bonus_unlocked = False
        self.confetti_spawn_timer = 0.0
        self.items = []
        self.bullets = []
        self.extra_balls = []
        self.confetti = []
        self.paused = False
        self.finished = False
        self.won = False
        self.bricks = []

        grid_width = BRICK_COLUMNS * BRICK_WIDTH + (BRICK_COLUMNS - 1) * BRICK_GAP
        left = (WIDTH - grid_width) // 2
        for row in range(BRICK_ROWS):
            for column in range(BRICK_COLUMNS):
                brick = pygame.Rect(
                    left + column * (BRICK_WIDTH + BRICK_GAP),
                    BRICK_TOP + row * (BRICK_HEIGHT + BRICK_GAP),
                    BRICK_WIDTH,
                    BRICK_HEIGHT,
                )
                self.bricks.append((brick, BRICK_COLORS[row]))

    def launch_ball(self):
        if not self.ball_launched and not self.finished:
            self.ball_launched = True
            self.ball_vx = random.choice((-240.0, 240.0))
            self.ball_vy = -360.0

    def move_paddle(self, direction, delta_time):
        self.paddle.x += round(direction * 520 * delta_time)
        self.paddle.left = max(0, min(self.paddle.left, WIDTH - self.paddle.width))

        if not self.ball_launched:
            self.ball_x = float(self.paddle.centerx)
            self.ball_y = float(self.paddle.top - BALL_RADIUS - 1)

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.finished = True
            self.won = False
            return

        self.ball_launched = False
        self.ball_vx = 0.0
        self.ball_vy = 0.0
        self.ball_x = float(self.paddle.centerx)
        self.ball_y = float(self.paddle.top - BALL_RADIUS - 1)

    def break_brick(self, brick, color):
        self.bricks.remove((brick, color))
        self.score += 10
        self.items.append(
            pygame.Rect(
                brick.centerx - ITEM_SIZE // 2,
                brick.centery - ITEM_SIZE // 2,
                ITEM_SIZE,
                ITEM_SIZE,
            )
        )

    def set_paddle_width(self, multiplier):
        center = self.paddle.centerx
        self.paddle.width = round(PADDLE_WIDTH * multiplier)
        self.paddle.centerx = center
        self.paddle.clamp_ip(self.screen.get_rect())

    def shoot_bullets(self):
        now = pygame.time.get_ticks()
        if self.finished or self.paused or self.bullet_ammo <= 0 or now < self.next_bullet_time:
            return

        self.bullet_ammo -= 1
        self.next_bullet_time = now + BULLET_COOLDOWN
        if self.bonus_unlocked:
            positions = (1 / 7, 2 / 7, 3 / 7, 4 / 7, 5 / 7, 6 / 7)
        elif self.fever_remaining > 0:
            positions = (0.2, 0.4, 0.6, 0.8)
        else:
            positions = (0.25, 0.75)
        for position in positions:
            x = self.paddle.left + round(self.paddle.width * position)
            self.bullets.append(pygame.Rect(x - 3, self.paddle.top - 14, 6, 14))

    def start_fever(self):
        self.fever_remaining = FEVER_DURATION
        self.set_paddle_width(1.6 if self.bonus_unlocked else 1.5)
        self.confetti = []
        self.confetti_spawn_timer = 0.0

    def unlock_bonus(self):
        self.bonus_unlocked = True
        self.set_paddle_width(1.6)
        for angle in (-0.38, 0.38):
            self.extra_balls.append(
                {
                    "x": self.ball_x,
                    "y": self.ball_y,
                    "vx": self.ball_vx + math.sin(angle) * 280,
                    "vy": self.ball_vy - 80,
                }
            )

    def update_fever(self, delta_time):
        if self.fever_remaining <= 0:
            return

        self.fever_remaining = max(0.0, self.fever_remaining - delta_time)
        if self.fever_remaining == 0:
            self.set_paddle_width(1.6 if self.bonus_unlocked else 1.0)
            self.confetti.clear()

    def update_confetti(self, delta_time):
        if self.fever_remaining > 0:
            self.confetti_spawn_timer -= delta_time
            while self.confetti_spawn_timer <= 0:
                for _ in range(8):
                    self.confetti.append(
                        {
                            "x": random.uniform(0, WIDTH),
                            "y": random.uniform(-80, -10),
                            "vx": random.uniform(-110, 110),
                            "vy": random.uniform(100, 360),
                            "color": random.choice(RAINBOW_COLORS),
                            "size": random.randint(4, 9),
                            "life": random.uniform(1.8, 3.2),
                        }
                    )
                self.confetti_spawn_timer += 0.15

        for piece in self.confetti[:]:
            piece["x"] += piece["vx"] * delta_time
            piece["y"] += piece["vy"] * delta_time
            piece["vy"] += 380 * delta_time
            piece["life"] -= delta_time
            if piece["life"] <= 0 or piece["y"] > HEIGHT:
                self.confetti.remove(piece)

        if self.fever_remaining <= 0:
            self.confetti.clear()

    def update_extra_balls(self, delta_time):
        for ball in self.extra_balls[:]:
            ball["x"] += ball["vx"] * delta_time
            ball["y"] += ball["vy"] * delta_time

            if ball["x"] - BALL_RADIUS <= 0:
                ball["x"] = float(BALL_RADIUS)
                ball["vx"] = abs(ball["vx"])
            elif ball["x"] + BALL_RADIUS >= WIDTH:
                ball["x"] = float(WIDTH - BALL_RADIUS)
                ball["vx"] = -abs(ball["vx"])

            if ball["y"] - BALL_RADIUS <= 0:
                ball["y"] = float(BALL_RADIUS)
                ball["vy"] = abs(ball["vy"])

            ball_rect = pygame.Rect(
                round(ball["x"] - BALL_RADIUS),
                round(ball["y"] - BALL_RADIUS),
                BALL_RADIUS * 2,
                BALL_RADIUS * 2,
            )
            if ball["vy"] > 0 and ball_rect.colliderect(self.paddle):
                ball["y"] = float(self.paddle.top - BALL_RADIUS)
                hit_position = (ball["x"] - self.paddle.centerx) / (self.paddle.width / 2)
                ball["vx"] = hit_position * 390
                ball["vy"] = -max(300.0, abs(ball["vy"]))

            for brick, color in self.bricks:
                if ball_rect.colliderect(brick):
                    ball["vy"] = -ball["vy"]
                    self.break_brick(brick, color)
                    break

            if ball["y"] - BALL_RADIUS > HEIGHT:
                self.extra_balls.remove(ball)

    def update_items(self, delta_time):
        for item in self.items[:]:
            item.y += round(ITEM_SPEED * delta_time)
            if item.colliderect(self.paddle):
                self.items.remove(item)
                self.items_collected += 1
                self.bullet_ammo += BULLET_AMMO_PER_ITEM
                fever_threshold = math.ceil(BRICK_ROWS * BRICK_COLUMNS * FEVER_ITEM_THRESHOLD)
                if not self.fever_triggered and self.items_collected >= fever_threshold:
                    self.fever_triggered = True
                    self.start_fever()
                bonus_threshold = math.ceil(BRICK_ROWS * BRICK_COLUMNS * BONUS_ITEM_THRESHOLD)
                if not self.bonus_unlocked and self.items_collected >= bonus_threshold:
                    self.unlock_bonus()
                    self.start_fever()
            elif item.top > HEIGHT:
                self.items.remove(item)

    def update_bullets(self, delta_time):
        for bullet in self.bullets[:]:
            bullet.y -= round(BULLET_SPEED * delta_time)
            if bullet.bottom < 0:
                self.bullets.remove(bullet)
                continue

            for brick, color in self.bricks:
                if bullet.colliderect(brick):
                    self.break_brick(brick, color)
                    self.bullets.remove(bullet)
                    break

    def update_ball(self, delta_time):
        if not self.ball_launched or self.paused or self.finished:
            return

        self.ball_x += self.ball_vx * delta_time
        self.ball_y += self.ball_vy * delta_time

        if self.ball_x - BALL_RADIUS <= 0:
            self.ball_x = float(BALL_RADIUS)
            self.ball_vx = abs(self.ball_vx)
        elif self.ball_x + BALL_RADIUS >= WIDTH:
            self.ball_x = float(WIDTH - BALL_RADIUS)
            self.ball_vx = -abs(self.ball_vx)

        if self.ball_y - BALL_RADIUS <= 0:
            self.ball_y = float(BALL_RADIUS)
            self.ball_vy = abs(self.ball_vy)

        ball_rect = pygame.Rect(
            round(self.ball_x - BALL_RADIUS),
            round(self.ball_y - BALL_RADIUS),
            BALL_RADIUS * 2,
            BALL_RADIUS * 2,
        )

        if self.ball_vy > 0 and ball_rect.colliderect(self.paddle):
            self.ball_y = float(self.paddle.top - BALL_RADIUS)
            hit_position = (self.ball_x - self.paddle.centerx) / (self.paddle.width / 2)
            self.ball_vx = hit_position * 390
            self.ball_vy = -max(300.0, abs(self.ball_vy))

        for brick, color in self.bricks:
            if not ball_rect.colliderect(brick):
                continue

            overlap_left = ball_rect.right - brick.left
            overlap_right = brick.right - ball_rect.left
            overlap_top = ball_rect.bottom - brick.top
            overlap_bottom = brick.bottom - ball_rect.top
            smallest_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if smallest_overlap in (overlap_left, overlap_right):
                self.ball_vx = -self.ball_vx
            else:
                self.ball_vy = -self.ball_vy

            self.break_brick(brick, color)
            break

        if not self.bricks:
            self.finished = True
            self.won = True
        elif self.ball_y - BALL_RADIUS > HEIGHT:
            self.lose_life()

    def draw_text(self, text, font, color, center):
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=center))

    def draw(self):
        self.screen.fill(BACKGROUND)
        self.draw_text(f"Score  {self.score}", self.font, WHITE, (105, 40))
        self.draw_text(f"Lives  {self.lives}", self.font, WHITE, (WIDTH - 105, 40))
        self.draw_text(f"Ammo  {self.bullet_ammo}", self.small_font, WHITE, (WIDTH // 2, 40))
        if self.fever_remaining > 0:
            self.draw_text(
                f"FEVER TIME  {self.fever_remaining:04.1f}s",
                self.font,
                (255, 215, 100),
                (WIDTH // 2, 75),
            )

        gauge = pygame.Rect(WIDTH - 28, 185, 14, 250)
        pygame.draw.rect(self.screen, (44, 54, 75), gauge, border_radius=5)
        fill_ratio = min(self.items_collected / (BRICK_ROWS * BRICK_COLUMNS), 1.0)
        fill_height = round(gauge.height * fill_ratio)
        if fill_height:
            for step in range(fill_height):
                progress = step / max(gauge.height - 1, 1)
                color_position = (1 - progress) * (len(RAINBOW_COLORS) - 1)
                color_index = int(color_position)
                next_color_index = min(color_index + 1, len(RAINBOW_COLORS) - 1)
                blend = color_position - color_index
                color = tuple(
                    round(
                        RAINBOW_COLORS[color_index][channel] * (1 - blend)
                        + RAINBOW_COLORS[next_color_index][channel] * blend
                    )
                    for channel in range(3)
                )
                y = gauge.bottom - step - 1
                pygame.draw.line(self.screen, color, (gauge.left + 1, y), (gauge.right - 1, y))
        for threshold, color in (
            (FEVER_ITEM_THRESHOLD, (255, 215, 100)),
            (BONUS_ITEM_THRESHOLD, (255, 255, 255)),
        ):
            threshold_y = gauge.bottom - round(gauge.height * threshold)
            pygame.draw.line(
                self.screen,
                color,
                (gauge.left - 3, threshold_y),
                (gauge.right + 3, threshold_y),
                2,
            )
        pygame.draw.rect(self.screen, WHITE, gauge, 1, border_radius=5)
        self.draw_text("ITEMS", self.small_font, WHITE, (WIDTH - 45, gauge.bottom + 22))
        self.draw_text(
            f"{self.items_collected}/{BRICK_ROWS * BRICK_COLUMNS}",
            self.small_font,
            WHITE,
            (WIDTH - 45, gauge.bottom + 44),
        )

        for brick, color in self.bricks:
            pygame.draw.rect(self.screen, color, brick, border_radius=6)
            pygame.draw.rect(self.screen, (255, 255, 255), brick, 1, border_radius=6)

        for item in self.items:
            pygame.draw.rect(self.screen, (110, 255, 160), item, border_radius=5)
            pygame.draw.rect(self.screen, WHITE, item, 1, border_radius=5)

        for bullet in self.bullets:
            pygame.draw.rect(self.screen, (255, 248, 150), bullet, border_radius=3)

        for ball in self.extra_balls:
            pygame.draw.circle(
                self.screen,
                (255, 105, 220),
                (round(ball["x"]), round(ball["y"])),
                BALL_RADIUS,
            )

        for piece in self.confetti:
            pygame.draw.rect(
                self.screen,
                piece["color"],
                pygame.Rect(round(piece["x"]), round(piece["y"]), piece["size"], piece["size"] // 2 + 2),
            )

        pygame.draw.rect(self.screen, PADDLE_COLOR, self.paddle, border_radius=8)
        if self.fever_remaining > 0:
            pygame.draw.rect(self.screen, (255, 190, 80), self.paddle, border_radius=8)
        pygame.draw.circle(
            self.screen,
            BALL_COLOR,
            (round(self.ball_x), round(self.ball_y)),
            BALL_RADIUS,
        )
        if self.fever_remaining > 0:
            self.draw_text("FEVER TIME!", self.title_font, (255, 215, 100), (WIDTH // 2, HEIGHT // 2))

        if self.finished:
            title = "You Win!" if self.won else "Game Over"
            self.draw_text(title, self.title_font, WHITE, (WIDTH // 2, HEIGHT // 2 - 25))
            self.draw_text("Press R to restart", self.font, MUTED, (WIDTH // 2, HEIGHT // 2 + 30))
        elif self.paused:
            self.draw_text("Paused", self.title_font, WHITE, (WIDTH // 2, HEIGHT // 2))
        elif not self.ball_launched:
            self.draw_text("Press Space to launch", self.font, WHITE, (WIDTH // 2, HEIGHT - 105))

        self.draw_text(
            "Move: Left/Right or A/D    Launch: Space    Shoot: F    Pause: P    Restart: R",
            self.small_font,
            MUTED,
            (WIDTH // 2, HEIGHT - 20),
        )
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            delta_time = min(self.clock.tick(FPS) / 1000, 0.03)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_p and not self.finished:
                        self.paused = not self.paused
                    elif event.key == pygame.K_SPACE:
                        self.launch_ball()
                    elif event.key == pygame.K_f:
                        self.shoot_bullets()

            keys = pygame.key.get_pressed()
            if not self.paused and not self.finished:
                direction = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(
                    keys[pygame.K_LEFT] or keys[pygame.K_a]
                )
                self.move_paddle(direction, delta_time)
                self.update_fever(delta_time)
                self.update_confetti(delta_time)
                self.update_items(delta_time)
                self.update_bullets(delta_time)
                self.update_extra_balls(delta_time)
                self.update_ball(delta_time)
                if not self.bricks:
                    self.finished = True
                    self.won = True

            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    BreakoutGame().run()
