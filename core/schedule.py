# core/schedule.py
from datetime import datetime, timedelta

class Schedule:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.time_slots = []

    def add_task(self, task, start_time):
        end_time = start_time + task.estimated_time
        if end_time > self.end_time:
            return False  # Task doesn't fit

        for _, existing_end_time in self.time_slots:
            if start_time < existing_end_time:
                return False # Overlapping task

        self.time_slots.append((start_time, end_time, task))
        self.time_slots.sort()
        return True

    def get_schedule(self):
        return self.time_slots

