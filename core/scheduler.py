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
        
        新策略（按deadline分段调度）：
        1. 有起始时间的任务：严格按时间锁定
        2. 收集所有deadline时间点，将一天分成多个时间段
        3. 在每个时间段内：
           - 必须在该段deadline前完成的任务必须完成
           - 其他任务按重要性参与调度
        4. 从早到晚按重要性填充

        参数:
            tasks: Task对象列表
            schedule: Schedule对象
            allow_split: 是否允许拆分任务
            
        返回:
            (scheduled_tasks, failed_tasks): 一个元组，包含成功安排的任务列表和无法安排的任务列表
        """
        scheduled_tasks = []
        failed_tasks = []

        # 跟踪每个任务的剩余时间
        task_remaining_time = {task.id: task.estimated_time for task in tasks}
        task_parts_count = {task.id: 0 for task in tasks}

        # 第一步：处理有起始时间的任务（严格锁定）
        tasks_with_start = [t for t in tasks if t.earliest_start_time]
        for task in sorted(tasks_with_start, key=lambda t: t.earliest_start_time):
            start = task.earliest_start_time
            end = start + task.estimated_time

            if schedule.is_time_available(start, end):
                task.start_time = start
                task.end_time = end
                schedule.add_task(task)
                scheduled_tasks.append(task)
                task_remaining_time[task.id] = timedelta(0)

        # 第二步：收集所有deadline，按时间排序
        deadlines = []
        for task in tasks:
            if task.deadline and task_remaining_time[task.id] > timedelta(0):
                deadlines.append(task.deadline)

        deadlines = sorted(set(deadlines))  # 去重并排序

        # 第三步：按deadline分段处理
        free_slots = schedule.get_all_free_slots()

        for slot in free_slots:
            slot_start = slot['start']
            slot_end = slot['end']

            # 找到当前slot内的所有deadline分段点
            segment_points = [slot_start]
            for dl in deadlines:
                if slot_start < dl < slot_end:
                    segment_points.append(dl)
            segment_points.append(slot_end)

            # 处理每个子段
            for i in range(len(segment_points) - 1):
                segment_start = segment_points[i]
                segment_end = segment_points[i + 1]
                current_time = segment_start

                while current_time < segment_end:
                    # 在当前段内选择任务
                    best_task = None

                    # 收集可以在当前段调度的任务
                    available_tasks = []
                    must_complete_tasks = []  # 必须在当前段完成的任务

                    for task in tasks:
                        if task_remaining_time[task.id] <= timedelta(minutes=0):
                            continue

                        # 检查任务是否可以在当前段调度
                        # 1. 有deadline的任务
                        if task.deadline:
                            # 如果deadline是当前段的结束点，必须在此段完成
                            if task.deadline == segment_end:
                                must_complete_tasks.append(task)
                            # 如果deadline在当前段之后，可以参与调度
                            elif task.deadline > segment_end:
                                available_tasks.append(task)
                            # 如果deadline已过，跳过
                            else:
                                continue
                        else:
                            # 无deadline的任务可以参与调度
                            available_tasks.append(task)

                    # 计算must_complete任务需要的总时间
                    must_complete_total_time = timedelta(0)
                    for task in must_complete_tasks:
                        must_complete_total_time += task_remaining_time[task.id]

                    # 计算当前段剩余时间
                    remaining_time_in_segment = segment_end - current_time

                    # 计算可以分配给其他任务的时间（需要预留must_complete的时间）
                    available_for_others = remaining_time_in_segment - must_complete_total_time

                    # 选择任务逻辑
                    # 1. 如果must_complete任务快没时间了，优先安排
                    must_complete_tasks.sort(key=lambda t: t.importance, reverse=True)

                    for task in must_complete_tasks:
                        # 计算该任务最晚开始时间
                        latest_start = segment_end - task_remaining_time[task.id]

                        # 如果已经到了最晚开始时间，必须立即安排
                        if current_time >= latest_start:
                            best_task = task
                            break

                    # 2. 如果没有紧急的must_complete任务，按重要性选择
                    if not best_task:
                        all_candidates = must_complete_tasks + available_tasks
                        all_candidates.sort(key=lambda t: t.importance, reverse=True)

                        for task in all_candidates:
                            # 如果是must_complete任务，直接选择
                            if task in must_complete_tasks:
                                best_task = task
                                break
                            # 如果是available任务，检查是否还有空间（需要预留must_complete时间）
                            elif available_for_others > timedelta(minutes=0):
                                best_task = task
                                break

                    if not best_task:
                        break  # 没有可调度的任务

                    # 计算填充时间
                    available_time = segment_end - current_time
                    fill_duration = min(task_remaining_time[best_task.id], available_time)

                    # 如果任务在must_complete中，确保能在segment_end前完成
                    if best_task in must_complete_tasks:
                        # 不能超过deadline
                        time_until_deadline = best_task.deadline - current_time
                        fill_duration = min(fill_duration, time_until_deadline)
                    else:
                        # 如果是available任务，不能占用must_complete的预留时间
                        fill_duration = min(fill_duration, available_for_others)

                    if fill_duration <= timedelta(minutes=0):
                        break

                    # 创建任务片段
                    task_parts_count[best_task.id] += 1
                    part_num = task_parts_count[best_task.id]

                    if task_remaining_time[best_task.id] > fill_duration:
                        task_name = f"{best_task.name} - Part {part_num}"
                    else:
                        task_name = f"{best_task.name} - Part {part_num}" if part_num > 1 else best_task.name

                    sub_task = Task(
                        name=task_name,
                        estimated_time=int(fill_duration.total_seconds() / 60),
                        importance=best_task.importance,
                        deadline=best_task.deadline,
                        earliest_start_time=None,
                        note=best_task.note
                    )
                    sub_task.start_time = current_time
                    sub_task.end_time = current_time + fill_duration

                    if schedule.add_task(sub_task):
                        scheduled_tasks.append(sub_task)
                        task_remaining_time[best_task.id] -= fill_duration
                        current_time += fill_duration
                    else:
                        break

        # 检查失败的任务
        for task in tasks:
            if task_remaining_time[task.id] > timedelta(minutes=0):
                failed_tasks.append(task)

        if failed_tasks:
            print("\n[Scheduler] 提示: 以下任务无法完全安排:")
            for task in failed_tasks:
                remaining_min = task_remaining_time[task.id].total_seconds() / 60
                total_min = task.estimated_time.total_seconds() / 60
                if remaining_min < total_min:
                    print(f"- {task.name} (部分完成，还剩 {remaining_min:.0f}/{total_min:.0f} 分钟)")
                else:
                    print(f"- {task.name} (完全未安排，需要 {total_min:.0f} 分钟)")

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
                estimated_time=int(sub_task_duration.total_seconds() / 60),
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
