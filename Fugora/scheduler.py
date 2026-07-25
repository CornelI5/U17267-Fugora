import heapq
from .vcpu import Task


class TaskScheduler:
    def __init__(self):
        self.queue = []
        self.completed_tasks = []

    def add_task(self, task):
        if not isinstance(task, Task):
            raise TypeError("Expected Task instance from fugora.vcpu")
        heapq.heappush(self.queue, task)

    def run_next(self, vcpu):
        if not self.queue:
            return None
        task = heapq.heappop(self.queue)
        vcpu.execute_task(task)
        self.completed_tasks.append(task)
        return task

    def run_all(self, vcpu):
        while self.queue:
            self.run_next(vcpu)

    def get_pending_count(self):
        return len(self.queue)

    def get_completed_count(self):
        return len(self.completed_tasks)

    def clear(self):
        self.queue.clear()
        self.completed_tasks.clear()
