#ifndef FUGORA_H
#define FUGORA_H

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>
#include <stdbool.h>

#define FUGORA_VERSION "0.1.0"
#define MAX_OBJECTS 10000
#define MAX_SOURCES 32
#define MAX_NAME 128
#define G 6.67430e-11

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    char id[MAX_NAME];
    char name[MAX_NAME];
    double mass;
    Vec3 position;
    Vec3 velocity;
    Vec3 acceleration;
    bool tracked;
} Object;

typedef struct {
    char name[MAX_NAME];
    char url[256];
    bool active;
} Source;

typedef struct {
    char object_id[MAX_NAME];
    double deviation;
    double timestamp;
} Anomaly;

typedef struct {
    Object objects[MAX_OBJECTS];
    int object_count;
    Source sources[MAX_SOURCES];
    int source_count;
    Anomaly anomalies[1000];
    int anomaly_count;
    double refresh_rate;
    bool running;
    time_t start_time;
} Engine;

void engine_init(Engine *e, double refresh);
void engine_run(Engine *e, int seconds);
void engine_stop(Engine *e);
int add_object(Engine *e, const Object *obj);
Object* find_object(Engine *e, const char *id);
double gravity_force(double m1, double m2, double dist);
Vec3 gravity_accel(const Object *a, const Object *b);
double orbital_velocity(double central_mass, double radius);
double orbital_period(double central_mass, double radius);
int detect_anomaly(Engine *e, const char *id, double expected, double actual);
Vec3 v_add(Vec3 a, Vec3 b);
Vec3 v_sub(Vec3 a, Vec3 b);
Vec3 v_scale(Vec3 v, double s);
double v_mag(Vec3 v);
double v_dist(Vec3 a, Vec3 b);
Vec3 v_norm(Vec3 v);

#endif
