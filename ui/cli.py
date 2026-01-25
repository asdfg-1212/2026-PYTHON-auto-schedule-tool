# ui/cli.py
"""
命令行交互界面模块
提供用户友好的问答式交互
"""

from datetime import datetime, timedelta, time
from core.task import Task
from config.settings import Settings


def show_welcome():
# ...existing code...
    print()


def get_time_input(prompt):
    """获取时间输入并验证 (HH:MM)"""
    while True:
        time_str = input(prompt).strip()
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            print("❌ 格式错误，请输入 HH:MM 格式的时间 (例如: 08:00)")

def get_time_range_input(prompt):
    """获取时间范围输入并验证 (HH:MM-HH:MM)"""
    while True:
        range_str = input(prompt).strip()
        try:
            start_str, end_str = range_str.split('-')
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
            if start_time >= end_time:
                print("❌ 结束时间必须晚于开始时间")
                continue
            return f"{start_str}-{end_str}"
        except ValueError:
            print("❌ 格式错误，请输入 HH:MM-HH:MM 格式的时间范围 (例如: 08:00-10:00)")

def first_time_setup():
    """
    首次使用配置向导
    设置课表和默认作息时间
    """
    print("\n" + "="*60)
    print("  欢迎使用智能日程安排工具！")
    print("  首次使用，我们先来配置您的课表和默认作息时间。")
    print("="*60)
    
    settings = Settings()
    
    # 1. 设置作息时间
    print("\n--- 1. 设置默认作息时间 ---")
    
    # 封装一个确认修改的逻辑
    def confirm_and_set_time(key, prompt_text, input_func):
        default_value = settings.DEFAULT_SETTINGS.get(key)
        change = input(f"默认 {prompt_text} 为 {default_value}，是否修改？ (y/n, 默认n): ").strip().lower()
        if change == 'y':
            new_value = input_func(f"请输入新的 {prompt_text}: ")
            if hasattr(new_value, 'strftime'): # 如果是time对象
                 settings.set(key, new_value.strftime('%H:%M'))
            else: # 如果是字符串
                 settings.set(key, new_value)
        else:
            settings.set(key, default_value)

    confirm_and_set_time('wake_up', '起床时间', get_time_input)
    confirm_and_set_time('sleep', '睡觉时间', get_time_input)
    confirm_and_set_time('breakfast', '早餐时间范围', get_time_range_input)
    confirm_and_set_time('lunch', '午餐时间范围', get_time_range_input)
    confirm_and_set_time('dinner', '晚餐时间范围', get_time_range_input)

    # 2. 设置课表
    # ... (课表设置部分保持不变)
    print("\n--- 2. 设置每周课表 ---")
    print("请输入课程信息，格式为：'开始时间-结束时间 课程名'")
    print("例如：'08:00-10:00 高等数学'")
    print("如果一天有多门课，用英文逗号 ',' 分隔。没课请直接按回车。")
    
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    for i, day_name in enumerate(weekdays):
        while True:
            try:
                courses_input = input(f"\n请输入 {day_name} 的课程: ").strip()
                if not courses_input:
                    settings.setup_course_schedule(i, [])
                    break
                
                courses_list = []
                for course_str in courses_input.split(','):
                    time_part, name_part = course_str.strip().split(' ', 1)
                    start_str, end_str = time_part.split('-')
                    # 简单验证
                    datetime.strptime(start_str, "%H:%M")
                    datetime.strptime(end_str, "%H:%M")
                    courses_list.append((start_str, end_str, name_part.strip()))
                
                settings.setup_course_schedule(i, courses_list)
                break
            except Exception as e:
                print(f"❌ 格式错误，请重新输入。错误: {e}")

    # 3. 标记完成
    settings.mark_setup_complete()
    print("\n🎉 首次配置完成！您的设置已保存。")
    return settings

def load_daily_fixed_slots(schedule, settings):
    """
    从配置加载某一天的固定时间段（课程、吃饭）并直接添加到schedule对象中
    
    参数:
        schedule: Schedule 对象，将把固定日程添加到此对象
        settings: Settings 对象
    """
    # 从schedule对象中获取日期
    date = schedule.date
    
    # 加载吃饭时间
    meal_keys = ['breakfast', 'lunch', 'dinner']
    meal_names = ['早餐', '午餐', '晚餐']
    for key, name in zip(meal_keys, meal_names):
        time_range = settings.get(key)
        if time_range:
            start_str, end_str = time_range.split('-')
            start_dt = datetime.combine(date, datetime.strptime(start_str, "%H:%M").time())
            end_dt = datetime.combine(date, datetime.strptime(end_str, "%H:%M").time())
            schedule.add_fixed_slot(start_dt, end_dt, name)
            
    # 加载当天课程
    weekday = date.weekday()  # 0=周一, 6=周日
    courses = settings.get_courses_for_day(weekday)
    for start_str, end_str, course_name in courses:
        start_dt = datetime.combine(date, datetime.strptime(start_str, "%H:%M").time())
        end_dt = datetime.combine(date, datetime.strptime(end_str, "%H:%M").time())
        schedule.add_fixed_slot(start_dt, end_dt, f"课程: {course_name}")


def ask_modify_today_schedule(schedule, settings):
    """
    询问用户是否要修改当日的作息时间
    如果修改，则清空schedule的固定时间段并重新加载

    参数:
        schedule: Schedule 对象
        settings: Settings 对象
    """
    print("\n>>> 是否需要修改今日的作息时间？")
    modify = input("请输入 (y/n, 默认n): ").strip().lower()

    if modify != 'y':
        return

    print("\n--- 修改今日作息时间 ---")
    print("请选择要修改的项目（输入对应数字，多个用逗号分隔，如: 1,2）：")
    print("1. 早餐时间")
    print("2. 午餐时间")
    print("3. 晚餐时间")

    choice = input("请输入选择: ").strip()
    if not choice:
        return

    # 解析选择
    choices = [c.strip() for c in choice.split(',')]

    date = schedule.date
    meal_mapping = {
        '1': ('breakfast', '早餐时间范围'),
        '2': ('lunch', '午餐时间范围'),
        '3': ('dinner', '晚餐时间范围')
    }

    # 临时存储修改后的时间
    modified_meals = {}

    for c in choices:
        if c in meal_mapping:
            key, name = meal_mapping[c]
            current_value = settings.get(key)
            print(f"\n当前 {name}: {current_value}")
            new_value = get_time_range_input(f"请输入新的 {name} (HH:MM-HH:MM): ")
            modified_meals[key] = new_value

    if not modified_meals:
        print("未进行任何修改。")
        return

    # 清空现有的固定时间段
    schedule.fixed_slots = []

    # 重新加载，使用修改后的值
    meal_keys = ['breakfast', 'lunch', 'dinner']
    meal_names = ['早餐', '午餐', '晚餐']
    for key, name in zip(meal_keys, meal_names):
        # 如果用户修改了这一项，使用新值；否则使用配置中的值
        time_range = modified_meals.get(key, settings.get(key))
        if time_range:
            start_str, end_str = time_range.split('-')
            start_dt = datetime.combine(date, datetime.strptime(start_str, "%H:%M").time())
            end_dt = datetime.combine(date, datetime.strptime(end_str, "%H:%M").time())
            schedule.add_fixed_slot(start_dt, end_dt, name)

    # 重新加载课程（课程不变）
    weekday = date.weekday()
    courses = settings.get_courses_for_day(weekday)
    for start_str, end_str, course_name in courses:
        start_dt = datetime.combine(date, datetime.strptime(start_str, "%H:%M").time())
        end_dt = datetime.combine(date, datetime.strptime(end_str, "%H:%M").time())
        schedule.add_fixed_slot(start_dt, end_dt, f"课程: {course_name}")

    print("\n✓ 今日作息时间已更新！")


def create_task_from_input():
# ...existing code...
    print("\n--- 添加新任务 ---")
    
    name = input("任务名称: ").strip()
    if not name:
        print("任务名称不能为空！")
        return None

    while True:
        try:
            estimated_time = int(input("预计用时（分钟）: "))
            if estimated_time > 0:
                break
            print("❌ 时间必须大于0！")
        except ValueError:
            print("❌ 请输入有效的数字！")

    while True:
        try:
            importance = int(input("重要程度 (1-5, 5为最重要): "))
            if 1 <= importance <= 5:
                break
            print("❌ 请输入1-5之间的数字！")
        except ValueError:
            print("❌ 请输入有效的数字！")

    # 获取起始时间（作为任务的实际开始时间）
    earliest_start_time = None
    earliest_start_str = input("起始时间 (格式: HH:MM, 可选, 回车跳过): ").strip()
    if earliest_start_str:
        try:
            # 将时间与当前日期组合
            time_obj = datetime.strptime(earliest_start_str, "%H:%M").time()
            today = datetime.now().date()
            earliest_start_time = datetime.combine(today, time_obj)
        except ValueError:
            print("⚠️ 起始时间格式错误，已忽略。")

    # 获取截止时间
    deadline = None
    deadline_str = input("截止时间 (格式: HH:MM, 可选, 回车跳过): ").strip()
    if deadline_str:
        try:
            # 将时间与当前日期组合
            time_obj = datetime.strptime(deadline_str, "%H:%M").time()
            today = datetime.now().date()
            deadline = datetime.combine(today, time_obj)
        except ValueError:
            print("⚠️ 截止时间格式错误，已忽略。")


    note = input("备注 (可选, 回车跳过): ").strip()
    
    print(f"✓ 任务 '{name}' 已创建")
    return Task(name=name, estimated_time=estimated_time, importance=importance, deadline=deadline, earliest_start_time=earliest_start_time, note=note)


def add_multiple_tasks():
# ...existing code...
    tasks = []
    
    while True:
        task = create_task_from_input()
        if task:
            tasks.append(task)
        
        continue_add = input("\n是否继续添加任务？(y/n, 默认y): ").strip().lower()
        if continue_add == 'n':
            break
            
    return tasks


def display_schedule(schedule):
# ...existing code...
    """
    美观地显示某一天的日程
    
    参数:
        schedule: Schedule对象
    """
    schedule.display()


def show_menu():
# ...existing code...
    print("\n--- 主菜单 ---")
    print("1. 创建新日程")
    print("2. 查看日程 (功能待开发)")
    print("3. 退出")
    
    choice = input("请输入选项: ").strip()
    return choice


# 更多辅助函数...
# 你可以根据需要添加更多函数
