#include "../fugora.h"

int main(void) {
    Engine engine;
    engine_init(&engine, 1.0);

    Object sun = {
        .id = "SUN",
        .name = "Sun",
        .mass = 1.989e30,
        .position = {0, 0, 0},
        .velocity = {0, 0, 0},
        .tracked = true
    };
    add_object(&engine, &sun);

    Object earth = {
        .id = "EARTH",
        .name = "Earth",
        .mass = 5.972e24,
        .position = {1.496e11, 0, 0},
        .velocity = {0, 29780, 0},
        .tracked = true
    };
    add_object(&engine, &earth);

    Object asteroid = {
        .id = "U17267",
        .name = "Fugora Target",
        .mass = 1.0e12,
        .position = {2.0e11, 1.0e10, 0},
        .velocity = {-5000, 20000, 0},
        .tracked = true
    };
    add_object(&engine, &asteroid);

    engine_run(&engine, 10);

    printf("\n--- Final State ---\n");
    for (int i = 0; i < engine.object_count; i++) {
        Object *o = &engine.objects[i];
        printf("%-10s pos: (%.3e, %.3e, %.3e)  vel: %.2f m/s\n",
               o->id, o->position.x, o->position.y, o->position.z,
               v_mag(o->velocity));
    }

    printf("\nAnomalies detected: %d\n", engine.anomaly_count);
    return 0;
}
