# 开发指南 - 你需要完成的任务

## 📁 项目新结构

```
2026-PythonProject/
├── main.py                    # 主程序（需要重构）
├── requirements.txt           
├── core/                      # 核心业务逻辑
│   ├── task.py               # ✅ 已完成
│   ├── schedule.py           # ⚠️ 需要完善
│   ├── scheduler.py          # ❌ 需要你实现
│   └── week_schedule.py      # ❌ 需要你实现
├── ui/                        # 用户界面
│   └── cli.py                # ❌ 需要你实现
├── config/                    # 配置管理
│   └── settings.py           # ❌ 需要你实现
├── utils/                     # 工具函数
│   └── parser.py             # ⚠️ 需要扩展
└── data/                      # 数据存储
    ├── tasks.json
    └── schedules/             # 新增：按日期存储日程
```

---

## 🎯 你需要完成的5个主要任务

### 任务1: 完善 `core/schedule.py` ⭐⭐⭐
**目标**: 添加固定时间段支持、冲突检测

**需要添加的方法**:

```python
def add_fixed_slot(self, start_time, end_time, description):
    """添加固定时间段（吃饭、睡觉、上课等）"""
    # 提示：添加到 self.fixed_slots 列表
    # 格式：(start_time, end_time, description)

def find_available_slot(self, duration):
    """
    找到一个可以容纳duration时长的可用时间段
    
    参数:
        duration: timedelta对象，需要的时长
    
    返回:
        可用的开始时间（datetime），如果没有则返回None
    
    实现思路：
    1. 从self.start_time开始遍历
    2. 检查每个时间点是否被占用（固定时间段或已安排任务）
    3. 找到连续的空闲时间 >= duration
    4. 返回该时间段的开始时间
    """

def is_time_available(self, start_time, end_time):
    """检查某个时间段是否可用（没有冲突）"""
    # 提示：检查是否与fixed_slots和time_slots冲突

def get_available_slots(self):
    """获取所有可用时间段列表"""
    # 返回：[(start, end), (start, end), ...]

def display(self):
    """美观地打印日程表"""
    # 按时间顺序显示固定时间段和任务
```

**难度**: ⭐⭐⭐  
**预计时间**: 1-2小时

---

### 任务2: 实现 `core/scheduler.py` ⭐⭐⭐⭐
**目标**: 智能调度算法

**核心逻辑**:
```python
def schedule_tasks(tasks, schedule):
    # 1. 任务排序
    #    - 按重要性从高到低
    #    - 相同重要性的，按截止时间从近到远
    
    # 2. 遍历任务
    #    for task in sorted_tasks:
    #        找到可用时间段
    #        尝试添加任务
    #        如果失败，记录失败原因
    
    # 3. 返回统计信息
```

**挑战点**:
- 如何处理截止时间？（任务必须在截止时间前完成）
- 如何处理任务太多、时间不够的情况？

**难度**: ⭐⭐⭐⭐  
**预计时间**: 2-3小时

---

### 任务3: 实现 `ui/cli.py` ⭐⭐⭐
**目标**: 友好的命令行交互

**重点函数**:

1. `create_task_from_input()` - 交互式创建任务
2. `get_daily_settings()` - 获取每日作息时间
3. `add_multiple_tasks()` - 循环添加任务
4. `display_schedule()` - 美观显示日程

**示例代码**:
```python
def create_task_from_input():
    print("\n--- 添加新任务 ---")
    name = input("任务名称: ")
    
    while True:
        try:
            estimated_time = int(input("预计用时（分钟）: "))
            if estimated_time > 0:
                break
            print("时间必须大于0！")
        except ValueError:
            print("请输入有效的数字！")
    
    # 继续实现重要程度、截止时间等输入...
    
    return Task(name, estimated_time, importance, deadline, note=note)
```

**难度**: ⭐⭐⭐  
**预计时间**: 2-3小时

---

### 任务4: 实现 `config/settings.py` ⭐⭐
**目标**: 配置文件管理

**需要实现**:
- `load_settings()` - 从JSON加载配置
- `save_settings()` - 保存配置到JSON
- `set()` - 更新配置项

**示例**:
```python
def load_settings(self):
    if not os.path.exists(self.config_file):
        return self.DEFAULT_SETTINGS.copy()
    
    try:
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return self.DEFAULT_SETTINGS.copy()
```

**难度**: ⭐⭐  
**预计时间**: 1小时

---

### 任务5: 实现 `core/week_schedule.py` ⭐⭐⭐⭐
**目标**: 多日日程管理

**核心方法**:
```python
def __init__(self, start_date, days=7):
    self.schedules = {}
    
    # 为每一天创建Schedule对象
    for i in range(days):
        date = start_date + timedelta(days=i)
        # 从配置文件读取默认作息时间
        wake_up = ...  # 结合settings
        sleep = ...
        
        start_time = datetime.combine(date, wake_up)
        end_time = datetime.combine(date, sleep)
        
        self.schedules[date] = Schedule(start_time, end_time)
```

**难度**: ⭐⭐⭐⭐  
**预计时间**: 2小时

---

## 🔄 完整工作流程

```
用户运行程序
    ↓
[cli.py] 显示欢迎，询问要创建几天的日程
    ↓
[week_schedule.py] 创建WeekSchedule对象
    ↓
[cli.py] 为每一天询问作息时间（或使用默认配置）
    ↓
[schedule.py] 为每天添加固定时间段（吃饭、睡觉）
    ↓
[cli.py] 循环添加任务
    ↓
[scheduler.py] 智能调度，将任务分配到各天
    ↓
[cli.py] 显示完整日程
    ↓
[parser.py] 保存数据
```

---

## 📝 建议的开发顺序

1. **第一步**: 完善 `schedule.py`（最基础）
2. **第二步**: 实现 `settings.py`（简单，有成就感）
3. **第三步**: 实现 `cli.py` 的基础交互
4. **第四步**: 实现 `scheduler.py` 的调度算法
5. **第五步**: 实现 `week_schedule.py`
6. **第六步**: 整合到 `main.py`，测试完整流程

---

## 💡 实用提示

### 时间处理技巧：
```python
from datetime import datetime, timedelta, time

# 字符串转时间
time_str = "07:30"
hour, minute = map(int, time_str.split(':'))
wake_up = time(hour, minute)

# 日期+时间 = datetime
date = datetime.now().date()
wake_up_datetime = datetime.combine(date, wake_up)

# 时间段检查
def has_overlap(start1, end1, start2, end2):
    return start1 < end2 and start2 < end1
```

### 输入验证技巧：
```python
def get_int_input(prompt, min_val, max_val):
    """获取整数输入，带验证"""
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            print(f"请输入{min_val}-{max_val}之间的数字！")
        except ValueError:
            print("请输入有效的数字！")
```

---

## 🐛 调试建议

1. **先写简单版本，再优化**
2. **每完成一个函数就测试**
3. **使用print()查看中间结果**
4. **从小功能开始，逐步组合**

---

## ❓ 遇到问题？

随时问我：
- "这个函数怎么实现？"
- "为什么会报这个错误？"
- "有没有更好的实现方式？"
- "帮我检查一下这段代码"

加油！💪
