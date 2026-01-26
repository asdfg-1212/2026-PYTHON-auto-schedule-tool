# main.py
"""
主程序入口
负责整合所有模块，驱动应用运行
"""

from datetime import date, datetime, timedelta
from config.settings import Settings
from core.schedule import Schedule
from core.scheduler import Scheduler
from ui import cli
from utils import parser

def main():
    """
    主函数
    """
    print("欢迎来到自动日程规划器！\nWelcome to the Auto Scheduler!")

    # 1. 初始化设置
    settings = Settings()

    # 2. 检查是否首次运行，如果是，则进行引导设置
    if settings.is_first_time():
        print("\n--- 首次运行设置 ---")
        settings = cli.first_time_setup()  # first_time_setup returns a Settings object

    # 3. 选择日期并创建日程表
    target_date = cli.choose_target_date()

    # 先尝试加载历史元信息
    date_key = target_date.isoformat()
    saved_meta, saved_entries = parser.load_date_data(date_key)

    wake_time = datetime.strptime(settings.get('wake_up', '08:00'), "%H:%M").time()
    sleep_time = datetime.strptime(settings.get('sleep', '23:00'), "%H:%M").time()

    # 如果有保存的元信息则覆盖默认作息
    wake_time = datetime.fromisoformat(saved_meta['start']).time() if saved_meta.get('start') else wake_time
    sleep_time = datetime.fromisoformat(saved_meta['end']).time() if saved_meta.get('end') else sleep_time

    schedule = Schedule(date=target_date, start_time=datetime.combine(target_date, wake_time), end_time=datetime.combine(target_date, sleep_time))

    # 使用保存的餐段，否则用配置
    meal_sources = saved_meta if saved_meta else settings.settings
    for key, name, fallback in [
        ('breakfast', '早餐', settings.get('breakfast', '07:40-08:00')),
        ('lunch', '午休', settings.get('lunch', '12:00-13:40')),
        ('dinner', '晚餐', settings.get('dinner', '18:00-18:30')),
    ]:
        rng = meal_sources.get(key, fallback)
        if rng:
            start_str, end_str = rng.split('-')
            schedule.add_fixed_slot(
                datetime.combine(target_date, datetime.strptime(start_str, "%H:%M").time()),
                datetime.combine(target_date, datetime.strptime(end_str, "%H:%M").time()),
                name,
            )

    # 4. 仅加载课程等固定日程（避免重复添加三餐）
    cli.load_daily_fixed_slots(schedule, settings, include_meals=False)

    # 4.5 加载已保存的任务（如果有），并询问是否保留
    if cli.ask_keep_previous_tasks(saved_entries):
        for task, start_dt, end_dt in saved_entries:
            task.start_time = start_dt
            task.end_time = end_dt
            schedule.add_task(task)

    print("\n--- 固定日程与历史任务已加载 ---")
    schedule.display()

    # 5. 询问是否修改当日作息时间
    cli.ask_modify_today_schedule(schedule, settings)

    # 如果修改了，重新显示
    schedule.display()

    # 6. 引导用户输入今日任务
    print("\n--- 请输入今天的任务 ---")
    tasks_to_schedule = cli.add_multiple_tasks()

    if not tasks_to_schedule:
        print("\n今天没有新任务，祝你轻松愉快！")
        return

    # 7. 调用调度器安排任务
    print("\n正在为您智能安排日程...")
    scheduler = Scheduler()
    scheduled_tasks, failed_tasks = scheduler.schedule_tasks(tasks_to_schedule, schedule)

    # 8. 显示最终的日程表并保存
    print("\n--- ✨ 您今天的日程表已生成 ---")
    schedule.display()

    # 记录当日元信息（起止时间与餐段）
    meta_to_save = {
        'start': schedule.start_time.isoformat(),
        'end': schedule.end_time.isoformat(),
    }
    # 提取餐段
    for slot_start, slot_end, desc in schedule.fixed_slots:
        if desc in ['早餐', '午休', '晚餐']:
            key = 'breakfast' if desc == '早餐' else 'lunch' if desc == '午休' else 'dinner'
            meta_to_save[key] = f"{slot_start.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"

    parser.save_date_entries(date_key, schedule, meta=meta_to_save)

if __name__ == "__main__":
    main()

