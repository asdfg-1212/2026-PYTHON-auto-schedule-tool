# utils/parser.py
import json
from core.task import Task

def save_tasks(tasks, filename="data/tasks.json"):
    with open(filename, 'w') as f:
        json.dump([task.__dict__ for task in tasks], f, default=str, indent=4)

def load_tasks(filename="data/tasks.json"):
    try:
        with open(filename, 'r') as f:
            tasks_data = json.load(f)
            return [Task(**data) for data in tasks_data]
    except FileNotFoundError:
        return []

