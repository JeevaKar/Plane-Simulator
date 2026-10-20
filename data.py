from dataclasses import dataclass
import math
import numpy as np

@dataclass
class Coord:
    lat: float
    long: float
    alt: float = 0

    def offset(self, offsetx = 5, offsety = 5):
        return Coord(self.lat + offsetx, self.long - offsety)

    def __iter__(self):
        yield self.lat
        yield self.long

@dataclass
class Plane:
    id: str
    heading: int # magnetic heading
    plan: list[Coord]
    speed: float # knots
    ascentRate: float
    pos: Coord

    maxRate:float = 20

    def futurePos(self, t: float) -> Coord:
        vx = self.speed * math.sin(math.radians(self.heading))
        vy = self.speed * math.cos(math.radians(self.heading))

        x = self.pos.lat + vx * t
        y = self.pos.long + vy * t
        z = self.pos.alt + self.ascentRate * t

        return Coord(x, y, z)

def overlap(x1, x2, y1, y2, z1, z2, margin = 15, zmargin = 50):
    xdiff = abs(x1 - x2)
    ydiff = abs(y1 - y2)
    zdiff = abs(z1 - z2)

    if xdiff < margin and ydiff < margin and zdiff < zmargin:
        return True
    return False

def checkCollision(pos1: Coord, pos2: Coord, margin = 50):
    return overlap(pos1.lat, pos2.lat, pos1.long, pos2.long, pos1.alt, pos2.alt, margin)

def euclideanDist(*args):
    return math.sqrt(sum(pow(a, 2) for a in args))

def avoidCollision(plane: Plane, planes: Plane):
    i = 0
    while i < len(planes):
        otherplane = planes[i]
        if otherplane == plane:
            i += 1
            continue
        while futureCrash(plane, otherplane):
            plane.heading += 5
            if futureCrash(plane, otherplane):
                plane.heading -= 10
            if futureCrash(plane, otherplane):
                plane.heading += 15
        i += 1
    return plane

def terrainCollision(pos_init, pos_final):
    return False

def angleBetween(pos: Coord, point1: Coord, point2: Coord) -> float:
    angle1 = math.atan2(point1.lat - pos.lat, point1.long - pos.long)
    angle2 = math.atan2(point2.lat - pos.lat, point2.long - pos.long)
    diff = abs(math.degrees(angle1 - angle2)) % 360
    return 360 - diff if diff > 180 else diff

def nextCheckpoint(plane: Plane) -> Coord | None:
    if not plane.plan:
        return None  # nothing to fly to

    final = plane.plan[-1]
    valid_checkpoints = []
    for checkpoint in plane.plan:
        valid_checkpoints.insert(0, checkpoint)
        if angleBetween(plane.pos, checkpoint, final) < 90:
            break

    for checkpoint in valid_checkpoints:
        if not terrainCollision(plane.pos, checkpoint):
            return checkpoint

    return plane.plan[0]

def setHeading(plane: Plane):
    nextCoord = nextCheckpoint(plane)

    xdiff = nextCoord.lat - plane.pos.lat
    ydiff = nextCoord.long - plane.pos.long
    zdiff = nextCoord.alt - plane.pos.alt
    dist = euclideanDist(xdiff, ydiff)
    framesLeft = max(dist / plane.speed, 1)
    
    plane.heading = math.degrees(math.atan2(xdiff, ydiff)) % 360
    plane.ascentRate = zdiff / framesLeft
    plane.ascentRate = max(-plane.maxRate, min(plane.maxRate, plane.ascentRate))

    return plane

def updateCheckpoints(plane: Plane):
    i = 0
    for checkpoint in plane.plan:
        if overlap(plane.pos.lat, checkpoint.lat, plane.pos.long, checkpoint.long, plane.pos.alt, checkpoint.alt, 1.5 * plane.speed):
            plane.plan = plane.plan[i+1:]
            return plane
    return plane

def updatePos(planes: list[Plane]):
    remaining = []
    for plane in planes:
        if not plane.plan:
            remaining.append(plane)
            continue  # nothing to fly to, drop it

        plane = updateCheckpoints(plane)
        if not plane.plan:
            remaining.append(plane)
            continue

        plane = setHeading(plane)
        plane = avoidCollision(plane, planes)
        
        remaining.append(plane)
    return remaining

def futureCrash(plane1:Plane, plane2:Plane) -> int:
    for i in np.linspace(0, 300, 600, True):
        if checkCollision(plane1.futurePos(i), plane2.futurePos(i)):
            return i
    return 0