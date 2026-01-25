"""
测试脚本：自动测试调度策略
"""

from datetime import datetime, timedelta
from core.task import Task
from core.schedule import Schedule
from core.scheduler import Scheduler

def test_basic_schedule():
    """
    测试基本调度场景：
    - walk: 300分钟，重要性3
    - nap: 40分钟，重要性1，截止14:45
    - cs: 50分钟，重要性2，起始时间13:50

    预期结果：
    - walk先开始（重要性最高）
    - nap在午餐前完成（11:20-12:00）
    - cs在13:50开始
    - walk继续填充剩余时间
    """
    print("=" * 60)
    print("测试场景：基本调度策略")
    print("=" * 60)

    # 创建今日日程
    today = datetime.now().date()
    schedule = Schedule(today)

    # 添加固定日程
    breakfast_start = datetime.combine(today, datetime.strptime("07:40", "%H:%M").time())
    breakfast_end = datetime.combine(today, datetime.strptime("08:00", "%H:%M").time())
    schedule.add_fixed_slot(breakfast_start, breakfast_end, "早餐")

    lunch_start = datetime.combine(today, datetime.strptime("12:00", "%H:%M").time())
    lunch_end = datetime.combine(today, datetime.strptime("13:40", "%H:%M").time())
    schedule.add_fixed_slot(lunch_start, lunch_end, "午餐")

    dinner_start = datetime.combine(today, datetime.strptime("18:00", "%H:%M").time())
    dinner_end = datetime.combine(today, datetime.strptime("18:30", "%H:%M").time())
    schedule.add_fixed_slot(dinner_start, dinner_end, "晚餐")

    # 创建任务
    tasks = []

    # walk: 300分钟，重要性3
    walk = Task(
        name="walk",
        estimated_time=300,
        importance=3,
        deadline=None,
        earliest_start_time=None,
        note=""
    )
    tasks.append(walk)

    # nap: 40分钟，重要性1，截止14:45
    nap_deadline = datetime.combine(today, datetime.strptime("14:45", "%H:%M").time())
    nap = Task(
        name="nap",
        estimated_time=40,
        importance=1,
        deadline=nap_deadline,
        earliest_start_time=None,
        note=""
    )
    tasks.append(nap)

    # cs: 50分钟，重要性2，起始时间13:50
    cs_start = datetime.combine(today, datetime.strptime("13:50", "%H:%M").time())
    cs = Task(
        name="cs",
        estimated_time=50,
        importance=2,
        deadline=None,
        earliest_start_time=cs_start,
        note=""
    )
    tasks.append(cs)

    # 打印初始日程
    print("\n初始日程：")
    schedule.display()

    # 执行调度
    print("\n执行调度...")
    scheduler = Scheduler()
    scheduled_tasks, failed_tasks = scheduler.schedule_tasks(tasks, schedule)

    # 打印结果
    print("\n最终日程：")
    schedule.display()

    # 分析结果
    print("\n" + "=" * 60)
    print("调度分析：")
    print("=" * 60)

    for task in scheduled_tasks:
        start_str = task.start_time.strftime("%H:%M")
        end_str = task.end_time.strftime("%H:%M")
        duration = int((task.end_time - task.start_time).total_seconds() / 60)
        print(f"{start_str} - {end_str}  {task.name} ({duration}分钟, 重要性:{task.importance})")

    if failed_tasks:
        print("\n未完成的任务：")
        for task in failed_tasks:
            print(f"- {task.name}")

    # 验证重要性顺序
    print("\n验证：")
    task_start_times = {}
    for task in scheduled_tasks:
        base_name = task.name.split(" - Part ")[0] if " - Part " in task.name else task.name
        if base_name not in task_start_times:
            task_start_times[base_name] = task.start_time

    if "walk" in task_start_times and "nap" in task_start_times:
        if task_start_times["walk"] < task_start_times["nap"]:
            print("✓ walk（重要性3）先于nap（重要性1）开始")
        else:
            print("✗ 错误：nap先于walk开始")

    if "nap" in task_start_times:
        nap_start = task_start_times["nap"]
        if nap_start.time() >= datetime.strptime("11:00", "%H:%M").time() and \
           nap_start.time() <= datetime.strptime("12:00", "%H:%M").time():
            print("✓ nap在午餐前安排")
        else:
            print(f"✗ nap开始时间：{nap_start.strftime('%H:%M')}")

    print("=" * 60)

if __name__ == "__main__":
    test_basic_schedule()

