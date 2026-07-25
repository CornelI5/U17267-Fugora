#include "../fugora.h"

void engine_init(Engine *e, double refresh) {
    memset(e, 0, sizeof(Engine));
    e->refresh_rate = refresh;
    e->running = false;
    e->start_time = time(NULL);
}

int add_object(Engine *e, const Object *obj) {
    if (e->object_count >= MAX_OBJECTS) return -1;
    e->objects[e->object_count] = *obj;
    e->object_count++;
    return e->object_count - 1;
}

Object* find_object(Engine *e, const char *id) {
    for (int i = 0; i < e->object_count; i++) {
        if (strcmp(e->objects[i].id, id) == 0)
            return &e->objects[i];
    }
    return NULL;
}

void engine_run(Engine *e, int seconds) {
    e->running = true;
    time_t end = time(NULL) + seconds;

    while (e->running && time(NULL) < end) {

        for (int i = 0; i < e->object_count; i++) {
            Vec3 total = {0, 0, 0};
            for (int j = 0; j < e->object_count; j++) {
                if (i == j) continue;
                total = v_add(total, gravity_accel(&e->objects[i], &e->objects[j]));
            }
            e->objects[i].acceleration = total;
        }

        for (int i = 0; i < e->object_count; i++) {
            Object *o = &e->objects[i];
            o->velocity = v_add(o->velocity, v_scale(o->acceleration, e->refresh_rate));
            o->position = v_add(o->position, v_scale(o->velocity, e->refresh_rate));
        }

        for (int i = 0; i < e->object_count; i++) {
            Object *o = &e->objects[i];
            double speed = v_mag(o->velocity);
            double dist = v_mag(o->position);
            double expected = orbital_velocity(1.989e30, dist);
            detect_anomaly(e, o->id, expected, speed);
        }

        struct timespec ts;
        ts.tv_sec = (time_t)e->refresh_rate;
        ts.tv_nsec = (long)((e->refresh_rate - ts.tv_sec) * 1e9);
        nanosleep(&ts, NULL);
    }

    e->running = false;
}

void engine_stop(Engine *e) {
    e->running = false;
}
