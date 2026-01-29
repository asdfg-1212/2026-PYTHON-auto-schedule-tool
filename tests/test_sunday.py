"""测试周日日程（和用户实际运行一样的配置）"""
from datetime import datetime, timedelta, date
from core.task import Task
from core.schedule import Schedule
from core.scheduler import Scheduler

# 创建周日的日程
target_date = date(2026, 2, 1)
schedule = Schedule(target_date)

# 添加固定时段（使用datetime对象）
schedule.add_fixed_slot(
    datetime.combine(target_date, datetime.strptime('07:40', "%H:%M").time()),
    datetime.combine(target_date, datetime.strptime('08:00', "%H:%M").time()),
    '早餐'
)
schedule.add_fixed_slot(
    datetime.combine(target_date, datetime.strptime('12:00', "%H:%M").time()),
    datetime.combine(target_date, datetime.strptime('13:40', "%H:%M").time()),
    '午休'
)
schedule.add_fixed_slot(
    datetime.combine(target_date, datetime.strptime('18:00', "%H:%M").time()),
    datetime.combine(target_date, datetime.strptime('18:30', "%H:%M").time()),
    '晚餐'
)

print("初始日程：")
schedule.display()

# 创建任务（使用datetime对象）
walk = Task('walk', 300, 3, splittable=True)

# nap的deadline
nap_deadline = datetime.combine(target_date, datetime.strptime('14:45', "%H:%M").time())
nap = Task('nap', 40, 1, splittable=True, deadline=nap_deadline)

# cs的earliest_start_time
cs_start = datetime.combine(target_date, datetime.strptime('13:50', "%H:%M").time())
cs = Task('cs', 50, 2, splittable=True, earliest_start_time=cs_start)

tasks = [walk, nap, cs]

# 运行调度
scheduled, failed = Scheduler.schedule_tasks(tasks, schedule)

print("\n调度后日程：")
schedule.display()

if failed:
    print("\n❌ 失败的任务:")
    for t in failed:
        print(f"  - {t.name}")
else:
    print("\n✅ 所有任务成功调度！")
