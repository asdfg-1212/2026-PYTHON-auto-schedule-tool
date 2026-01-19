# config/settings.py
"""
配置文件模块
管理用户偏好设置，如默认作息时间、默认时间段等
"""

import json
import os
from datetime import time


class Settings:
    """
    用户设置类
    存储课表和作息时间配置（首次使用时设置，长期有效）
    """
    
    DEFAULT_SETTINGS = {
        # 作息时间
        'wake_up': '07:00',
        'sleep': '23:00',
        'breakfast': '07:30-08:00',
        'lunch': '12:00-13:00',
        'dinner': '18:00-19:00',
        
        # 课表（每周固定）
        # 格式：{星期几: [(开始时间, 结束时间, 课程名), ...]}
        # 星期一=0, 星期日=6
        'course_schedule': {
            # 示例：周一 8:00-10:00 有课
            # 0: [('08:00', '10:00', '高等数学')],
        },
        
        # 是否已完成首次配置
        'first_time_setup_done': False,
    }
    
    def __init__(self, config_file='config/user_config.json'):
        self.config_file = config_file
        self.settings = self.load_settings()
    
    def load_settings(self):
        """
        从JSON文件加载设置
        
        TODO: 你需要实现：
        1. 检查配置文件是否存在
        2. 如果存在，读取JSON并返回
        3. 如果不存在，返回DEFAULT_SETTINGS
        
        提示：使用 os.path.exists() 和 json.load()
        """
        # TODO: 实现加载逻辑
        return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """
        保存设置到JSON文件
        
        TODO: 你需要实现：
        1. 创建config目录（如果不存在）
        2. 将self.settings写入JSON文件
        
        提示：使用 os.makedirs() 和 json.dump()
        """
        # TODO: 实现保存逻辑
        pass
    
    def get(self, key, default=None):
        """获取某个设置项"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """
        设置某个配置项
        
        TODO: 你需要实现：
        1. 更新self.settings[key] = value
        2. 调用save_settings()保存
        """
        # TODO: 实现设置逻辑
        pass
    
    def setup_course_schedule(self, weekday, courses):
        """
        设置某一天的课表
        
        参数:
            weekday: 星期几 (0-6, 0是周一)
            courses: 课程列表 [(开始时间, 结束时间, 课程名), ...]
        
        TODO: 你需要实现：
        1. 验证时间格式
        2. 更新 self.settings['course_schedule'][weekday]
        3. 保存设置
        """
        pass
    
    def get_courses_for_day(self, weekday):
        """
        获取某一天的课表
        
        参数:
            weekday: 星期几 (0-6)
        
        返回:
            课程列表 [(开始时间, 结束时间, 课程名), ...]
        
        TODO: 你需要实现：
        从 self.settings['course_schedule'] 获取对应星期的课程
        """
        return self.settings.get('course_schedule', {}).get(str(weekday), [])
    
    def mark_setup_complete(self):
        """标记首次配置已完成"""
        self.set('first_time_setup_done', True)
    
    def is_first_time(self):
        """检查是否首次使用"""
        return not self.get('first_time_setup_done', False)


# 示例使用：
# settings = Settings()
# wake_up_time = settings.get('default_wake_up')
# settings.set('schedule_days', 7)
