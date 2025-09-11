import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Easy Ping Pong ")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
OVERLAY = (0, 0, 0, 120)  # semi-transparent overlay

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PLAYER_SPEED = 7
AI_SPEED = 6

# Ball settings
BALL_SIZE = 20
BALL_SPEED_X = 6 * random.choice((1, -1))
BALL_SPEED_Y = 6 * random.choice((1, -1))

# Fonts
FONT = pygame.font.SysFont("Roboto", 36)
BIG_FONT = pygame.font.SysFont("Roboto", 72)

# Game objects
player = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ai = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Scores
player_score = 0
ai_score = 0

# Game state
game_state = "menu"  # "menu", "playing", "gameover", "paused"
winner = None


def draw_text(text, font, color, x, y, center=True):
    label = font.render(text, True, color)
    rect = label.get_rect(center=(x, y)) if center else label.get_rect(topleft=(x, y))
    WIN.blit(label, rect)
    return rect


def draw_playfield():
    WIN.fill(BLACK)

    # Draw paddles and ball
    pygame.draw.rect(WIN, WHITE, player)
    pygame.draw.rect(WIN, WHITE, ai)
    pygame.draw.ellipse(WIN, WHITE, ball)
    pygame.draw.aaline(WIN, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    # Draw scores
    player_text = FONT.render(str(player_score), True, WHITE)
    ai_text = FONT.render(str(ai_score), True, WHITE)
    WIN.blit(player_text, (WIDTH // 4, 20))
    WIN.blit(ai_text,(WIDTH * 2 // 4, 20))
    pygame.display.flip()


def handle_ball():
    global BALL_SPEED_X, BALL_SPEED_Y, player_score, ai_score, game_state, winner

    ball.x += BALL_SPEED_X
    ball.y += BALL_SPEED_Y

    # Collision with top/bottom
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        BALL_SPEED_Y *= -1

    # Collision with paddles
    if ball.colliderect(player) or ball.colliderect(ai):
        BALL_SPEED_X *= -1

    # Scoring
    if ball.left <= 0:
        ai_score += 1
        reset_ball()
    elif ball.right >= WIDTH:
        player_score += 1
        reset_ball()

    # Win condition
    if player_score >= 5:
        game_state = "gameover"
        winner = "Player"
    elif ai_score >= 5:
        game_state = "gameover"
        winner = "AI"


def reset_ball():
    global BALL_SPEED_X, BALL_SPEED_Y
    ball.center = (WIDTH // 2, HEIGHT // 2)
    BALL_SPEED_X = 6 * random.choice((1, -1))
    BALL_SPEED_Y = 6 * random.choice((1, -1))


def reset_game():
    global player_score, ai_score, game_state, winner
    player_score = 0
    ai_score = 0
    reset_ball()
    player.centery = HEIGHT // 2
    ai.centery = HEIGHT // 2
    game_state = "playing"
    winner = None


def handle_ai():
    if ai.centery < ball.centery:
        ai.y += AI_SPEED
    elif ai.centery > ball.centery:
        ai.y -= AI_SPEED

    if ai.top < 0:
        ai.top = 0
    if ai.bottom > HEIGHT:
        ai.bottom = HEIGHT


def menu_screen():
    WIN.fill(BLACK)
    draw_text("PING PONG", BIG_FONT, WHITE, WIDTH // 2, HEIGHT // 4)

    start_button = draw_text("Start", FONT, WHITE, WIDTH // 2, HEIGHT // 2)
    quit_button = draw_text("Quit", FONT, WHITE, WIDTH // 2, HEIGHT // 2 + 80)

    pygame.display.flip()
    return start_button, quit_button


def gameover_screen():
    WIN.fill(BLACK)
    draw_text(f"{winner} Wins!", BIG_FONT, WHITE, WIDTH // 2, HEIGHT // 4)

    restart_button = draw_text("RESTART", FONT, WHITE, WIDTH // 2, HEIGHT // 2)
    quit_button = draw_text("QUIT", FONT, WHITE, WIDTH // 2 , HEIGHT // 2 + 80)

    pygame.display.flip()
    return restart_button, quit_button


def pause_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY)
    WIN.blit(overlay, (0, 0))

    draw_text("PAUSED", BIG_FONT, WHITE, WIDTH // 2, HEIGHT // 3)
    resume_button = draw_text("Resume", FONT, WHITE, WIDTH // 2, HEIGHT // 2)
    quit_button = draw_text("Quit", FONT, WHITE, WIDTH // 2, HEIGHT // 2 + 80)

    pygame.display.flip()
    return resume_button, quit_button


def main():
    global game_state
    clock = pygame.time.Clock()

    while True:
        if game_state == "menu":
            start_button, quit_button = menu_screen()
        elif game_state == "gameover":
            restart_button, quit_button = gameover_screen()
        elif game_state == "paused":
            resume_button, quit_button = pause_overlay()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "menu":
                    if start_button.collidepoint(event.pos):
                        reset_game()
                    elif quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

                elif game_state == "gameover":
                    if restart_button.collidepoint(event.pos):
                        reset_game()
                    elif quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

                elif game_state == "paused":
                    if resume_button.collidepoint(event.pos):
                        game_state = "playing"
                    elif quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and game_state == "playing":
                    game_state = "paused"
                elif event.key == pygame.K_ESCAPE and game_state == "paused":
                    game_state = "playing"

        if game_state == "playing":
            # Player controls
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and player.top > 0:
                player.y -= PLAYER_SPEED
            if keys[pygame.K_s] and player.bottom < HEIGHT:
                player.y += PLAYER_SPEED

            handle_ball()
            handle_ai()
            draw_playfield()

        clock.tick(120)


if __name__ == "__main__":
    main()
