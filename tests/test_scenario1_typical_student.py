"""测试场景一：典型学生日程
测试日期：周二 (2026-02-03)
测试目标：验证deadline分段调度、前瞻性预留、重要性排序
"""
from datetime import datetime, timedelta, date
from core.task import Task
from core.schedule import Schedule
from core.scheduler import Scheduler

# 创建周二的日程
target_date = date(2026, 2, 3)
schedule = Schedule(target_date)

# 添加固定时段
# 早餐
schedule.add_fixed_slot(
    datetime.combine(target_date, datetime.strptime('08:40', "%H:%M").time()),
    datetime.combine(target_date, datetime.strptime('09:00', "%H:%M").time()),
    '早餐'
)
# 课程1：计算机操作系统
schedule.add_fixed_slot(
    datetime.combine(target_date, datetime.strptime('10:10', "%H:%M").time()),
    datetime.combine(target_date, datetime.strptime('12:00', "%H:%M").time()),
    '课程: 计算机操作系统'
)
# 午休
schedule.add_fixed_slot(
    datetime.combine(target_date, datetime.strptime('12:00', "%H:%M").time()),
    datetime.combine(target_date, datetime.strptime('13:40', "%H:%M").time()),
    '午休'
)
# 课程2：编译原理
schedule.add_fixed_slot(
    datetime.combine(target_date, datetime.strptime('14:00', "%H:%M").time()),
    datetime.combine(target_date, datetime.strptime('17:00', "%H:%M").time()),
    '课程: 编译原理'
)
# 晚餐
schedule.add_fixed_slot(
    datetime.combine(target_date, datetime.strptime('18:00', "%H:%M").time()),
    datetime.combine(target_date, datetime.strptime('18:30', "%H:%M").time()),
    '晚餐'
)

print("=" * 60)
print("场景一：典型学生日程")
print("=" * 60)
print("\n初始日程：")
schedule.display()

# 创建任务
# 1. 完成Python大作业，180分钟，重要性5，起始时间09:00，deadline=23:00，可拆分
py_start = datetime.combine(target_date, datetime.strptime('09:00', "%H:%M").time())
py_deadline = datetime.combine(target_date, datetime.strptime('23:00', "%H:%M").time())
py_homework = Task('Python大作业', 180, 5, splittable=True, 
                   earliest_start_time=py_start, deadline=py_deadline)

# 2. 复习英语单词，60分钟，重要性3，deadline=14:20，不可拆分
eng_deadline = datetime.combine(target_date, datetime.strptime('14:20', "%H:%M").time())
english = Task('英语单词', 60, 3, splittable=False, deadline=eng_deadline)

# 3. 运动锻炼，30分钟，重要性4，无约束，可拆分
exercise = Task('运动锻炼', 30, 4, splittable=True)

tasks = [py_homework, english, exercise]

print("\n任务列表：")
for i, task in enumerate(tasks, 1):
    print(f"{i}. {task.name}:")
    print(f"   - 预计用时: {task.estimated_time.total_seconds() // 60}分钟")
    print(f"   - 重要性: {task.importance}")
    print(f"   - 可拆分: {'是' if task.splittable else '否'}")
    if task.earliest_start_time:
        print(f"   - 起始时间: {task.earliest_start_time.strftime('%H:%M')}")
    if task.deadline:
        print(f"   - 截止时间: {task.deadline.strftime('%H:%M')}")

# 运行调度
print("\n" + "=" * 60)
print("开始智能调度...")
print("=" * 60)
scheduled, failed = Scheduler.schedule_tasks(tasks, schedule)

print("\n最终日程：")
schedule.display()

if failed:
    print("\n❌ 失败的任务:")
    for t in failed:
        print(f"  - {t.name}")
else:
    print("\n✅ 所有任务成功调度！")

# 统计原始任务完成情况
completed_task_ids = set()
for task in scheduled:
    # 提取原始任务名（去掉 Part 后缀）
    base_name = task.name.split(" - Part ")[0] if " - Part " in task.name else task.name
    # 找到对应的原始任务
    for original_task in tasks:
        if original_task.name == base_name:
            completed_task_ids.add(original_task.id)
            break

print("\n性能指标：")
print(f"- 原始任务完成率: {len(completed_task_ids)}/{len(tasks)} = {len(completed_task_ids)/len(tasks)*100:.0f}%")
print(f"- 调度片段总数: {len(scheduled)}个")

print("\n" + "=" * 60)
print("场景一测试完成")
print("=" * 60)
