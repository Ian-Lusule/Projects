import pygame
import sys

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Simple Pong")

white = (255, 255, 255)
black = (0, 0, 0)

paddle_width, paddle_height = 10, 100
paddle_speed = 5

paddle1_y = height // 2 - paddle_height // 2
paddle2_y = height // 2 - paddle_height // 2

ball_x = width // 2
ball_y = height // 2
ball_radius = 10
ball_speed_x = 3
ball_speed_y = 3

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and paddle1_y > 0:
        paddle1_y -= paddle_speed
    if keys[pygame.K_s] and paddle1_y < height - paddle_height:
        paddle1_y += paddle_speed
    if keys[pygame.K_UP] and paddle2_y > 0:
        paddle2_y -= paddle_speed
    if keys[pygame.K_DOWN] and paddle2_y < height - paddle_height:
        paddle2_y += paddle_speed

    ball_x += ball_speed_x
    ball_y += ball_speed_y

    if ball_y <= 0 or ball_y >= height - ball_radius:
        ball_speed_y *= -1

    if ball_x <= 10 and paddle1_y <= ball_y <= paddle1_y + paddle_height:
        ball_speed_x *= -1
    elif ball_x <= 0:
        ball_x = width // 2
        ball_y = height // 2

    if ball_x >= width - 10 - ball_radius and paddle2_y <= ball_y <= paddle2_y + paddle_height:
        ball_speed_x *= -1
    elif ball_x >= width:
        ball_x = width // 2
        ball_y = height // 2


    screen.fill(black)
    pygame.draw.rect(screen, white, (10, paddle1_y, paddle_width, paddle_height))
    pygame.draw.rect(screen, white, (width - 20, paddle2_y, paddle_width, paddle_height))
    pygame.draw.circle(screen, white, (ball_x, ball_y), ball_radius)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
