import time


class VirtualCPU:
    def __init__(self, cores=1, clock_speed_ghz=3.0):
        self.cores = cores
        self.clock_speed = clock_speed_ghz * 1e9
        self.current_load = 0.0
        self.memory_used = 0
        self.instructions_executed = 0
        self.start_time = time.time()
        self.throttle_threshold = 80.0

    def execute_task(self, complexity, is_critical=False):
        start = time.time()
        
        if not is_critical and self.current_load > self.throttle_threshold:
            return 0.0

        simulated_work = 0
        for _ in range(int(complexity)):
            simulated_work += 1
        
        elapsed = time.time() - start
        self.instructions_executed += int(complexity)
        
        load = min(100.0, (elapsed / (1.0 / self.clock_speed)) * 100)
        self.current_load = load
        
        return elapsed

    def allocate_memory(self, size_bytes):
        self.memory_used += size_bytes

    def free_memory(self, size_bytes):
        self.memory_used = max(0, self.memory_used - size_bytes)

    def get_stats(self):
        uptime = time.time() - self.start_time
        return {
            "cores": self.cores,
            "clock_speed_ghz": self.clock_speed / 1e9,
            "load_percent": round(self.current_load, 2),
            "memory_used_mb": round(self.memory_used / (1024**2), 2),
            "instructions": self.instructions_executed,
            "uptime_s": round(uptime, 2)
        }
