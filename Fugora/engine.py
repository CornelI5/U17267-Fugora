import time
from .constants import DEFAULT_DT, SUN_MASS
from .integrator import VelocityVerlet
from .gravity import compute_nbody_gravity, detect_anomalies
from .objects import CelestialObject


class FugoraEngine:
    def __init__(self, dt=DEFAULT_DT):
        self.objects = []
        self.dt = float(dt)
        self.integrator = VelocityVerlet(self.dt)
        self.time_elapsed = 0.0
        self.step_count = 0
        self.anomalies = []
        self.central_mass = SUN_MASS
        self._running = False

    def add_object(self, obj):
        if not isinstance(obj, CelestialObject):
            raise TypeError("Expected CelestialObject instance")
        self.objects.append(obj)

    def remove_object(self, obj_id):
        self.objects = [o for o in self.objects if o.id != obj_id]

    def get_object(self, obj_id):
        for obj in self.objects:
            if obj.id == obj_id:
                return obj
        return None

    def set_central_mass(self, mass):
        self.central_mass = float(mass)

    def initialize(self):
        compute_nbody_gravity(self.objects)

    def step(self):
        self.integrator.step(self.objects)
        self.time_elapsed += self.dt
        self.step_count += 1

        new_anomalies = detect_anomalies(
            self.objects, self.central_mass, self.time_elapsed
        )
        self.anomalies.extend(new_anomalies)

        return new_anomalies

    def run(self, total_steps, callback=None):
        self._running = True
        self.initialize()

        for i in range(total_steps):
            if not self._running:
                break

            anomalies = self.step()

            if callback:
                callback(self, i, anomalies)

        self._running = False

    def stop(self):
        self._running = False

    def get_state(self):
        return {
            "time_elapsed": self.time_elapsed,
            "step_count": self.step_count,
            "object_count": len(self.objects),
            "anomaly_count": len(self.anomalies),
            "objects": [obj.copy_state() for obj in self.objects],
        }

    def summary(self):
        state = self.get_state()
        lines = [
            f"FUGORA Engine Status",
            f"  Time elapsed : {state['time_elapsed']:.2e} s",
            f"  Steps        : {state['step_count']}",
            f"  Objects      : {state['object_count']}",
            f"  Anomalies    : {state['anomaly_count']}",
        ]
        return "\n".join(lines)
