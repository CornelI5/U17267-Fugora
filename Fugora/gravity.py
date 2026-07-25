from .vector import Vec3

G = 6.67430e-11

def calculate_force(m1, m2, distance):
    if distance <= 0:
        return 0.0
    return G * m1 * m2 / (distance ** 2)

def calculate_acceleration(obj_a, obj_b):
    direction = obj_b.position.sub(obj_a.position)
    dist = direction.magnitude()
    
    if dist == 0:
        return Vec3(0, 0, 0)
    
    accel_mag = G * obj_b.mass / (dist ** 2)
    return direction.normalize().scale(accel_mag)
