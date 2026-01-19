# core/schedule.py
"""
单日日程表模块
管理一天的固定时间段（课程、吃饭）和任务时间段
"""

from datetime import datetime, timedelta


class Schedule:
    """
    单日日程表
    
    功能：
    1. 管理固定时间段（课程、吃饭、睡觉）
    2. 管理任务时间段
    3. 检查时间冲突
    4. 自动查找可用时间段
    """
    
    def __init__(self, date, start_time=None, end_time=None):
        """
        初始化日程表
        
        参数:
            date: 日期 (datetime.date)
            start_time: 开始时间（默认8:00）
            end_time: 结束时间（默认23:00）
        """
        self.date = date
        
        # 默认工作时间：8:00 - 23:00
        if start_time is None:
            start_time = datetime.combine(date, datetime.min.time().replace(hour=8))
        if end_time is None:
            end_time = datetime.combine(date, datetime.min.time().replace(hour=23))
            
        self.start_time = start_time
        self.end_time = end_time
        
        self.fixed_slots = []  # 固定时间段：[(start, end, description), ...]
        self.time_slots = []   # 任务时间段：[(start, end, task), ...]

    def add_fixed_slot(self, start_time, end_time, description):
        """
        添加固定时间段（课程、吃饭等）
        
        TODO: 已实现，你可以直接使用
        """
        self.fixed_slots.append((start_time, end_time, description))
        self.fixed_slots.sort()

    def is_time_available(self, start_time, end_time):
        """
        检查时间段是否可用（没有冲突）
        
        返回: True/False
        
        TODO: 已实现，你可以直接使用
        """
        # 检查是否超出范围
        if start_time < self.start_time or end_time > self.end_time:
            return False
        
        # 检查与固定时间段冲突
        for slot_start, slot_end, _ in self.fixed_slots:
            if self._has_overlap(start_time, end_time, slot_start, slot_end):
                return False
        
        # 检查与已安排任务冲突
        for slot_start, slot_end, _ in self.time_slots:
            if self._has_overlap(start_time, end_time, slot_start, slot_end):
                return False
        
        return True
    
    def _has_overlap(self, start1, end1, start2, end2):
        """判断两个时间段是否重叠"""
        return start1 < end2 and start2 < end1

    def find_available_slot(self, duration):
        """
        找到第一个能容纳指定时长的空闲时间段
        
        参数:
            duration: timedelta对象，需要的时长
        
        返回:
            可用的开始时间（datetime），找不到返回None
        
        TODO: 已实现，你可以直接使用
        """
        current = self.start_time
        step = timedelta(minutes=15)  # 每15分钟检查一次
        
        while current + duration <= self.end_time:
            end = current + duration
            if self.is_time_available(current, end):
                return current
            current += step
        
        return None

    def add_task(self, task, start_time=None):
        """
        添加任务到日程
        
        参数:
            task: Task对象
            start_time: 指定开始时间，None则自动查找
        
        返回:
            True (成功) / False (失败)
        
        TODO: 已实现，你可以直接使用
        """
        if start_time is None:
            # 自动查找可用时间
            start_time = self.find_available_slot(task.estimated_time)
            if start_time is None:
                return False  # 没有可用时间
        
        end_time = start_time + task.estimated_time
        
        # 检查时间是否可用
        if not self.is_time_available(start_time, end_time):
            return False
        
        # 添加任务
        self.time_slots.append((start_time, end_time, task))
        self.time_slots.sort()
        return True
    
    def get_available_slots(self):
        """
        获取所有空闲时间段
        
        返回: [(start, end, duration_minutes), ...]
        
        TODO: 你可以实现（可选，用于显示空闲时间）
        """
        pass

    def get_schedule(self):
        """获取所有已安排的任务"""
        return self.time_slots
    
    def display(self):
        """
        美观地显示日程表
        
        TODO: 已实现，你可以直接使用
        """
        print(f"\n{'='*60}")
        print(f"  日程安排：{self.date.strftime('%Y-%m-%d %A')}")
        print(f"{'='*60}\n")
        
        # 合并所有时间段
        all_slots = []
        
        for start, end, desc in self.fixed_slots:
            all_slots.append((start, end, desc, "固定"))
        
        for start, end, task in self.time_slots:
            all_slots.append((start, end, task.name, f"任务(重要性:{task.importance})"))
        
        # 排序并显示
        all_slots.sort()
        if not all_slots:
            print("  （暂无安排）")
        else:
            for start, end, name, type_info in all_slots:
                print(f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}  "
                      f"[{type_info}] {name}")

