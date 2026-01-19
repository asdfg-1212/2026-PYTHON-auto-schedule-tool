# main.py
from datetime import datetime
from core.task import Task
from core.schedule import Schedule
from utils.parser import save_tasks, load_tasks

tasks = [] # 全局任务列表

def creat_task_from_input() -> Task:
    """命令行交互创建Task对象"""    
    name = input("请输入任务名称: ")
    estimated_time = int(input("请输入预计用时（分钟）: "))
    importance = int(input("请输入重要程度（1-5）: "))

    deadline_input = input("请输入截止时间（格式：2026-01-20 18:00，可选）: ")
    deadline = datetime.strptime(deadline_input, "%Y-%m-%d %H:%M") if deadline_input else None

    note = input("请输入备注（可选）: ")

    # 创建Task对象
    task = Task(
        name=name,
        estimated_time=estimated_time,
        importance=importance,
        deadline=deadline,
        note=note
    )

    return task

def main():
    global tasks
    print("欢迎来到自动日程规划器！\nWelcome to the Auto Scheduler!")

    while True:
        
    


if __name__ == "__main__":
    main()

