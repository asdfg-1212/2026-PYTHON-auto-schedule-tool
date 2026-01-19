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
            成功安排的任务数量
        
        TODO: 你需要实现以下逻辑：
        1. 对任务进行排序
           - 重要性高的优先（importance降序）
           - 截止时间近的优先
        
        2. 遍历排序后的任务
           - 尝试找到可用时间段
           - 如果任务太长且allow_split=True，考虑拆分
           - 调用schedule.add_task()添加任务
        
        3. 记录无法安排的任务
        
        4. 返回成功安排的任务数量
        
        示例：
        sorted_tasks = sorted(tasks, 
            key=lambda t: (-t.importance, t.deadline or datetime.max))
        """
        scheduled_count = 0
        failed_tasks = []
        
        # TODO: 实现排序
        # sorted_tasks = sorted(...)
        
        # TODO: 遍历任务
        # for task in sorted_tasks:
        #     if schedule.add_task(task):
        #         scheduled_count += 1
        #     elif allow_split:
        #         # 尝试拆分任务
        #         拆分逻辑...
        #     else:
        #         failed_tasks.append(task)
        
        # TODO: 打印结果
        # if failed_tasks:
        #     print(f"⚠️ 有{len(failed_tasks)}个任务无法安排")
        
        return scheduled_count
    
    @staticmethod
    def split_task(task, max_duration):
        """
        将大任务拆分为多个小任务
        
        参数:
            task: Task对象
            max_duration: 单个时间段的最大时长 (timedelta)
        
        返回:
            拆分后的Task列表
        
        TODO: 你可以实现（可选，进阶功能）：
        1. 计算需要拆分成几部分
        2. 创建多个子任务（名称如"任务名-part1", "任务名-part2"）
        3. 返回子任务列表
        """
        pass


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
