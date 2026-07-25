import time
import gc
from .constants import DEFAULT_DT, SUN_MASS
from .integrator import VelocityVerlet
from .gravity import compute_nbody_gravity, detect_anomalies
from .objects import CelestialObject
from .events import EventManager
from .sources import SourceManager
from .vcpu import VirtualCPU
from .scheduler import TaskScheduler, Task


class FugoraEngine:
    def __init__(self, dt=DEFAULT_DT, cpu_cores=1, allow_external=False):
        self.objects = []
        self.dt = float(dt)
        self.integrator = VelocityVerlet(self.dt)
        self.time_elapsed = 0.0
        self.step_count = 0
        self.anomalies = []
        self.central_mass = SUN_MASS
        self._running = False
        
        self.events = EventManager()
        self.sources = SourceManager(allow_external=allow_external)
        
        self.vcpu = VirtualCPU(cores=cpu_cores)
        self.scheduler = TaskScheduler()

    def add_object(self, obj):
        if not isinstance(obj, CelestialObject):
            raise TypeError("Expected CelestialObject instance")
        self.objects.append(obj)
        self.vcpu.allocate_memory(1024)
        self.events.emit("object_added", obj.id)

    def remove_object(self, obj_id):
        self.objects = [o for o in self.objects if o.id != obj_id]
        self.vcpu.free_memory(1024)
        self.events.emit("object_removed", obj_id)

    def get_object(self, obj_id):
        for obj in self.objects:
            if obj.id == obj_id:
                return obj
        return None

    def set_central_mass(self, mass):
        self.central_mass = float(mass)

    def initialize(self):
        compute_nbody_gravity(self.objects)
        self.sources.activate_all()
        self.events.emit("engine_initialized")

    def ingest_external_data(self):
        external_data = self.sources.get_all_data()
        if external_data:
            self.events.emit("data_ingested", external_data)

    def step(self):
        task = Task(f"Step_{self.step_count}", priority=self.step_count, complexity=1000)
        self.scheduler.add_task(task)
        self.scheduler.run_next(self.vcpu)

        self.ingest_external_data()
        self.integrator.step(self.objects)
        self.time_elapsed += self.dt
        self.step_count += 1

        new_anomalies = detect_anomalies(
            self.objects, self.central_mass, self.time_elapsed
        )
        
        if new_anomalies:
            self.anomalies.extend(new_anomalies)
            self.events.emit("anomaly_detected", new_anomalies)

        self.events.emit("step_completed", {
            "time": self.time_elapsed,
            "step": self.step_count,
            "cpu_load": self.vcpu.current_load
        })

        return new_anomalies

    def run(self, total_steps, callback=None):
        self._running = True
        self.initialize()

        try:
            for i in range(total_steps):
                if not self._running:
                    break
                anomalies = self.step()
                if callback:
                    callback(self, i, anomalies)
        finally:
            self.cleanup()

    def stop(self):
        self._running = False

    def cleanup(self):
        self.sources.deactivate_all()
        self.events.clear()
        self.objects.clear()
        self.anomalies.clear()
        self.scheduler.queue.clear()
        self.scheduler.completed_tasks.clear()
        gc.collect()
        self._running = False
        self.events.emit("simulation_finished")

    def get_state(self):
        return {
            "time_elapsed": self.time_elapsed,
            "step_count": self.step_count,
            "object_count": len(self.objects),
            "anomaly_count": len(self.anomalies),
            "objects": [obj.copy_state() for obj in self.objects],
            "sources_active": list(self.sources.sources.keys()),
            "cpu_stats": self.vcpu.get_stats()
        }

    def summary(self):
        state = self.get_state()
        cpu = state['cpu_stats']
        lines = [
            f"FUGORA Engine v1.0 Status",
            f"  Time elapsed : {state['time_elapsed']:.2e} s",
            f"  Steps        : {state['step_count']}",
            f"  Objects      : {state['object_count']}",
            f"  Anomalies    : {state['anomaly_count']} (Unbounded)",
            f"  CPU Load     : {cpu['load_percent']}%",
            f"  Memory Used  : {cpu['memory_used_mb']} MB",
        ]
        return "\n".join(lines)
