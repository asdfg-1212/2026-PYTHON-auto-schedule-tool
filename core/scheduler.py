# core/scheduler.py
"""
智能调度器模块
负责将任务列表智能地分配到可用时间段中
"""

from datetime import datetime, timedelta
from core.task import Task
from core.schedule import Schedule


class Scheduler:
    """
    智能任务调度器（单日版本）
    
    主要功能：
    1. 根据任务的重要性、截止时间进行排序
    2. 找到Schedule中的可用时间段（避开课程、吃饭等固定时间）
    3. 将任务分配到合适的时间段
    4. 支持任务拆分：如果任务时间长于某个空闲段，可拆分成多个子任务
    """
    
    @staticmethod
    def schedule_tasks(tasks, schedule, allow_split=True):
        """
        核心调度算法：将任务列表安排到当天日程中
        
        参数:
            tasks: Task对象列表
            schedule: Schedule对象
            allow_split: 是否允许拆分任务
            
        返回:
            (scheduled_tasks, failed_tasks): 一个元组，包含成功安排的任务列表和无法安排的任务列表
        """
        scheduled_tasks = []
        failed_tasks = []

        # 1. 对任务进行排序 (按重要性降序)
        sorted_tasks = sorted(tasks, key=lambda t: t.importance, reverse=True)

        # 2. 遍历排序后的任务
        for task in sorted_tasks:
            # 确定查找时间段的范围
            earliest_start = task.earliest_start_time if task.earliest_start_time else None
            latest_end = task.deadline if task.deadline else None

            # 尝试找到一个完整的时间段来容纳任务
            start_time = schedule.find_available_slot_in_range(
                task.estimated_time,
                earliest_start=earliest_start,
                latest_end=latest_end
            )

            if start_time:
                task.start_time = start_time
                task.end_time = start_time + task.estimated_time
                schedule.add_task(task)
                scheduled_tasks.append(task)
            elif allow_split:
                # 如果找不到完整时间段，并且允许拆分
                sub_tasks = Scheduler.split_and_schedule_task(task, schedule, earliest_start, latest_end)
                if sub_tasks:
                    scheduled_tasks.extend(sub_tasks)
                else:
                    failed_tasks.append(task) # 拆分后也无法安排
            else:
                # 如果不允许拆分，且找不到时间段，则任务失败
                failed_tasks.append(task)

        # 3. 打印无法安排的任务
        if failed_tasks:
            print("\n[Scheduler] 提示: 以下任务无法安排, 请考虑减少任务或调整日程。")
            for task in failed_tasks:
                print(f"- {task.name} (预计耗时: {task.estimated_time.total_seconds() / 60} 分钟)")
        
        return scheduled_tasks, failed_tasks

    @staticmethod
    def split_and_schedule_task(task, schedule, earliest_start=None, latest_end=None):
        """
        尝试将单个任务拆分并放入多个可用时间段

        参数:
            task: Task对象
            schedule: Schedule对象
            earliest_start: 最早开始时间
            latest_end: 最晚结束时间（截止时间）
        """
        remaining_time = task.estimated_time
        all_free_slots = schedule.get_all_free_slots()

        # 过滤时间段：只保留符合时间范围的空闲时间段
        filtered_slots = []
        for slot in all_free_slots:
            slot_start = slot['start']
            slot_end = slot['end']

            # 应用earliest_start限制
            if earliest_start and slot_end <= earliest_start:
                continue  # 这个时间段完全在最早开始时间之前
            if earliest_start and slot_start < earliest_start:
                slot_start = earliest_start  # 调整开始时间

            # 应用latest_end限制
            if latest_end and slot_start >= latest_end:
                continue  # 这个时间段完全在截止时间之后
            if latest_end and slot_end > latest_end:
                slot_end = latest_end  # 调整结束时间

            # 检查调整后的时间段是否仍然有效
            if slot_start < slot_end:
                filtered_slots.append({'start': slot_start, 'end': slot_end})

        sub_tasks = []
        part_num = 1

        for slot in filtered_slots:
            if remaining_time <= timedelta(minutes=0):
                break

            slot_duration = slot['end'] - slot['start']
            
            if slot_duration >= remaining_time:
                # 当前时间段足够容纳剩余任务
                sub_task_duration = remaining_time
                remaining_time = timedelta(minutes=0)
            else:
                # 当前时间段不够，只能放一部分
                sub_task_duration = slot_duration

            # 创建并添加子任务
            sub_task = Task(
                name=f"{task.name} - Part {part_num}",
                estimated_time=int(sub_task_duration.total_seconds() // 60),
                importance=task.importance,
                deadline=task.deadline,
                earliest_start_time=task.earliest_start_time,
                note=task.note
            )
            sub_task.start_time = slot['start']
            sub_task.end_time = slot['start'] + sub_task_duration
            
            schedule.add_task(sub_task)
            sub_tasks.append(sub_task)
            
            remaining_time -= sub_task_duration
            part_num += 1

        # 如果任务完全被拆分并安排，则返回子任务列表
        if remaining_time <= timedelta(minutes=0):
            return sub_tasks
        else:
            # 如果遍历完所有时间段后，任务仍未完全安排，则说明安排失败
            # 需要从schedule中移除已经添加的子任务
            for sub in sub_tasks:
                schedule.remove_task(sub)
            return []

    @staticmethod
    def split_task(task, max_duration):
        """
        将大任务拆分为多个小任务 (此函数在此版调度器中未直接使用，保留为工具函数)
        
        参数:
            task: Task对象
            max_duration: 单个时间段的最大时长 (timedelta)
        
        返回:
            拆分后的Task列表
        """
        sub_tasks = []
        total_time = task.estimated_time
        num_parts = int(total_time / max_duration)
        if total_time % max_duration > timedelta(0):
            num_parts += 1

        if num_parts <= 1:
            return [task]

        for i in range(num_parts):
            part_time = min(total_time, max_duration)
            sub_task = Task(
                name=f"{task.name} - Part {i+1}/{num_parts}",
                estimated_time=part_time,
                importance=task.importance,
                deadline=task.deadline,
                note=task.note
            )
            sub_tasks.append(sub_task)
            total_time -= part_time
        
        return sub_tasks


# 辅助函数（可选）
def calculate_priority(task):
    """
    计算任务优先级分数
    
    TODO: 你可以实现更复杂的优先级算法
    考虑因素：
    - 重要性（1-5）
    - 截止时间紧迫程度
    - 任务时长
    """
    pass
