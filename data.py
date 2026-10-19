from dataclasses import dataclass

@dataclass
class Coord:
    lat: float
    long: float

@dataclass
class Plane:
    heading: int # magnetic heading
    plan: list[Coord]
    speed: float # knots