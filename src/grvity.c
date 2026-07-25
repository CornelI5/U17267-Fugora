#include "../fugora.h"

double gravity_force(double m1, double m2, double dist) {
    if (dist <= 0) return 0;
    return G * m1 * m2 / (dist * dist);
}

Vec3 gravity_accel(const Object *a, const Object *b) {
    Vec3 dir = v_sub(b->position, a->position);
    double dist = v_mag(dir);
    if (dist == 0) return (Vec3){0, 0, 0};
    double accel = G * b->mass / (dist * dist);
    return v_scale(v_norm(dir), accel);
}
