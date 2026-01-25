# main.py
"""
主程序入口
负责整合所有模块，驱动应用运行
"""

from datetime import date
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
    user_config = settings.settings
    
    schedule = Schedule(
        date=today,
        start_time=user_config.get('wake_up_time'),
        end_time=user_config.get('sleep_time')
    )
    
    # 4. 加载当天的固定日程（课程、午餐、晚餐）
    cli.load_daily_fixed_slots(schedule, settings)
    
    print("\n--- 今日固定日程已加载 ---")
    schedule.display()
    
    # 5. 询问是否修改当日作息时间
    cli.ask_modify_today_schedule(schedule, settings)

    # 如果修改了，重新显示
    if len(schedule.fixed_slots) > 0:
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

