# test_settings.py
"""测试 Settings 类"""

from config.settings import Settings

# 创建Settings对象
settings = Settings()

print("\n=== 测试1：读取默认设置 ===")
print(f"起床时间: {settings.get('wake_up')}")
print(f"睡觉时间: {settings.get('sleep')}")
print(f"是否首次使用: {settings.is_first_time()}")

print("\n=== 测试2：设置课表 ===")
# 设置周一的课表
settings.setup_course_schedule(0, [
    ('08:00', '10:00', '高等数学'),
    ('14:00', '16:00', 'Python编程'),
    ('18:30', '20:30', '大学英语')
])

# 设置周三的课表
settings.setup_course_schedule(2, [
    ('08:00', '10:00', '线性代数'),
])

print("\n=== 测试3：读取课表 ===")
monday_courses = settings.get_courses_for_day(0)
print(f"周一课表: {monday_courses}")

wednesday_courses = settings.get_courses_for_day(2)
print(f"周三课表: {wednesday_courses}")

print("\n=== 测试4：修改作息时间 ===")
settings.set('wake_up', '06:30')
settings.set('sleep', '23:00')
print(f"新的起床时间: {settings.get('wake_up')}")

print("\n=== 测试5：标记首次配置完成 ===")
settings.mark_setup_complete()
print(f"是否首次使用: {settings.is_first_time()}")

print("\n✅ 所有测试完成！")
print(f"配置文件保存在: {settings.config_file}")
print("你可以打开这个文件查看保存的内容")
