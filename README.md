# 智能日程安排工具 📅

一个基于Python的自动日程安排工具，帮助你高效管理日常任务。

## 项目简介

本项目是南京大学Python课程大作业，旨在实现一个智能的日程安排系统。用户可以添加任务（包括预计用时、重要程度），设置每日起床、吃饭、睡觉时间，系统将自动生成优化的日程安排。

## 主要功能

- ✅ **任务管理**：添加、删除、修改任务信息
- ✅ **智能调度**：根据任务重要性和时间自动排程
- ✅ **固定时间段**：支持设置起床、吃饭、睡觉等固定时间
- 📅 **课表导入**：支持南京大学课表导入（开发中）
- 🔄 **动态调整**：支持临时增删任务，实时调整日程
- 💾 **数据持久化**：保存任务和日程数据
- 🎨 **GUI界面**：图形化操作界面（计划中）

## 项目结构

```
2026-PythonProject/
├── main.py              # 主程序入口
├── requirements.txt     # 依赖包列表
├── core/               # 核心模块
│   ├── task.py         # 任务类定义
│   └── schedule.py     # 日程调度类
├── utils/              # 工具模块
│   └── parser.py       # 数据解析和存储
└── data/               # 数据存储
    └── tasks.json      # 任务数据
```

## 安装使用

### 环境要求

- Python 3.8+

### 安装步骤

1. 克隆项目到本地：
```bash
git clone <your-repository-url>
cd 2026-PythonProject
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行程序：
```bash
python main.py
```

## 使用示例

```python
# 创建任务
task = Task(name="完成大作业", estimated_time=180, importance=5)

# 自动排程
schedule = Schedule(start_time=..., end_time=...)
schedule.add_task(task, start_time)
```

## 开发计划

- [x] 基础框架搭建
- [ ] 完善核心功能
- [ ] 实现智能调度算法
- [ ] 命令行交互界面
- [ ] GUI图形界面
- [ ] 课表导入功能
- [ ] 单元测试

## 作者

南京大学 - Python课程大作业

## 许可证

MIT License

---

**项目开始时间**：2026年1月
**提交截止时间**：2026年1月31日
