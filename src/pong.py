# Imports
from random import choice
import pygame
import os

# Pygame inits
pygame.mixer.init()
pygame.font.init()

# Constants + window
WIDTH, HEIGHT = 900, 500
PADDLE_WIDTH, PADDLE_HEIGHT = 8, 80
SPLITTER_RECT_WIDTH, SPLITTER_RECT_HEIGHT = 5, 10
FPS_CAP = 60
BALL_VELOCITY_X = 6
BALL_VELOCITY_Y = 6
PADDLE_VELOCITY = 8
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

# Non-constant but needs caution changing
HAS_SOUND = True

# Window setting
pygame.display.set_caption("Pong (by R1DF)")
pygame.display.set_icon(pygame.image.load(os.path.join("assets", "icon", "icon_32x32.bmp")))

# Colours
BLACK = (0, 0, 0)
GRAY = (125.5, 125.5, 125.5)
WHITE = (255, 255, 255)

# Text + Mixer
SCORES_DRAWER = pygame.font.SysFont("fixedsys", (HEIGHT // 10) + 20)
MIXERS = {
    "ping_left": pygame.mixer.Sound(os.path.join("assets", "sound", "ping_left.mp3")),
    "ping_right": pygame.mixer.Sound(os.path.join("assets", "sound", "ping_right.mp3")),
    "scored": pygame.mixer.Sound(os.path.join("assets", "sound", "scored.mp3"))
}

# User events
E_RESET = pygame.USEREVENT + 1
P1_SCORED = pygame.USEREVENT + 2
P2_SCORED = pygame.USEREVENT + 3
E_RESTART = pygame.USEREVENT + 4

# Global game variables
points_1, points_2 = 0, 0

# Handling
def handle_keys(keys_pressed, paddle_1, paddle_2):
    if keys_pressed[pygame.K_w] and paddle_1.y - PADDLE_VELOCITY > 0:
        paddle_1.y -= PADDLE_VELOCITY
    if keys_pressed[pygame.K_s] and paddle_1.y + PADDLE_HEIGHT + PADDLE_VELOCITY < HEIGHT:
        paddle_1.y += PADDLE_VELOCITY
    if keys_pressed[pygame.K_UP] and paddle_2.y - PADDLE_VELOCITY > 0:
        paddle_2.y -= PADDLE_VELOCITY
    if keys_pressed[pygame.K_DOWN] and paddle_2.y + PADDLE_HEIGHT + PADDLE_VELOCITY < HEIGHT:
        paddle_2.y += PADDLE_VELOCITY

def handle_ball(ball, direction_multiplier, vertical_multiplier):
    ball.x += BALL_VELOCITY_X * direction_multiplier
    ball.y += BALL_VELOCITY_Y * vertical_multiplier

def handle_sound(has_sound, which):
    if has_sound:
        MIXERS[which].play()

def check_direction(ball, paddle_1, paddle_2, direction_multiplier, vertical_multiplier, has_sound):
    global BALL_VELOCITY_Y  # Gets updated here
    new_direction_multiplier, new_vertical_multiplier = direction_multiplier, vertical_multiplier
    
    # Checking X direction
    match direction_multiplier:
        case 1:
            if ball.x + ball.width + BALL_VELOCITY_X > WIDTH:
                handle_sound(has_sound, "scored")
                pygame.event.post(pygame.event.Event(P1_SCORED))
                pygame.event.post(pygame.event.Event(E_RESET))
                new_direction_multiplier = choice([-1, 1])

            elif paddle_2.colliderect(ball):
                handle_sound(has_sound, "ping_right")
                BALL_VELOCITY_Y = BALL_VELOCITY_X + abs(ball.y + (ball.height // 2) - (paddle_2.y + (paddle_2.height // 2))) // 8
                new_direction_multiplier = -1

        case -1:
            if ball.x - BALL_VELOCITY_X < 0:
                handle_sound(has_sound, "scored")
                pygame.event.post(pygame.event.Event(P2_SCORED))
                pygame.event.post(pygame.event.Event(E_RESET))
                new_direction_multiplier = choice([-1, 1])

            elif paddle_1.colliderect(ball):
                handle_sound(has_sound, "ping_left")
                BALL_VELOCITY_Y = BALL_VELOCITY_X + abs(ball.y + (ball.height // 2) - (paddle_1.y + (paddle_1.height // 2))) // 8
                new_direction_multiplier = 1
    
    # Checking Y direction
    match vertical_multiplier:
        case 1:
            if ball.y + BALL_VELOCITY_Y > HEIGHT:
                handle_sound(has_sound, "ping_left")
                new_vertical_multiplier = -1
        case -1:
            if ball.y < 0:
                new_vertical_multiplier = 1
                handle_sound(has_sound, "ping_right")
    return new_direction_multiplier, new_vertical_multiplier

# Drawing functions
def draw_scores():
    left_score_text = SCORES_DRAWER.render(str(points_1), 1, WHITE)
    right_score_text = SCORES_DRAWER.render(str(points_2), 1, WHITE)
    WINDOW.blit(left_score_text, ((WIDTH // 4) - left_score_text.get_width(), 60))
    WINDOW.blit(right_score_text, ((3 * WIDTH // 4) - right_score_text.get_width(), 60))
    # No update needed since there's another draw function called right after

def draw(WINDOW, ball, paddle_1, paddle_2):
    splitter_rect_amount = HEIGHT // (SPLITTER_RECT_HEIGHT + 10)  # Amount of splitter Rect objects shown
    empty_space_height = (HEIGHT - (SPLITTER_RECT_HEIGHT * splitter_rect_amount)) // splitter_rect_amount  # Separator height

    # Splitter
    for i in range(splitter_rect_amount):
        pygame.draw.rect(WINDOW, GRAY,
            pygame.Rect(
                WIDTH // 2 - (SPLITTER_RECT_WIDTH // 2),
                (i * SPLITTER_RECT_HEIGHT) + ((i + 1) * empty_space_height),
                SPLITTER_RECT_WIDTH,
                SPLITTER_RECT_HEIGHT
            )
        )

    # Paddles
    pygame.draw.rect(WINDOW, WHITE, paddle_1)
    pygame.draw.rect(WINDOW, WHITE, paddle_2)
    pygame.draw.rect(WINDOW, WHITE, ball)

    # Update
    pygame.display.update()

# Main
def main():
    global points_1, points_2, BALL_VELOCITY_X, BALL_VELOCITY_Y, HAS_SOUND
    BALL_VELOCITY_X = 6
    BALL_VELOCITY_Y = 6
    clock = pygame.time.Clock()
    running = True
    starting_position = True
    is_listening = True
    is_listening_space = True
    ball = pygame.Rect((WIDTH // 2) - 5, (HEIGHT // 2) - 5, 10, 10)
    vertical_multiplier = choice([-1, 1])
    direction_multiplier = choice([-1, 1])
    paddle_1 = pygame.Rect(15, (HEIGHT // 2) - (PADDLE_HEIGHT // 2), PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_2 = pygame.Rect(WIDTH - PADDLE_WIDTH - 15, (HEIGHT // 2) - (PADDLE_HEIGHT // 2), PADDLE_WIDTH, PADDLE_HEIGHT)
    while running:
        clock.tick(FPS_CAP)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LCTRL:
                HAS_SOUND = not HAS_SOUND  # Toggle sound
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and starting_position and is_listening_space:
                starting_position = False
                is_listening = True
                is_listening_space = False

            if event.type == P1_SCORED:
                points_1 += 1
            
            if event.type == P2_SCORED:
                points_2 += 1
            
            if event.type == E_RESTART:
                running = False

            if event.type == E_RESET:
                is_listening_space = False
                pygame.time.delay(2000)
                starting_position = True
                pygame.event.post(pygame.event.Event(E_RESTART))
        
        if not starting_position:
            direction_multiplier, vertical_multiplier = check_direction(ball, paddle_1, paddle_2, direction_multiplier, vertical_multiplier, HAS_SOUND)
            handle_ball(ball, direction_multiplier, vertical_multiplier)
        
        if is_listening:
            handle_keys(pygame.key.get_pressed(), paddle_1, paddle_2)

        WINDOW.fill(BLACK) # Filling must always come before
        draw_scores()
        draw(WINDOW, ball, paddle_1, paddle_2)
    main()

if __name__ == "__main__":
    try:
        main()
    except pygame.error:
        pass

