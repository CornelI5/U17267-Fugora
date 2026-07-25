import time
import os
import platform
import sys
import threading


class PlatformInfo:
    def __init__(self):
        self.system = platform.system()
        self.machine = platform.machine()
        self.processor = platform.processor()
        self.python_version = platform.python_version()
        self.distro_name = self._detect_distro()
        self.distro_id = self._detect_distro_id()
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        self.is_macos = self.system == "Darwin"
        self.is_64bit = platform.architecture()[0] == "64bit"
        self.cpu_count = os.cpu_count() or 1
        self.home_dir = os.path.expanduser("~")
        self.config_dir = self._get_config_dir()

    def _detect_distro(self):
        if not self.is_linux:
            return self.system

        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
        except FileNotFoundError:
            pass

        try:
            with open("/etc/lsb-release", "r") as f:
                for line in f:
                    if line.startswith("DISTRIB_DESCRIPTION="):
                        return line.split("=", 1)[1].strip().strip('"')
        except FileNotFoundError:
            pass

        return "Unknown Linux"

    def _detect_distro_id(self):
        if not self.is_linux:
            return self.system.lower()

        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.split("=", 1)[1].strip().strip('"')
        except FileNotFoundError:
            pass

        return "unknown"

    def _get_config_dir(self):
        if self.is_windows:
            base = os.environ.get("APPDATA", self.home_dir)
            return os.path.join(base, "fugora")
        elif self.is_macos:
            return os.path.join(self.home_dir, "Library", "Application Support", "fugora")
        else:
            xdg = os.environ.get("XDG_CONFIG_HOME", os.path.join(self.home_dir, ".config"))
            return os.path.join(xdg, "fugora")

    def ensure_config_dir(self):
        os.makedirs(self.config_dir, exist_ok=True)
        return self.config_dir

    def summary(self):
        return {
            "system": self.system,
            "distro": self.distro_name,
            "distro_id": self.distro_id,
            "machine": self.machine,
            "processor": self.processor,
            "python": self.python_version,
            "64bit": self.is_64bit,
            "cpu_count": self.cpu_count,
            "config_dir": self.config_dir,
        }


class Task:
    def __init__(self, name, callback=None, priority=0, complexity=100,
                 is_critical=False, tags=None):
        self.name = name
        self.callback = callback
        self.priority = priority
        self.complexity = complexity
        self.is_critical = is_critical
        self.tags = tags or []
        self.completed = False
        self.result = None
        self.error = None
        self.created_at = time.time()
        self.finished_at = None

    def __lt__(self, other):
        return self.priority < other.priority

    def execute(self):
        try:
            if self.callback:
                self.result = self.callback()
            self.completed = True
        except Exception as e:
            self.error = str(e)
            self.completed = True
        finally:
            self.finished_at = time.time()
        return self.result


class VirtualCPU:
    def __init__(self, cores=None, clock_speed_ghz=3.0):
        self.platform = PlatformInfo()
        self.cores = cores or self.platform.cpu_count
        self.clock_speed = clock_speed_ghz * 1e9
        self.current_load = 0.0
        self.memory_used = 0
        self.memory_limit = 2048 * 1024 * 1024
        self.instructions_executed = 0
        self.start_time = time.time()
        self.throttle_threshold = 80.0
        self.task_registry = {}
        self.task_history = []
        self.lock = threading.Lock()

    def register_task_type(self, name, handler):
        self.task_registry[name] = handler

    def create_task(self, name, callback=None, priority=0, complexity=100,
                    is_critical=False, tags=None):
        task = Task(
            name=name,
            callback=callback,
            priority=priority,
            complexity=complexity,
            is_critical=is_critical,
            tags=tags,
        )
        return task

    def execute_task(self, task_or_complexity, is_critical=False):
        if isinstance(task_or_complexity, Task):
            return self._execute_task_object(task_or_complexity)

        complexity = task_or_complexity
        start = time.time()

        if not is_critical and self.current_load > self.throttle_threshold:
            return 0.0

        simulated_work = 0
        for _ in range(int(complexity)):
            simulated_work += 1

        elapsed = time.time() - start
        self.instructions_executed += int(complexity)

        with self.lock:
            load = min(100.0, (elapsed / (1.0 / self.clock_speed)) * 100)
            self.current_load = load

        return elapsed

    def _execute_task_object(self, task):
        if not task.is_critical and self.current_load > self.throttle_threshold:
            return None

        start = time.time()
        task.execute()
        elapsed = time.time() - start

        self.instructions_executed += task.complexity
        self.task_history.append(task)

        with self.lock:
            load = min(100.0, (elapsed / (1.0 / self.clock_speed)) * 100)
            self.current_load = load

        return task.result

    def execute_registered(self, name, *args, **kwargs):
        handler = self.task_registry.get(name)
        if not handler:
            return None

        task = self.create_task(
            name=name,
            callback=lambda: handler(*args, **kwargs),
            complexity=100,
        )
        return self._execute_task_object(task)

    def allocate_memory(self, size_bytes):
        with self.lock:
            if self.memory_used + size_bytes > self.memory_limit:
                return False
            self.memory_used += size_bytes
            return True

    def free_memory(self, size_bytes):
        with self.lock:
            self.memory_used = max(0, self.memory_used - size_bytes)

    def set_memory_limit(self, limit_bytes):
        self.memory_limit = limit_bytes

    def get_load(self):
        return self.current_load

    def is_throttled(self):
        return self.current_load > self.throttle_threshold

    def set_throttle_threshold(self, value):
        self.throttle_threshold = max(0.0, min(100.0, value))

    def get_stats(self):
        uptime = time.time() - self.start_time
        return {
            "cores": self.cores,
            "clock_speed_ghz": self.clock_speed / 1e9,
            "load_percent": round(self.current_load, 2),
            "memory_used_mb": round(self.memory_used / (1024 ** 2), 2),
            "memory_limit_mb": round(self.memory_limit / (1024 ** 2), 2),
            "instructions": self.instructions_executed,
            "uptime_s": round(uptime, 2),
            "tasks_completed": len(self.task_history),
            "throttled": self.is_throttled(),
            "platform": self.platform.summary(),
        }

    def get_task_history(self, limit=50):
        return self.task_history[-limit:]

    def clear_history(self):
        self.task_history.clear()

    def summary(self):
        stats = self.get_stats()
        plat = stats["platform"]
        lines = [
            "FUGORA Virtual CPU",
            f"  Platform    : {plat['distro']} ({plat['system']})",
            f"  Arch        : {plat['machine']} {'64-bit' if plat['64bit'] else '32-bit'}",
            f"  Cores       : {stats['cores']}",
            f"  Clock       : {stats['clock_speed_ghz']:.1f} GHz",
            f"  Load        : {stats['load_percent']}%",
            f"  Memory      : {stats['memory_used_mb']} / {stats['memory_limit_mb']} MB",
            f"  Instructions: {stats['instructions']}",
            f"  Tasks Done  : {stats['tasks_completed']}",
            f"  Throttled   : {'Yes' if stats['throttled'] else 'No'}",
            f"  Uptime      : {stats['uptime_s']}s",
        ]
        return "\n".join(lines)
