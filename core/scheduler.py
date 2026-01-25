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
                    # 收集可以在当前段调度的任务
                    available_tasks = []
                    must_complete_tasks = []  # deadline在当前段结束的任务

                    for task in tasks:
                        if task_remaining_time[task.id] <= timedelta(minutes=0):
                            continue

                        # 有deadline的任务
                        if task.deadline:
                            if task.deadline == segment_end:
                                must_complete_tasks.append(task)
                            elif task.deadline > segment_end:
                                available_tasks.append(task)
                            # deadline已过的任务跳过
                        else:
                            # 无deadline的任务
                            available_tasks.append(task)

                    # === 前瞻性检查：计算有deadline的任务后续可用时间 ===
                    tasks_need_space = []  # 需要在当前段预留空间的任务

                    for task in available_tasks:
                        if task.deadline:
                            # 计算从下一个时间点到deadline之间的可用时间
                            future_available_time = timedelta(0)

                            # 遍历当前slot的后续segments
                            for j in range(i + 1, len(segment_points) - 1):
                                seg_start = segment_points[j]
                                seg_end = segment_points[j + 1]

                                if seg_start >= task.deadline:
                                    break

                                available_in_seg = min(seg_end, task.deadline) - seg_start
                                future_available_time += available_in_seg

                            # 检查后续所有free_slots中的可用时间
                            current_slot_index = free_slots.index(slot)
                            for future_slot in free_slots[current_slot_index + 1:]:
                                if future_slot['start'] >= task.deadline:
                                    break
                                slot_available = min(future_slot['end'], task.deadline) - future_slot['start']
                                if slot_available > timedelta(0):
                                    future_available_time += slot_available

                            # 如果后续可用时间不足以完成该任务，标记为需要空间
                            if future_available_time < task_remaining_time[task.id]:
                                tasks_need_space.append(task)

                    # 计算must_complete任务需要的总时间
                    must_complete_total_time = timedelta(0)
                    for task in must_complete_tasks:
                        must_complete_total_time += task_remaining_time[task.id]

                    # 计算tasks_need_space任务需要的总时间
                    tasks_need_space_total_time = timedelta(0)
                    for task in tasks_need_space:
                        if task not in must_complete_tasks:  # 避免重复计算
                            tasks_need_space_total_time += task_remaining_time[task.id]

                    # 当前段剩余时间
                    remaining_time_in_segment = segment_end - current_time

                    # 可以分配给available任务的时间（需要预留must_complete和need_space时间）
                    reserved_time = must_complete_total_time + tasks_need_space_total_time
                    available_for_others = remaining_time_in_segment - reserved_time

                    # === 选择任务逻辑 ===
                    best_task = None

                    # 1. 检查must_complete任务是否到了最晚开始时间
                    for task in must_complete_tasks:
                        latest_start = segment_end - task_remaining_time[task.id]
                        if current_time >= latest_start:
                            # 按重要性选择紧急任务
                            if not best_task or task.importance > best_task.importance:
                                best_task = task

                    # 2. 如果没有紧急的must_complete任务，按重要性选择
                    if not best_task:
                        # 分成两类：已开始的任务 和 未开始的任务
                        started_tasks = []
                        not_started_tasks = []

                        all_candidates = must_complete_tasks + available_tasks

                        for task in all_candidates:
                            if task_parts_count[task.id] > 0:
                                started_tasks.append(task)
                            else:
                                not_started_tasks.append(task)

                        # 优先继续已开始的任务（按重要性排序）
                        if started_tasks:
                            started_tasks.sort(key=lambda t: t.importance, reverse=True)
                            for task in started_tasks:
                                if task in must_complete_tasks:
                                    best_task = task
                                    break
                                elif task not in tasks_need_space and available_for_others > timedelta(minutes=0):
                                    # 不在need_space中的任务，需要有available_for_others空间
                                    best_task = task
                                    break
                                elif task in tasks_need_space:
                                    # 在need_space中的已开始任务，可以使用预留空间
                                    best_task = task
                                    break

                        # 如果没有可继续的任务，开始新任务（严格按重要性排序）
                        if not best_task and not_started_tasks:
                            not_started_tasks.sort(key=lambda t: t.importance, reverse=True)

                            # 首先尝试按重要性选择（如果有available_for_others空间）
                            for task in not_started_tasks:
                                if task in must_complete_tasks:
                                    best_task = task
                                    break
                                elif available_for_others > timedelta(minutes=0):
                                    best_task = task
                                    break

                            # 如果没有选中任务（可能因为available_for_others <= 0），
                            # 检查是否有need_space任务可以使用预留空间
                            if not best_task:
                                for task in tasks_need_space:
                                    if task in not_started_tasks:
                                        best_task = task
                                        break

                    if not best_task:
                        break  # 没有可调度的任务

                    # 计算填充时间
                    available_time = segment_end - current_time
                    fill_duration = min(task_remaining_time[best_task.id], available_time)

                    # 根据任务类型限制填充时间
                    if best_task in must_complete_tasks:
                        # must_complete任务不能超过deadline
                        time_until_deadline = best_task.deadline - current_time
                        fill_duration = min(fill_duration, time_until_deadline)
                    elif best_task in tasks_need_space:
                        # need_space任务可以使用reserved时间
                        max_fill = available_for_others + task_remaining_time[best_task.id]
                        fill_duration = min(fill_duration, max_fill)
                    else:
                        # 普通available任务不能占用reserved时间
                        fill_duration = min(fill_duration, max(timedelta(0), available_for_others))

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

                        # 更新available_for_others（如果是available任务）
                        if best_task not in must_complete_tasks:
                            available_for_others -= fill_duration
                    else:
                        break

        # 第四步：合并连续的同一任务片段
        merged_tasks = Scheduler._merge_consecutive_tasks(scheduled_tasks, schedule)

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

        return merged_tasks, failed_tasks

    @staticmethod
    def _merge_consecutive_tasks(scheduled_tasks, schedule):
        """
        合并连续的同一任务片段

        参数:
            scheduled_tasks: 已调度的任务列表
            schedule: Schedule对象

        返回:
            合并后的任务列表
        """
        if not scheduled_tasks:
            return scheduled_tasks

        # 按开始时间排序
        sorted_tasks = sorted(scheduled_tasks, key=lambda t: t.start_time)

        merged = []
        i = 0

        while i < len(sorted_tasks):
            current_task = sorted_tasks[i]

            # 提取任务的基础名称（去掉 "- Part X" 后缀）
            base_name = current_task.name
            if " - Part " in base_name:
                base_name = base_name.split(" - Part ")[0]

            # 查找所有连续的同一任务片段
            merge_group = [current_task]
            j = i + 1

            while j < len(sorted_tasks):
                next_task = sorted_tasks[j]
                next_base_name = next_task.name
                if " - Part " in next_base_name:
                    next_base_name = next_base_name.split(" - Part ")[0]

                # 检查是否是同一任务且时间连续
                if (next_base_name == base_name and
                    next_task.start_time == merge_group[-1].end_time and
                    next_task.importance == current_task.importance):
                    merge_group.append(next_task)
                    j += 1
                else:
                    break

            # 如果有多个连续片段，合并它们
            if len(merge_group) > 1:
                # 从schedule中移除所有片段
                for task in merge_group:
                    schedule.remove_task(task)

                # 创建合并后的任务
                total_duration = sum((t.end_time - t.start_time for t in merge_group), timedelta(0))

                # 保留第一个片段的Part编号
                merged_name = merge_group[0].name

                merged_task = Task(
                    name=merged_name,
                    estimated_time=int(total_duration.total_seconds() / 60),
                    importance=current_task.importance,
                    deadline=current_task.deadline,
                    earliest_start_time=None,
                    note=current_task.note
                )
                merged_task.start_time = merge_group[0].start_time
                merged_task.end_time = merge_group[-1].end_time

                # 添加合并后的任务
                schedule.add_task(merged_task)
                merged.append(merged_task)

                i = j
            else:
                # 只有一个片段，直接添加
                merged.append(current_task)
                i += 1

        return merged

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
