from datetime import timedelta, datetime
import uuid

class Task:
    """
    任务类：用于描述一个待办事项/任务的基本信息
    支持：
        - 任务名称
        - 预计用时（分钟）
        - 重要程度（1-5）
        - 截止时间（可选）
        - 是否完成
        - 唯一ID
        - 备注（可选）
    """
    def __init__(self, name, estimated_time, importance, deadline=None, earliest_start_time=None, completed=False, note=None, task_id=None, splittable=True):
        self.name = name  # 任务名称
        self.estimated_time = timedelta(minutes=estimated_time)  # 预计用时，timedelta对象
        self.importance = importance  # 重要程度，1-5
        self.deadline = deadline  # 截止时间，datetime对象或None
        self.earliest_start_time = earliest_start_time  # 最早开始时间，datetime对象或None
        self.completed = completed  # 是否完成
        self.note = note  # 备注，可选
        self.id = task_id if task_id else str(uuid.uuid4())  # 唯一ID，字符串
        self.splittable = splittable  # 是否可拆分

    def mark_completed(self):
        """标记任务为已完成"""
        self.completed = True

    def to_dict(self):
        """序列化为字典，便于保存为JSON"""
        return {
            'name': self.name,
            'estimated_time': self.estimated_time.total_seconds() // 60,  # 以分钟为单位
            'importance': self.importance,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'earliest_start_time': self.earliest_start_time.isoformat() if self.earliest_start_time else None,
            'completed': self.completed,
            'note': self.note,
            'id': self.id,
            'splittable': self.splittable,
        }

    @staticmethod
    def from_dict(data):
        """从字典反序列化为Task对象"""
        deadline = datetime.fromisoformat(data['deadline']) if data.get('deadline') else None
        earliest_start_time = datetime.fromisoformat(data['earliest_start_time']) if data.get('earliest_start_time') else None
        return Task(
            name=data['name'],
            estimated_time=int(data['estimated_time']),
            importance=int(data['importance']),
            deadline=deadline,
            earliest_start_time=earliest_start_time,
            completed=data.get('completed', False),
            note=data.get('note'),
            task_id=data.get('id'),
            splittable=data.get('splittable', True)
        )

    def __repr__(self):
        return f"Task(name={self.name}, estimated_time={self.estimated_time}, importance={self.importance}, deadline={self.deadline}, earliest_start_time={self.earliest_start_time}, completed={self.completed})"

# TODO:
# 1. 可以根据实际需求扩展更多字段，如标签、优先级类型等
# 2. 可以实现任务的子任务（如支持多级任务拆分）
# 3. 后续可添加与人机交互相关的静态方法，如：
#    - @staticmethod
#      def from_user_input():
#          # 通过命令行/GUI交互获取用户输入，生成Task对象
# 4. 可实现任务的导出/导入（如CSV、JSON等格式）

