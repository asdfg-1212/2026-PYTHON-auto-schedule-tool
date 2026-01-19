# core/task.py
        return f"Task(name={self.name}, estimated_time={self.estimated_time}, importance={self.importance})"
    def __repr__(self):

        self.completed = False
        self.deadline = deadline
        self.importance = importance
        self.estimated_time = timedelta(minutes=estimated_time)
        self.name = name
        self.id = uuid.uuid4()
    def __init__(self, name, estimated_time, importance, deadline=None):
class Task:

from datetime import timedelta
import uuid

