from data import *
import pygame
import math

planes: list[Plane] = [
    Plane(
        id = 'UAL212',
        heading = 227,
        plan = [Coord(420, 800, 550), Coord(200, 650, 400), Coord(150, 500, 250), Coord(350, 500, 120), Coord(600, 500, 0)],
        speed = 20,
        ascentRate = 0,
        pos = Coord(600, 970, 700)
    ),
    Plane(
        id = 'SWA518',
        heading = 254,
        plan = [Coord(620, 900, 600), Coord(420, 800, 550), Coord(200, 650, 400), Coord(150, 500, 250), Coord(350, 500, 120), Coord(600, 500, 0)],
        speed = 20,
        ascentRate = 0,
        pos = Coord(900, 980, 700)
    ),
    Plane(
        id = 'DAL904',
        heading = 12,
        plan = [Coord(300, 250, 450), Coord(120, 400, 330), Coord(150, 500, 250), Coord(350, 500, 120), Coord(600, 500, 0)],
        speed = 20,
        ascentRate = 0,
        pos = Coord(250, 20, 600)
    ),
    Plane(
        id = 'JBU77',
        heading = 288,
        plan = [Coord(450, 100, 500), Coord(300, 250, 450), Coord(120, 400, 330), Coord(150, 500, 250), Coord(350, 500, 120), Coord(600, 500, 0)],
        speed = 20,
        ascentRate = 0,
        pos = Coord(700, 20, 600)
    ),
    Plane(
        id = 'AAL330',
        heading = 280,
        plan = [Coord(1000, 700, 600), Coord(500, 760, 500), Coord(150, 700, 380), Coord(150, 500, 250), Coord(350, 500, 120), Coord(600, 500, 0)],
        speed = 25,
        ascentRate = 0,
        pos = Coord(1450, 620, 650)
    ),
    Plane(
        id = 'FDX12',
        heading = 95,
        plan = [Coord(1150, 430, 250), Coord(1300, 330, 500), Coord(1480, 250, 800)],
        speed = 20,
        ascentRate = 0,
        pos = Coord(900, 450, 0)
    ),
    Plane(
        id = 'UAL48',
        heading = 81,
        plan = [Coord(1150, 600, 250), Coord(1300, 720, 500), Coord(1480, 850, 800)],
        speed = 20,
        ascentRate = 0,
        pos = Coord(900, 560, 0)
    ),
]

pygame.init()
pygame.font.init()

font1 = pygame.font.SysFont('freesanbold.ttf', 15)

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

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

    # Display future points
    for plane in planes:
        for point in plane.plan:
            pygame.draw.circle(screen, YELLOW, toPygame(tuple(point)), 2)

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
                color = BLUE
        
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