#include "../fugora.h"

int detect_anomaly(Engine *e, const char *id, double expected, double actual) {
    double dev = fabs(expected - actual);
    if (dev < 0.01) return -1;

    Anomaly a;
    strncpy(a.object_id, id, MAX_NAME - 1);
    a.deviation = dev;
    a.timestamp = (double)time(NULL);

    e->anomalies[e->anomaly_count] = a;
    e->anomaly_count++;
    return e->anomaly_count - 1;
}
