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

def setHeading(plane: Plane):
    xdiff = plane.plan[0].lat - plane.pos.lat
    ydiff = plane.plan[0].long - plane.pos.long
    zdiff = plane.plan[0].alt - plane.pos.alt
    dist = euclideanDist(xdiff, ydiff)
    framesLeft = max(dist / plane.speed, 1)
    
    plane.heading = math.degrees(math.atan2(xdiff, ydiff)) % 360
    plane.ascentRate = zdiff / framesLeft
    plane.ascentRate = max(-plane.maxRate, min(plane.maxRate, plane.ascentRate))

    return plane

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


def updatePos(planes: list[Plane]):
    remaining = []
    for plane in planes:
        if not plane.plan:
            remaining.append(plane)
            continue  # nothing to fly to, drop it

        if overlap(plane.pos.lat, plane.plan[0].lat, plane.pos.long, plane.plan[0].long, plane.pos.alt, plane.plan[0].alt, 1.5 * plane.speed):
            plane.plan.pop(0)
            if not plane.plan:
                remaining.append(plane)
                continue  # reached final waypoint, drop it

        plane = setHeading(plane)
        plane = avoidCollision(plane, planes)
        
        remaining.append(plane)
    return remaining

def futureCrash(plane1:Plane, plane2:Plane) -> int:
    for i in np.linspace(0, 300, 600, True):
        if checkCollision(plane1.futurePos(i), plane2.futurePos(i)):
            return i
    return 0