from dataclasses import dataclass
import math
import numpy as np

@dataclass
class Coord:
    lat: float
    long: float
    alt: float = 0
    skippable: bool = False

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
    turnRate: float = 30          # degrees turned per frame while circling

    def futurePos(self, t: float) -> Coord:
        vx = self.speed * math.sin(math.radians(self.heading))
        vy = self.speed * math.cos(math.radians(self.heading))

        x = self.pos.lat + vx * t
        y = self.pos.long + vy * t
        z = self.pos.alt + self.ascentRate * t

        return Coord(x, y, z)

@dataclass
class Runway:
    id: str
    heading: int # magnetic heading
    landingRoute: list[Coord]
    departureRoute: list[Coord]

def goAround(plane: Plane, zmargin=50) -> bool:
    """Circle a checkpoint that was reached too high. Returns True while looping."""
    target = plane.plan[0]
    tooHigh = plane.pos.alt - target.alt > zmargin
    near = euclideanDist(target.lat - plane.pos.lat, target.long - plane.pos.long) < 1.5 * plane.speed

    if near and tooHigh:
        zdiff = plane.pos.alt - target.alt
        zdiff /= 2
        distance = zdiff / (plane.maxRate * 0.75)


        newx = plane.pos.lat + distance * math.sin(math.degrees(plane.heading))
        newy = plane.pos.long + distance * math.cos(math.degrees(plane.heading))
        plane.plan.insert(0, Coord(newx, newy, zdiff, True))
        print(f'{plane.id} went around')

    return plane

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

def avoidCollision(plane: Plane, planes: list[Plane], maxTurn=90, step=5):
    others = [p for p in planes if p is not plane]

    def clear():
        return all(futureCrash(plane, o) is None for o in others)

    if clear():
        return plane

    base = plane.heading
    for turn in range(step, maxTurn + 1, step):
        for sign in (1, -1):
            plane.heading = (base + sign * turn) % 360
            if clear():
                return plane

    plane.heading = base  # no safe turn found
    return plane

def terrainCollision(pos_init, pos_final):
    return False

def angleBetween(pos: Coord, point1: Coord, point2: Coord) -> float:
    angle1 = math.atan2(point1.lat - pos.lat, point1.long - pos.long)
    angle2 = math.atan2(point2.lat - pos.lat, point2.long - pos.long)
    diff = abs(math.degrees(angle1 - angle2)) % 360
    return 360 - diff if diff > 180 else diff

def nextCheckpoint(plane: Plane) -> Coord | None:
    plan = plane.plan
    if not plan:
        return None  # nothing to fly to

    final = plan[-1]

    # Furthest waypoint we're allowed to skip to: the first one that points
    # within 90° of the direction to the final waypoint. The last waypoint
    # always qualifies, so this never runs off the end.
    j = next((i for i, c in enumerate(plan)
          if not c.skippable or angleBetween(plane.pos, c, final) < 90),
         len(plan) - 1)

    # Prefer the furthest-ahead waypoint with a clear path, falling back toward plan[0]
    for i in range(j, -1, -1):
        if not terrainCollision(plane.pos, plan[i]):
            del plan[:i]       # commit: skipped waypoints are gone for good
            return plan[0]

    return plan[0]             # everything is blocked, skip nothing

def setHeading(plane: Plane):
    nextCoord = nextCheckpoint(plane)

    xdiff = nextCoord.lat - plane.pos.lat
    ydiff = nextCoord.long - plane.pos.long
    zdiff = nextCoord.alt - plane.pos.alt
    dist = euclideanDist(xdiff, ydiff)
    framesLeft = max(dist / plane.speed, 1)

    desired = math.degrees(math.atan2(xdiff, ydiff)) % 360

    # shortest signed turn from the current heading to the desired one, in -180..180
    diff = (desired - plane.heading + 180) % 360 - 180

    # limit how far it can turn this frame
    diff = max(-plane.turnRate, min(plane.turnRate, diff))

    plane.heading = (plane.heading + diff) % 360
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
        if plane.plan:
            plane = updateCheckpoints(plane)

        if not plane.plan:
            # out of waypoints: keep descending straight ahead until on the ground
            if plane.pos.alt <= 0:
                continue                      # landed, remove it
            plane.ascentRate = -plane.maxRate
            remaining.append(plane)
            continue

        plane = goAround(plane)
        plane = setHeading(plane)
        plane = avoidCollision(plane, planes)

        remaining.append(plane)
    return remaining

def futureCrash(plane1: Plane, plane2: Plane, horizon=300, step=0.5):
    for t in np.arange(0, horizon, step):
        if checkCollision(plane1.futurePos(t), plane2.futurePos(t)):
            return t
    return None