"""测试场景二：Deadline冲突测试
测试日期：周二 (2026-02-03)
测试目标：验证不可拆分任务的deadline约束处理、任务连续性优先策略
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
print("场景二：Deadline冲突测试")
print("=" * 60)
print("\n初始日程：")
schedule.display()

# 创建任务
# 1. 长任务A，150分钟，重要性5，deadline=10:10，不可拆分
longA_deadline = datetime.combine(target_date, datetime.strptime('10:10', "%H:%M").time())
longA = Task('长任务A', 150, 5, splittable=False, deadline=longA_deadline)

# 2. 短任务B，60分钟，重要性4，deadline=14:00，不可拆分
shortB_deadline = datetime.combine(target_date, datetime.strptime('14:00', "%H:%M").time())
shortB = Task('短任务B', 60, 4, splittable=False, deadline=shortB_deadline)

# 3. 任务C，120分钟，重要性3，无deadline，可拆分
taskC = Task('任务C', 120, 3, splittable=True)

tasks = [longA, shortB, taskC]

print("\n任务列表：")
for i, task in enumerate(tasks, 1):
    print(f"{i}. {task.name}:")
    print(f"   - 预计用时: {task.estimated_time.total_seconds() // 60}分钟")
    print(f"   - 重要性: {task.importance}")
    print(f"   - 可拆分: {'是' if task.splittable else '否'}")
    if task.deadline:
        print(f"   - 截止时间: {task.deadline.strftime('%H:%M')}")

print("\n理论分析：")
print("- 长任务A需要150分钟连续时间，deadline=10:10")
print("- 在10:10前最长的连续空闲时间是09:00-10:10（70分钟）")
print("- 预期：长任务A无法在deadline前完成，将失败")
print("- 短任务B需要60分钟，可以安排在deadline 14:00前")

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
        remaining_min = t.estimated_time.total_seconds() / 60
        print(f"  - {t.name} (完全未安排，需要 {remaining_min:.0f} 分钟)")
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
print("场景二测试完成")
print("=" * 60)
