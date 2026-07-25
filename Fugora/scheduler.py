import heapq


class Task:
    def __init__(self, name, priority, complexity):
        self.name = name
        self.priority = priority
        self.complexity = complexity
        self.completed = False

    def __lt__(self, other):
        return self.priority < other.priority


class TaskScheduler:
    def __init__(self):
        self.queue = []
        self.completed_tasks = []

    def add_task(self, task):
        heapq.heappush(self.queue, task)

    def run_next(self, vcpu):
        if not self.queue:
            return None
        task = heapq.heappop(self.queue)
        vcpu.execute_task(task.complexity)
        task.completed = True
        self.completed_tasks.append(task)
        return task

    def run_all(self, vcpu):
        while self.queue:
            self.run_next(vcpu)

    def clear(self):
        self.queue.clear()
        self.completed_tasks.clear()
