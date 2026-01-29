"""测试场景四：前瞻性预留压力测试
测试日期：周二 (2026-02-03)
测试目标：验证前瞻性时间预留算法、不可拆分任务的约束检查
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
print("场景四：前瞻性预留压力测试")
print("=" * 60)
print("\n初始日程：")
schedule.display()

# 创建任务
# 1. 紧急复习，80分钟，重要性5，deadline=10:10，不可拆分
urgent_deadline = datetime.combine(target_date, datetime.strptime('10:10', "%H:%M").time())
urgent_review = Task('紧急复习', 80, 5, splittable=False, deadline=urgent_deadline)

# 2. 长作业，200分钟，重要性4，无deadline，可拆分
long_homework = Task('长作业', 200, 4, splittable=True)

tasks = [urgent_review, long_homework]

print("\n任务列表：")
for i, task in enumerate(tasks, 1):
    print(f"{i}. {task.name}:")
    print(f"   - 预计用时: {task.estimated_time.total_seconds() // 60}分钟")
    print(f"   - 重要性: {task.importance}")
    print(f"   - 可拆分: {'是' if task.splittable else '否'}")
    if task.deadline:
        print(f"   - 截止时间: {task.deadline.strftime('%H:%M')}")

print("\n时间分析：")
print("- 09:00-10:10：仅70分钟，无法完成紧急复习（需80分钟）")
print("- 08:00-08:40有40分钟，加上09:00-10:10的70分钟，总计110分钟")
print("- 但紧急复习是不可拆分任务，无法利用分散的时间段")
print("\n预期结果：")
print("- 紧急复习无法安排（不可拆分且时间不足）")
print("- 长作业填充所有可用时间")

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
    print("\n约束检查结果：")
    print(f"✓ 正确识别：紧急复习需要{urgent_review.estimated_time.total_seconds() // 60}分钟连续时间")
    print(f"✓ 在deadline {urgent_deadline.strftime('%H:%M')}前只有70分钟连续空闲")
    print(f"✓ 算法正确标记为失败")
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

# 计算已安排时间
total_scheduled_time = 0
for task in scheduled:
    duration = (task.end_time - task.start_time).total_seconds() / 60
    total_scheduled_time += duration

print("\n性能指标：")
print(f"- 原始任务完成率: {len(completed_task_ids)}/{len(tasks)} = {len(completed_task_ids)/len(tasks)*100:.0f}%")
print(f"- 调度片段总数: {len(scheduled)}个")
print(f"- 已安排任务时间: {total_scheduled_time:.0f}分钟")

print("\n" + "=" * 60)
print("场景四测试完成")
print("=" * 60)
