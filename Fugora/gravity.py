import math
from .constants import G, ANOMALY_THRESHOLD
from .vector import Vec3
from .objects import AnomalyRecord


def compute_nbody_gravity(objects):
    n = len(objects)
    accelerations = [Vec3(0, 0, 0) for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            diff = objects[j].position - objects[i].position
            dist_sq = diff.magnitude_sq()

            if dist_sq == 0:
                continue

            dist = math.sqrt(dist_sq)
            force_mag = G / dist_sq

            acc_i = diff * (force_mag * objects[j].mass / dist)
            acc_j = diff * (-force_mag * objects[i].mass / dist)

            accelerations[i] = accelerations[i] + acc_i
            accelerations[j] = accelerations[j] + acc_j

    for i in range(n):
        objects[i].acceleration = accelerations[i]


def detect_anomalies(objects, central_mass, current_time):
    anomalies = []

    for obj in objects:
        if not obj.tracked or obj.mass >= central_mass * 0.01:
            continue

        dist = obj.position.magnitude()
        if dist == 0:
            continue

        expected_speed = math.sqrt(G * central_mass / dist)
        actual_speed = obj.speed()
        deviation = abs(actual_speed - expected_speed) / expected_speed

        if deviation > ANOMALY_THRESHOLD:
            record = AnomalyRecord(
                object_id=obj.id,
                deviation=deviation,
                timestamp=current_time,
                expected=expected_speed,
                actual=actual_speed,
            )
            anomalies.append(record)

    return anomalies
