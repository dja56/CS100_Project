try:
    import pygame
except ImportError as exc:
    raise SystemExit("Pygame is required. Install it with: python -m pip install pygame") from exc


import sys
import gui_data as gd


darkGreen = (0, 100, 0)
forestGreen = (34, 139, 34)


pygame.init()

WIDTH, HEIGHT = 1280, 720

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

pygame.display.set_caption("Blackjack Trainer")

running = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    twelvePercent = WIDTH //8

    size = min(WIDTH, HEIGHT) //10


    screen.fill((darkGreen))

    pygame.draw.rect(screen, forestGreen, (twelvePercent, twelvePercent, size, size))
    
    pygame.draw.circle(screen, forestGreen, (WIDTH // 5, HEIGHT // 2), 275)
    pygame.draw.circle(screen, forestGreen, (int(WIDTH // (1.5 )), int(HEIGHT // 1.15)), 150)
    pygame.draw.circle(screen, forestGreen, (int(WIDTH // 1.15), int(HEIGHT // 10)), 150)

    pygame.display.flip()



pygame.quit()
sys.exit()