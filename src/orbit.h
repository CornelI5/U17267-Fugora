#include "../fugora.h"

double orbital_velocity(double central_mass, double radius) {
    if (radius <= 0) return 0;
    return sqrt(G * central_mass / radius);
}

double orbital_period(double central_mass, double radius) {
    if (radius <= 0 || central_mass <= 0) return 0;
    return 2.0 * M_PI * sqrt(radius * radius * radius / (G * central_mass));
}
