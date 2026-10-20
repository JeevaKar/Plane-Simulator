from data import *
import pygame
import math

planes: list[Plane] = [
    Plane(
        id = 'EAST',
        heading = 90,
        plan = [Coord(1400, 500, 200)],
        speed = 20,
        ascentRate = 0,
        pos = Coord(500, 500, 200)
    ),
    Plane(
        id = 'WEST',
        heading = 270,
        plan = [Coord(100, 500, 200)],
        speed = 20,
        ascentRate = 0,
        pos = Coord(1100, 500, 200)
    )
]

pygame.init()
pygame.font.init()

font1 = pygame.font.SysFont('freesanbold.ttf', 15)

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (0, 0, 255)

SCREEN_WIDTH = 1500
SCREEN_LENGTH = 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_LENGTH))
clock = pygame.time.Clock()
running = True
update = True

def toPygame(coords, height = SCREEN_LENGTH):
    return (coords[0], height - coords[1])

while running:
    planes = updatePos(planes)
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
            elif checkCollision(plane.pos, otherPlane.pos):
                color = RED
                # update = False
            elif color != RED and futureCrash(plane, otherPlane):
                color = ORANGE
        
        rad = math.radians(plane.heading)
        plane.pos.lat  += plane.speed * math.sin(rad)   # x
        plane.pos.long += plane.speed * math.cos(rad)   # y
        plane.pos.alt += plane.ascentRate
        
        label = font1.render(plane.id, True, color)
        labelRect = label.get_rect()
        labelRect.topleft = toPygame(tuple(plane.pos.offset()))

        altLabel = font1.render(str(plane.pos.alt), True, color)
        altRect = altLabel.get_rect()
        altRect.topleft = toPygame(tuple(plane.pos.offset(offsety=15)))
        
        screen.blit(label, labelRect)
        screen.blit(altLabel, altRect)
        pygame.draw.circle(screen, color, toPygame(tuple(plane.pos)), 5)
    
    if update:
        pygame.display.flip() # Update display
    clock.tick(1) # Limit FPS