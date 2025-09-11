import pygame
import random
import sys
import math

# ----------------------------
# Config
# ----------------------------
WIDTH, HEIGHT = 900, 600
GROUND_STEP = 6           # horizontal resolution of terrain
TERRAIN_MIN_Y = HEIGHT//3
TERRAIN_MAX_Y = HEIGHT - 120
NUM_COLLECTIBLES = 12     # spawn more than needed; collect 10 to win
TARGET_SCORE = 10
TIME_LIMIT = 120.0        # seconds (2 minutes)

PLAYER_W, PLAYER_H = 28, 36
PLAYER_SPEED = 5.0
JUMP_VELOCITY = -10.5
GRAVITY = 0.55

COLLECTIBLE_RADIUS = 8

FPS = 60

# ----------------------------
# Pygame init
# ----------------------------
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Collect on Random Terrain")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 28)
BIG_FONT = pygame.font.SysFont("Arial", 64)

# Colors
WHITE = (245, 245, 245)
BLACK = (15, 15, 15)
SKY = (80, 170, 255)
GROUND_COLOR = (40, 100, 40)
COLLECT_COLOR = (255, 215, 0)
PLAYER_COLOR = (200, 60, 60)
UI_BG = (20, 20, 30)

# ----------------------------
# Utility: terrain generation
# ----------------------------
def generate_terrain():
    """
    Create a heights list for x positions sampled every GROUND_STEP px.
    Use a random walk to make a natural-looking terrain, then smooth it.
    Return: list of (x, y) points suitable for polygon plotting and height lookup.
    """
    n_points = WIDTH // GROUND_STEP + 1
    heights = []
    y = random.randint(TERRAIN_MIN_Y, TERRAIN_MAX_Y)
    for i in range(n_points):
        delta = random.randint(-18, 18)
        y += delta
        y = max(TERRAIN_MIN_Y, min(TERRAIN_MAX_Y, y))
        heights.append(y)

    # simple smoothing
    for _ in range(2):
        heights = [heights[0]] + [(heights[i-1]+heights[i]+heights[i+1])//3 for i in range(1, n_points-1)] + [heights[-1]]
    # build points
    points = [(i * GROUND_STEP, heights[i]) for i in range(n_points)]
    return points

def terrain_height_at(points, x):
    """
    Given the terrain points (sampled), return the terrain y at an arbitrary x via linear interpolation.
    """
    if x <= 0:
        return points[0][1]
    if x >= WIDTH:
        return points[-1][1]
    idx = int(x // GROUND_STEP)
    x0, y0 = points[idx]
    x1, y1 = points[min(idx + 1, len(points)-1)]
    t = (x - x0) / max(1, x1 - x0)
    return y0 + (y1 - y0) * t

# ----------------------------
# Game objects
# ----------------------------
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(0, 0, PLAYER_W, PLAYER_H)
        self.rect.centerx = x
        self.rect.bottom = y
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False

    def update(self, keys, terrain_points):
        # horizontal movement
        self.vx = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = PLAYER_SPEED

        self.rect.x += int(self.vx)

        # gravity
        self.vy += GRAVITY
        self.rect.y += int(self.vy)

        # terrain collision: simple ground collision using terrain height at player's center x
        px = self.rect.centerx
        ground_y = terrain_height_at(terrain_points, px)

        if self.rect.bottom >= ground_y:
            # Land on ground
            self.rect.bottom = int(ground_y)
            self.vy = 0.0
            self.on_ground = True
        else:
            self.on_ground = False

        # Keep inside screen horizontally
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_VELOCITY
            self.on_ground = False

    def draw(self, surf):
        pygame.draw.rect(surf, PLAYER_COLOR, self.rect)

class Collectible:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.collected = False

    def draw(self, surf):
        if not self.collected:
            pygame.draw.circle(surf, COLLECT_COLOR, (int(self.pos.x), int(self.pos.y)), COLLECTIBLE_RADIUS)

# ----------------------------
# Game management
# ----------------------------
def spawn_collectibles(terrain_points, count=NUM_COLLECTIBLES):
    """
    Spawn collectibles at random x positions and at y positions above terrain.
    Ensure they are placed sufficiently above the ground so player can reach them by jumping.
    """
    picks = []
    tries = 0
    while len(picks) < count and tries < count * 8:
        tries += 1
        x = random.randint(30, WIDTH - 30)
        ground_y = terrain_height_at(terrain_points, x)
        # place collectible between (ground_y - 160) and (ground_y - 28)
        y = random.randint(max(30, int(ground_y - 160)), int(ground_y - 36))
        # avoid placing too close to other pickups
        ok = True
        for px, py in picks:
            if math.hypot(px - x, py - y) < 40:
                ok = False
                break
        if ok:
            picks.append((x, y))
    return [Collectible(x, y) for x, y in picks]

def draw_terrain(surf, points):
    poly = points[:]
    # extend polygon to bottom corners
    poly.append((WIDTH, HEIGHT))
    poly.append((0, HEIGHT))
    pygame.draw.polygon(surf, GROUND_COLOR, poly)

def draw_ui(surf, score, remaining_time):
    # top bar
    pygame.draw.rect(surf, UI_BG, (0, 0, WIDTH, 48))
    score_text = FONT.render(f"Score: {score}/{TARGET_SCORE}", True, WHITE)
    surf.blit(score_text, (12, 8))
    minutes = int(remaining_time) // 60
    seconds = int(remaining_time) % 60
    time_text = FONT.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
    surf.blit(time_text, (WIDTH - 160, 8))

# ----------------------------
# Screens: menu and gameover
# ----------------------------
def text_button(surf, text, font, x, y):
    label = font.render(text, True, WHITE)
    rect = label.get_rect(center=(x, y))
    surf.blit(label, rect)
    return rect

def menu_screen():
    WIN.fill(SKY)
    title_rect = text_button(WIN, "Collect Quest", BIG_FONT, WIDTH//2, HEIGHT//3)
    sub = FONT.render("Collect 10 golden circles before the time runs out. Move: A/D or ←/→, Jump: Space", True, WHITE)
    WIN.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//3 + 70)))
    start_rect = text_button(WIN, "Start", FONT, WIDTH//2, HEIGHT//2 + 20)
    quit_rect = text_button(WIN, "Quit", FONT, WIDTH//2, HEIGHT//2 + 80)
    pygame.display.flip()
    return start_rect, quit_rect

def gameover_screen(win_flag):
    WIN.fill(SKY)
    if win_flag:
        text = "You Win!"
        sub = "Nice! You collected enough circles."
    else:
        text = "Time Up"
        sub = "You ran out of time."
    text_button(WIN, text, BIG_FONT, WIDTH//2, HEIGHT//3)
    WIN.blit(FONT.render(sub, True, WHITE), FONT.render(sub, True, WHITE).get_rect(center=(WIDTH//2, HEIGHT//3 + 60)))
    restart_rect = text_button(WIN, "Restart", FONT, WIDTH//2, HEIGHT//2 + 20)
    quit_rect = text_button(WIN, "Quit", FONT, WIDTH//2, HEIGHT//2 + 80)
    pygame.display.flip()
    return restart_rect, quit_rect

# ----------------------------
# Main game loop
# ----------------------------
def run_game():
    # initial state
    game_state = "menu"   # "menu", "playing", "gameover"
    terrain_points = generate_terrain()
    player = Player(WIDTH//6, terrain_height_at(terrain_points, WIDTH//6))
    collectibles = spawn_collectibles(terrain_points)
    score = 0
    start_time = None
    remaining_time = TIME_LIMIT
    winner_flag = False

    start_btn = quit_btn = None
    restart_btn = quit_btn2 = None

    while True:
        dt = CLOCK.tick(FPS) / 1000.0  # seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_btn and start_btn.collidepoint(event.pos):
                    # start the game
                    terrain_points = generate_terrain()
                    player = Player(WIDTH//6, terrain_height_at(terrain_points, WIDTH//6))
                    collectibles = spawn_collectibles(terrain_points)
                    score = 0
                    remaining_time = TIME_LIMIT
                    start_time = pygame.time.get_ticks() / 1000.0
                    game_state = "playing"
                if quit_btn and quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

            if game_state == "gameover" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_btn and restart_btn.collidepoint(event.pos):
                    # restart new run
                    terrain_points = generate_terrain()
                    player = Player(WIDTH//6, terrain_height_at(terrain_points, WIDTH//6))
                    collectibles = spawn_collectibles(terrain_points)
                    score = 0
                    remaining_time = TIME_LIMIT
                    start_time = pygame.time.get_ticks() / 1000.0
                    game_state = "playing"
                if quit_btn2 and quit_btn2.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

            if game_state == "playing" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP:
                    player.jump()

        # ---------- Screen updates ----------
        if game_state == "menu":
            start_btn, quit_btn = menu_screen()

        elif game_state == "playing":
            # update timer
            if start_time is None:
                start_time = pygame.time.get_ticks() / 1000.0
            elapsed = (pygame.time.get_ticks() / 1000.0) - start_time
            remaining_time = max(0.0, TIME_LIMIT - elapsed)

            # input keys
            keys = pygame.key.get_pressed()
            player.update(keys, terrain_points)

            # check collectibles collisions
            for c in collectibles:
                if not c.collected:
                    dist = math.hypot(player.rect.centerx - c.pos.x, player.rect.centery - c.pos.y)
                    if dist <= COLLECTIBLE_RADIUS + max(player.rect.width, player.rect.height) * 0.45:
                        c.collected = True
                        score += 1

            # check win
            if score >= TARGET_SCORE:
                game_state = "gameover"
                winner_flag = True

            # check time up
            if remaining_time <= 0.0:
                game_state = "gameover"
                winner_flag = False

            # draw world
            WIN.fill(SKY)
            draw_terrain(WIN, terrain_points)

            # draw collectibles
            for c in collectibles:
                c.draw(WIN)

            # draw player on top
            player.draw(WIN)

            # draw UI
            draw_ui(WIN, score, remaining_time)

            pygame.display.flip()

        elif game_state == "gameover":
            restart_btn, quit_btn2 = gameover_screen(winner_flag)

        CLOCK.tick(FPS)

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    run_game()
