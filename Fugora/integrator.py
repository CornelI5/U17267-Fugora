from .gravity import compute_nbody_gravity


class VelocityVerlet:
    def __init__(self, dt):
        self.dt = float(dt)

    def step(self, objects):
        half_dt = self.dt * 0.5

        for obj in objects:
            obj.position = obj.position + obj.velocity * self.dt + obj.acceleration * (half_dt * self.dt)

        compute_nbody_gravity(objects)

        for obj in objects:
            obj.velocity = obj.velocity + obj.acceleration * half_dt

        old_accels = [obj.acceleration for obj in objects]
        compute_nbody_gravity(objects)

        for i, obj in enumerate(objects):
            obj.velocity = obj.velocity + (old_accels[i] + obj.acceleration) * half_dt
