from dataclasses import dataclass
import math

@dataclass
class Coord:
    lat: float
    long: float

    def offset(self, offset = 5):
        return Coord(self.lat + offset, self.long + offset)

    def __iter__(self):
        yield self.lat
        yield self.long

@dataclass
class Plane:
    id: str
    heading: int # magnetic heading
    plan: list[Coord]
    speed: float # knots
    pos: Coord

def overlap(x1, x2, y1, y2, margin = 15):
    xdiff = abs(x1 - x2)
    ydiff = abs(y1 - y2)

    if xdiff < margin and ydiff < margin:
        return True
    return False

def checkCollision(plane1: Plane, plane2: Plane, margin = 15):
    return overlap(plane1.pos.lat, plane2.pos.lat, plane1.pos.long, plane2.pos.long, margin)

def updateFunc(planes: list[Plane]):
    remaining = []
    for plane in planes:
        if not plane.plan:
            continue  # nothing to fly to, drop it

        if overlap(plane.pos.lat, plane.plan[0].lat, plane.pos.long, plane.plan[0].long, 1.5 * plane.speed):
            plane.plan.pop(0)
            if not plane.plan:
                continue  # reached final waypoint, drop it

        xdiff = plane.plan[0].lat - plane.pos.lat
        ydiff = plane.plan[0].long - plane.pos.long
        plane.heading = math.degrees(math.atan2(xdiff, -ydiff)) % 360
        remaining.append(plane)
    return remaining