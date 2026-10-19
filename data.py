from dataclasses import dataclass

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

def checkCollision(plane1: Plane, plane2: Plane, margin = 15):
    xdiff = abs(plane1.pos.lat - plane2.pos.lat)
    ydiff = abs(plane1.pos.long - plane2.pos.long)

    if xdiff < margin and ydiff < margin:
        return True
    return False

def update(planes: list[Plane]):
    return planes