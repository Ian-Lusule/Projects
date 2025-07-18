import pygame

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simple Platformer")

player_x = 50
player_y = 500
player_width = 40
player_height = 60
player_vel_y = 0
gravity = 0.5
jump_height = -10

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and player_y == 500:
                player_vel_y = jump_height

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= 5
    if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
        player_x += 5

    player_vel_y += gravity
    player_y += player_vel_y
    if player_y > 500:
        player_y = 500
        player_vel_y = 0

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 0, 0), (player_x, player_y, player_width, player_height))
    pygame.display.update()

pygame.quit()
