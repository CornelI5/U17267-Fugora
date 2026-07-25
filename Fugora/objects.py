from .vector import Vec3


class CelestialObject:
    __slots__ = (
        "id", "name", "mass", "position", "velocity",
        "acceleration", "tracked", "radius", "color",
    )

    def __init__(self, obj_id, name, mass, position, velocity,
                 radius=0.0, color="white", tracked=True):
        self.id = obj_id
        self.name = name
        self.mass = float(mass)
        self.position = position if isinstance(position, Vec3) else Vec3(*position)
        self.velocity = velocity if isinstance(velocity, Vec3) else Vec3(*velocity)
        self.acceleration = Vec3(0, 0, 0)
        self.tracked = tracked
        self.radius = float(radius)
        self.color = color

    def kinetic_energy(self):
        return 0.5 * self.mass * self.velocity.magnitude_sq()

    def speed(self):
        return self.velocity.magnitude()

    def copy_state(self):
        return {
            "id": self.id,
            "name": self.name,
            "mass": self.mass,
            "position": self.position.copy(),
            "velocity": self.velocity.copy(),
            "speed": self.speed(),
        }


class AnomalyRecord:
    __slots__ = ("object_id", "deviation", "timestamp", "expected", "actual")

    def __init__(self, object_id, deviation, timestamp, expected, actual):
        self.object_id = object_id
        self.deviation = deviation
        self.timestamp = timestamp
        self.expected = expected
        self.actual = actual

    def __repr__(self):
        return (
            f"Anomaly({self.object_id}, dev={self.deviation:.6f}, "
            f"t={self.timestamp:.0f})"
        )
