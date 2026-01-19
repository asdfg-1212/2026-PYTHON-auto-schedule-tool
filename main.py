# main.py
from datetime import datetime
from core.task import Task
from core.schedule import Schedule
from utils.parser import save_tasks, load_tasks

def main():
    # 示例：创建任务
    tasks = [
        Task(name="完成大作业", estimated_time=180, importance=5),
        Task(name="学习Python", estimated_time=120, importance=4),
        Task(name="锻炼", estimated_time=60, importance=3),
    ]

    # 示例：安排今天的日程
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    schedule = Schedule(start_time=start_of_day, end_time=end_of_day)

    # 简单的调度逻辑：按重要性排序
    tasks.sort(key=lambda x: x.importance, reverse=True)

    current_time = start_of_day.replace(hour=9) # 假设从早上9点开始

    for task in tasks:
        if not schedule.add_task(task, current_time):
            print(f"无法安排任务: {task.name}")
        else:
            current_time += task.estimated_time

    # 打印日程
    for start, end, task in schedule.get_schedule():
        print(f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}: {task.name}")

    # 保存任务
    save_tasks(tasks)

if __name__ == "__main__":
    main()

