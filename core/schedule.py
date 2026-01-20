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

    def add_task(self, task):
        """
        添加一个已经计算好时间的任务到日程
        
        参数:
            task: Task对象 (必须包含 start_time 和 end_time)
        
        返回:
            True (成功) / False (失败)
        """
        if not hasattr(task, 'start_time') or not hasattr(task, 'end_time'):
            print("[Schedule] Error: 任务缺少 'start_time' 或 'end_time'。")
            return False

        # 检查时间是否可用
        if not self.is_time_available(task.start_time, task.end_time):
            # print(f"[Schedule] Debug: 时间段 {task.start_time.strftime('%H:%M')}-{task.end_time.strftime('%H:%M')} 不可用。")
            return False
        
        # 添加任务
        self.time_slots.append((task.start_time, task.end_time, task))
        self.time_slots.sort()
        return True

    def remove_task(self, task_to_remove):
        """从日程中移除一个任务"""
        self.time_slots = [
            (start, end, task) for start, end, task in self.time_slots 
            if task.id != task_to_remove.id
        ]

    def get_all_free_slots(self):
        """
        获取当天所有空闲的时间段
        
        返回:
            一个字典列表 [{'start': datetime, 'end': datetime}, ...]
        """
        all_slots = self.fixed_slots + self.time_slots
        all_slots.sort()

        free_slots = []
        current_time = self.start_time

        for slot_start, slot_end, _ in all_slots:
            if current_time < slot_start:
                free_slots.append({'start': current_time, 'end': slot_start})
            current_time = max(current_time, slot_end)
        
        if current_time < self.end_time:
            free_slots.append({'start': current_time, 'end': self.end_time})
            
        return free_slots

    def get_schedule(self):
        """获取所有已安排的任务"""
        return self.time_slots
    
    def display(self):
        """
        美观地显示日程表
        """
        print(f"\n{'='*60}")
        print(f"  日程安排：{self.date.strftime('%Y-%m-%d %A')}")
        print(f"{'='*60}\n")
        
        # 合并所有时间段
        all_slots = []
        
        for start, end, desc in self.fixed_slots:
            all_slots.append({'start': start, 'end': end, 'name': desc, 'type': "固定"})
        
        for start, end, task in self.time_slots:
            all_slots.append({'start': start, 'end': end, 'name': task.name, 'type': f"任务(重要性:{task.importance})"})
        
        # 排序
        all_slots.sort(key=lambda x: x['start'])

        if not all_slots:
            print("  >> 今天是自由的一天，没有安排！")
            return

        # 打印第一个活动前的空闲时间
        if all_slots[0]['start'] > self.start_time:
             print(f"{self.start_time.strftime('%H:%M')} - {all_slots[0]['start'].strftime('%H:%M')}  [空闲] ...")

        # 打印活动和活动间的空闲时间
        for i, slot in enumerate(all_slots):
            print(f"{slot['start'].strftime('%H:%M')} - {slot['end'].strftime('%H:%M')}  [{slot['type']}] {slot['name']}")
            
            # 检查与下一个活动之间的空闲
            if i + 1 < len(all_slots):
                next_slot = all_slots[i+1]
                if slot['end'] < next_slot['start']:
                    print(f"{slot['end'].strftime('%H:%M')} - {next_slot['start'].strftime('%H:%M')}  [空闲] ...")

        # 打印最后一个活动后的空闲时间
        if all_slots[-1]['end'] < self.end_time:
            print(f"{all_slots[-1]['end'].strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}  [空闲] ...")

        print(f"\n{'='*60}")

