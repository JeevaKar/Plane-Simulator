from data import *
import pygame
import math

planes: list[Plane] = [
    Plane(
        id = 'AA743',
        heading = 45,
        plan = [Coord(0, 0)],
        speed = 5,
        pos = Coord(400,300)
    ),
    Plane(
        id = 'WND3997',
        heading = 180,
        plan = [Coord(50, 50)],
        speed = 5,
        pos = Coord(500, 50)
    ),
    Plane(
        id = 'YAYAYAYAYAY',
        heading = 270,
        plan = [Coord(0,0)],
        speed = 30,
        pos = Coord(1000, 50)
    )
]

pygame.init()
pygame.font.init()

font1 = pygame.font.SysFont('freesanbold.ttf', 15)

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((1500, 1000))
clock = pygame.time.Clock()
running = True
update = True

while running:
    planes = update(planes)
    screen.fill((0, 0, 0)) # Clear screen

    # Pygame event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Updating positions
    for plane in planes:
        color = GREEN
        for otherPlane in planes:
            if otherPlane == plane:
                continue
            elif checkCollision(plane, otherPlane):
                color = RED
                # update = False
        
        rad = math.radians(plane.heading)
        plane.pos.lat  += plane.speed * math.sin(rad)   # x
        plane.pos.long -= plane.speed * math.cos(rad)   # y
        
        label = font1.render(plane.id, True, color)
        labelRect = label.get_rect()
        labelRect.topleft = tuple(plane.pos.offset())
        
        screen.blit(label, labelRect)
        pygame.draw.circle(screen, color, tuple(plane.pos), 5)
    
    if update:
        pygame.display.flip() # Update display
    clock.tick(1) # Limit FPS