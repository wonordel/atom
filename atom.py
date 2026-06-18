from settings import ATOM_NEUTRAL

class Atom:
    __slots__ = ('x', 'y', 'vx', 'vy', 'mass', 'radius', 'charge')
    def __init__(self, x, y, mass=1.0, charge=ATOM_NEUTRAL):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.mass = mass
        self.radius = 5
        self.charge = charge
