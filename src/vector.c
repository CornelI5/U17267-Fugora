#include "../fugora.h"

Vec3 v_add(Vec3 a, Vec3 b) {
    return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z};
}

Vec3 v_sub(Vec3 a, Vec3 b) {
    return (Vec3){a.x - b.x, a.y - b.y, a.z - b.z};
}

Vec3 v_scale(Vec3 v, double s) {
    return (Vec3){v.x * s, v.y * s, v.z * s};
}

double v_mag(Vec3 v) {
    return sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}

double v_dist(Vec3 a, Vec3 b) {
    return v_mag(v_sub(a, b));
}

Vec3 v_norm(Vec3 v) {
    double m = v_mag(v);
    if (m == 0) return (Vec3){0, 0, 0};
    return v_scale(v, 1.0 / m);
}
