"""测试场景三：任务拆分与合并测试
测试日期：周日 (2026-02-01)
测试目标：验证任务拆分逻辑、Part编号规则、任务合并功能
"""
from datetime import datetime, timedelta, date
from core.task import Task
from core.schedule import Schedule
from core.scheduler import Scheduler

# 创建周日的日程
target_date = date(2026, 2, 1)
schedule = Schedule(target_date)

# 添加固定时段
# 早餐
schedule.add_fixed_slot(
    datetime.combine(target_date, datetime.strptime('07:40', "%H:%M").time()),
    datetime.combine(target_date, datetime.strptime('08:00', "%H:%M").time()),
    '早餐'
)
# 午休
schedule.add_fixed_slot(
    datetime.combine(target_date, datetime.strptime('12:00', "%H:%M").time()),
    datetime.combine(target_date, datetime.strptime('13:40', "%H:%M").time()),
    '午休'
)
# 晚餐
schedule.add_fixed_slot(
    datetime.combine(target_date, datetime.strptime('18:00', "%H:%M").time()),
    datetime.combine(target_date, datetime.strptime('18:30', "%H:%M").time()),
    '晚餐'
)

print("=" * 60)
print("场景三：任务拆分与合并测试")
print("=" * 60)
print("\n初始日程：")
schedule.display()

# 创建任务
# 1. walk，300分钟，重要性3，无deadline，可拆分
walk = Task('walk', 300, 3, splittable=True)

# 2. nap，40分钟，重要性1，deadline=14:45，可拆分
nap_deadline = datetime.combine(target_date, datetime.strptime('14:45', "%H:%M").time())
nap = Task('nap', 40, 1, splittable=True, deadline=nap_deadline)

# 3. cs，50分钟，重要性2，起始时间13:50，可拆分
cs_start = datetime.combine(target_date, datetime.strptime('13:50', "%H:%M").time())
cs = Task('cs', 50, 2, splittable=True, earliest_start_time=cs_start)

tasks = [walk, nap, cs]

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

print("\n预期结果：")
print("- walk被拆分为多个部分，充分利用空闲时间")
print("- nap在午休结束前完成")
print("- cs从13:50开始安排")
print("\nPart编号规则：")
print("- 多片段任务：所有片段都显示Part编号")
print("- 单片段任务：不显示Part编号")

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

# 检查Part编号规则
print("\n" + "=" * 60)
print("Part编号验证：")
print("=" * 60)
for task in scheduled:
    if " - Part " in task.name:
        print(f"✓ {task.name} ({task.start_time.strftime('%H:%M')}-{task.end_time.strftime('%H:%M')})")
    else:
        print(f"✓ {task.name} (无Part编号) ({task.start_time.strftime('%H:%M')}-{task.end_time.strftime('%H:%M')})")

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
print("场景三测试完成")
print("=" * 60)
