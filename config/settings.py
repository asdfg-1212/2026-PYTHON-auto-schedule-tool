# config/settings.py
"""
配置文件模块
管理用户偏好设置，如默认作息时间、课表等
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
        'wake_up': '07:20',
        'sleep': '23:40',
        'breakfast': '07:40-08:00',
        'lunch': '12:00-13:40',
        'dinner': '18:00-18:30',
        
        # 课表（每周固定）
        # 格式：{星期几: [(开始时间, 结束时间, 课程名), ...]}
        # 星期一=0, 星期日=6
        'course_schedule': {
            # 示例：周一 8:00-10:00 有课
            # '0': [('08:00', '10:00', '高等数学')],
        },
        
        # 是否已完成首次配置
        'first_time_setup_done': False,
    }
    
    def __init__(self, config_file='config/user_config.json'):
        """初始化Settings对象"""
        self.config_file = config_file
        self.settings = self.load_settings()
    
    def load_settings(self):
        """
        从JSON文件加载设置
        
        实现思路：
        1. 检查配置文件是否存在
        2. 如果存在，读取JSON并返回
        3. 如果不存在，返回默认设置
        """
        # 检查文件是否存在
        if not os.path.exists(self.config_file):
            # 第一次使用，返回默认设置
            print("未找到配置文件，使用默认设置")
            return self.DEFAULT_SETTINGS.copy()
        
        try:
            # 打开并读取JSON文件
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                print(f"成功加载配置文件: {self.config_file}")
                return loaded_settings
        except Exception as e:
            # 如果文件损坏或格式错误，使用默认设置
            print(f"配置文件读取失败: {e}，使用默认设置")
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """
        保存设置到JSON文件
        
        实现思路：
        1. 确保config目录存在
        2. 将settings字典写入JSON文件
        """
        try:
            # 获取文件所在目录（如 "config"）
            config_dir = os.path.dirname(self.config_file)
            
            # 如果目录不存在，创建它
            # exist_ok=True 表示如果目录已存在也不报错
            if config_dir:  # 防止空字符串
                os.makedirs(config_dir, exist_ok=True)
            
            # 打开文件并写入JSON
            # indent=4 让JSON格式更美观（缩进4个空格）
            # ensure_ascii=False 支持中文字符
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            
            print(f"配置已保存到: {self.config_file}")
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get(self, key, default=None):
        """
        获取某个设置项
        
        参数:
            key: 配置项名称
            default: 默认值（如果key不存在）
        
        返回:
            配置项的值
        """
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """
        设置某个配置项并保存
        
        参数:
            key: 配置项名称（如 'wake_up', 'sleep'）
            value: 配置项的值
        """
        # 更新配置
        self.settings[key] = value
        # 立即保存到文件
        self.save_settings()
    
    def setup_course_schedule(self, weekday, courses):
        """
        设置某一天的课表
        
        参数:
            weekday: 星期几 (0-6, 0是周一)
            courses: 课程列表 [(开始时间, 结束时间, 课程名), ...]
        
        示例:
            settings.setup_course_schedule(0, [
                ('08:00', '10:00', '高等数学'),
                ('14:00', '16:00', 'Python编程')
            ])
        """
        # 确保course_schedule字段存在
        if 'course_schedule' not in self.settings:
            self.settings['course_schedule'] = {}
        
        # 将星期几转换为字符串（JSON的key必须是字符串）
        weekday_str = str(weekday)
        
        # 更新该天的课表
        self.settings['course_schedule'][weekday_str] = courses
        
        # 保存
        self.save_settings()
        
        print(f"已设置星期{['一', '二', '三', '四', '五', '六', '日'][weekday]}的课表")
    
    def get_courses_for_day(self, weekday):
        """
        获取某一天的课表
        
        参数:
            weekday: 星期几 (0-6)
        
        返回:
            课程列表 [(开始时间, 结束时间, 课程名), ...]
        """
        return self.settings.get('course_schedule', {}).get(str(weekday), [])
    
    def mark_setup_complete(self):
        """标记首次配置已完成"""
        self.set('first_time_setup_done', True)
    
    def is_first_time(self):
        """检查是否首次使用"""
        return not self.get('first_time_setup_done', False)


# 示例使用：
if __name__ == "__main__":
    # 测试代码
    settings = Settings()
    print(f"起床时间: {settings.get('wake_up')}")
    print(f"是否首次使用: {settings.is_first_time()}")
