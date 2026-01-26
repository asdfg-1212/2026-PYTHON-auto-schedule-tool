# utils/parser.py
import json
from datetime import datetime
from core.task import Task

TASK_STORE = "data/tasks.json"


def load_date_data(target_date_str, filename=TASK_STORE):
    """加载指定日期的元信息和任务安排，返回 (meta_dict, [(task, start_dt, end_dt), ...])"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}, []

    # 兼容旧列表结构
    if isinstance(data, list):
        return {}, []

    # 兼容旧结构：直接是 tasks 列表
    if isinstance(data, dict) and 'start' in data or 'task' in data:
        data = {target_date_str: data}

    date_entry = data.get(target_date_str, {})

    # 如果是旧格式的列表
    if isinstance(date_entry, list):
        raw_tasks = date_entry
        meta = {}
    else:
        meta = date_entry.get('meta', {}) if isinstance(date_entry, dict) else {}
        raw_tasks = date_entry.get('tasks', []) if isinstance(date_entry, dict) else []

    result = []
    for item in raw_tasks:
        task = Task.from_dict(item['task'])
        start_dt = datetime.fromisoformat(item['start'])
        end_dt = datetime.fromisoformat(item['end'])
        task.start_time = start_dt
        task.end_time = end_dt
        result.append((task, start_dt, end_dt))
    return meta, result


def load_date_entries(target_date_str, filename=TASK_STORE):
    """兼容接口：仅返回任务列表"""
    _, entries = load_date_data(target_date_str, filename)
    return entries


def save_date_entries(target_date_str, schedule, filename=TASK_STORE, meta=None):
    """将当前日程的已安排任务持久化到指定日期下，附带元信息"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # 兼容旧版本：如果是列表，重置为字典
    if isinstance(data, list):
        data = {}

    serialized = []
    for start, end, task in schedule.time_slots:
        serialized.append({
            'start': start.isoformat(),
            'end': end.isoformat(),
            'task': task.to_dict()
        })

    data[target_date_str] = {
        'meta': meta or {},
        'tasks': serialized
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# 保留旧的简单接口（未按日期使用时）
def save_tasks(tasks, filename=TASK_STORE):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([task.__dict__ for task in tasks], f, default=str, indent=4)


def load_tasks(filename=TASK_STORE):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
            return [Task(**data) for data in tasks_data]
    except FileNotFoundError:
        return []
