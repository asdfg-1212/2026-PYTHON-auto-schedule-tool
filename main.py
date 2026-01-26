# main.py
"""
主程序入口
负责整合所有模块，驱动应用运行
"""

from datetime import date, datetime
from config.settings import Settings
from core.schedule import Schedule
from core.scheduler import Scheduler
from ui import cli

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

    # 3. 创建当天的日程表
    today = date.today()

    # 从配置直接构建今日作息（不每次询问）
    wake_time = datetime.strptime(settings.get('wake_up', '08:00'), "%H:%M").time()
    sleep_time = datetime.strptime(settings.get('sleep', '23:00'), "%H:%M").time()
    schedule = Schedule(date=today, start_time=datetime.combine(today, wake_time), end_time=datetime.combine(today, sleep_time))

    # 添加三餐/午休固定日程
    for rng, name in [
        (settings.get('breakfast', '07:40-08:00'), '早餐'),
        (settings.get('lunch', '12:00-13:40'), '午休'),
        (settings.get('dinner', '18:00-18:30'), '晚餐'),
    ]:
        if rng:
            start_str, end_str = rng.split('-')
            schedule.add_fixed_slot(
                datetime.combine(today, datetime.strptime(start_str, "%H:%M").time()),
                datetime.combine(today, datetime.strptime(end_str, "%H:%M").time()),
                name,
            )

    # 4. 仅加载课程等固定日程（避免重复添加三餐）
    cli.load_daily_fixed_slots(schedule, settings, include_meals=False)

    print("\n--- 今日固定日程已加载 ---")
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

    # 8. 显示最终的日程表
    print("\n--- ✨ 您今天的日程表已生成 ---")
    schedule.display()

if __name__ == "__main__":
    main()

