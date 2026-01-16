# -*- coding: utf-8 -*-
"""
QualInsight 进度反馈模块
提供详细的操作进度反馈和状态更新
"""

import time
import functools
from typing import Callable, List, Tuple, Any, Optional, Generator
from contextlib import contextmanager


# ==================== 进度管理器 ====================

class ProgressManager:
    """进度管理器 - 跟踪多步骤操作的进度"""

    def __init__(self, steps: List[str], container=None):
        """
        初始化进度管理器

        Args:
            steps: 步骤名称列表
            container: Streamlit 容器（用于显示进度）
        """
        self.steps = steps
        self.current_step = 0
        self.container = container
        self._start_time = None
        self._status_text = None
        self._progress_bar = None

    def start(self):
        """开始进度跟踪"""
        self._start_time = time.time()
        self.current_step = 0

        if self.container:
            with self.container:
                self._status_text = self.container.empty()
                self._progress_bar = self.container.progress(0)

    def update(self, step_index: int, message: str = ""):
        """
        更新进度

        Args:
            step_index: 当前步骤索引
            message: 状态消息
        """
        self.current_step = step_index

        if self._status_text:
            status_msg = self.steps[step_index] if step_index < len(self.steps) else message
            if message:
                status_msg = f"{status_msg}: {message}"
            self._status_text.text(status_msg)

        if self._progress_bar:
            progress = (step_index + 1) / len(self.steps)
            self._progress_bar.progress(progress)

    def complete(self, message: str = "完成！"):
        """标记完成"""
        if self._status_text:
            elapsed = time.time() - self._start_time if self._start_time else 0
            self._status_text.text(f"✅ {message} (耗时: {elapsed:.1f}秒)")

        if self._progress_bar:
            self._progress_bar.progress(1.0)

    def get_progress(self) -> float:
        """获取当前进度百分比"""
        return (self.current_step + 1) / len(self.steps) if self.steps else 0


# ==================== 进度装饰器 ====================

def with_progress(steps: List[str], show_time: bool = True):
    """
    为函数添加进度反馈装饰器

    Args:
        steps: 步骤名称列表
        show_time: 是否显示耗时

    Returns:
        装饰后的函数

    Example:
        @with_progress(["加载数据", "处理数据", "保存结果"])
        def process_data(data):
            result = step1(data)
            result = step2(result)
            return step3(result)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import streamlit as st

            # 创建进度容器
            progress_container = st.container()

            with progress_container:
                st.write(f"**执行进度**:")
                status_text = st.empty()
                progress_bar = st.progress(0)
                time_text = st.empty() if show_time else None

            start_time = time.time()

            try:
                # 执行函数（传入回调用于更新进度）
                def update_progress(step_index: int, message: str = ""):
                    if step_index < len(steps):
                        status_msg = steps[step_index]
                        if message:
                            status_msg = f"{status_msg}: {message}"
                    else:
                        status_msg = message

                    status_text.text(status_msg)
                    progress_bar.progress((step_index + 1) / len(steps))

                    if show_time and time_text:
                        elapsed = time.time() - start_time
                        time_text.caption(f"⏱️ 已耗时: {elapsed:.1f}秒")

                # 执行原函数
                result = func(*args, **kwargs, progress_callback=update_progress)

                # 显示完成状态
                elapsed = time.time() - start_time
                status_text.text(f"✅ 完成！")
                progress_bar.progress(1.0)
                if show_time and time_text:
                    time_text.caption(f"⏱️ 总耗时: {elapsed:.1f}秒")

                return result

            except Exception as e:
                status_text.text(f"❌ 出错: {str(e)}")
                raise

        return wrapper

    return decorator


def with_spinner(message: str = "处理中..."):
    """
    简单的加载装饰器

    Args:
        message: 加载消息

    Returns:
        装饰后的函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import streamlit as st

            with st.spinner(message):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# ==================== 进度上下文管理器 ====================

@contextmanager
def progress_context(steps: List[str], container=None):
    """
    进度上下文管理器

    Args:
        steps: 步骤名称列表
        container: Streamlit 容器

    Yields:
        ProgressManager 实例

    Example:
        with progress_context(["步骤1", "步骤2", "步骤3"]) as progress:
            progress.update(0, "初始化")
            # ... 执行步骤1
            progress.update(1, "处理中")
            # ... 执行步骤2
            progress.complete()
    """
    import streamlit as st

    manager = ProgressManager(steps, container)

    if container is None:
        container = st.container()

    with container:
        st.write("**执行进度**:")
        status_text = st.empty()
        progress_bar = st.progress(0)
        time_text = st.empty()

    manager.start()
    manager._status_text = status_text
    manager._progress_bar = progress_bar

    try:
        yield manager
    finally:
        manager.complete()


# ==================== 流式进度 ====================

def stream_progress(steps_generator: Generator[Tuple[int, str], None, Any], container=None):
    """
    流式显示进度

    Args:
        steps_generator: 生成 (step_index, message) 的生成器
        container: Streamlit 容器

    Returns:
        生成器的最终结果

    Example:
        def my_process():
            for i, msg in enumerate(["步骤1", "步骤2", "步骤3"]):
                yield i, msg
                time.sleep(1)
            return "完成"

        result = stream_progress(my_process())
    """
    import streamlit as st

    if container is None:
        container = st.container()

    with container:
        status_text = st.empty()
        progress_bar = st.empty()

    result = None
    for step_index, message in steps_generator:
        status_text.text(f"正在执行: {message}")
        # 创建进度条（需要重新创建来更新）
        progress_bar.write(f"进度: {step_index + 1} 步")

    status_text.text("✅ 完成！")
    return result


# ==================== 任务状态追踪 ====================

class TaskTracker:
    """任务状态追踪器"""

    def __init__(self, task_name: str):
        """
        初始化任务追踪器

        Args:
            task_name: 任务名称
        """
        self.task_name = task_name
        self.subtasks = []
        self.current_subtask = 0
        self._start_time = None
        self._container = None

    def add_subtask(self, name: str):
        """添加子任务"""
        self.subtasks.append(name)

    def start(self, container=None):
        """开始追踪"""
        import streamlit as st

        self._start_time = time.time()
        self._container = container or st.container()

        with self._container:
            st.write(f"**📋 {self.task_name}**")

            if self.subtasks:
                for i, subtask in enumerate(self.subtasks):
                    st.markdown(f"{'✅' if i < self.current_subtask else '⏳'} {subtask}")

    def update_subtask(self, index: int):
        """更新当前子任务"""
        self.current_subtask = index
        if self._container:
            self.start()  # 重新渲染

    def complete(self):
        """标记完成"""
        if self._container:
            with self._container:
                elapsed = time.time() - self._start_time if self._start_time else 0
                st.success(f"✅ {self.task_name} 完成！ (耗时: {elapsed:.1f}秒)")


# ==================== 辅助函数 ====================

def format_time(seconds: float) -> str:
    """
    格式化时间显示

    Args:
        seconds: 秒数

    Returns:
        格式化的时间字符串
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}毫秒"
    elif seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def estimate_remaining(start_time: float, current_step: int, total_steps: int) -> float:
    """
    估算剩余时间

    Args:
        start_time: 开始时间
        current_step: 当前步骤
        total_steps: 总步骤数

    Returns:
        估算的剩余秒数
    """
    if current_step == 0:
        return 0

    elapsed = time.time() - start_time
    time_per_step = elapsed / current_step
    remaining = time_per_step * (total_steps - current_step)

    return remaining


def show_progress_with_eta(steps: List[str], container=None):
    """
    显示带预计完成时间的进度

    Args:
        steps: 步骤列表
        container: 容器

    Returns:
        更新函数
    """
    import streamlit as st

    if container is None:
        container = st.container()

    start_time = time.time()

    with container:
        status_text = st.empty()
        progress_bar = st.progress(0)
        eta_text = st.empty()

    def update(step_index: int, message: str = ""):
        step_name = steps[step_index] if step_index < len(steps) else message

        status_text.text(f"正在执行: {step_name}")
        progress_bar.progress((step_index + 1) / len(steps))

        # 计算预计时间
        remaining = estimate_remaining(start_time, step_index + 1, len(steps))
        if remaining > 0:
            eta_text.caption(f"⏱️ 预计剩余: {format_time(remaining)}")
        else:
            eta_text.empty()

    def complete():
        elapsed = time.time() - start_time
        status_text.text("✅ 完成！")
        progress_bar.progress(1.0)
        eta_text.caption(f"⏱️ 总耗时: {format_time(elapsed)}")

    return update, complete


# ==================== Streamlit 集成 ====================

def create_progress_container(steps: List[str]) -> tuple:
    """
    创建进度显示容器

    Args:
        steps: 步骤列表

    Returns:
        (update_func, complete_func) 元组
    """
    import streamlit as st

    with st.container():
        st.write("**执行进度**:")
        status = st.empty()
        progress = st.progress(0)

    start_time = time.time()

    def update(step: int, msg: str = ""):
        name = steps[step] if step < len(steps) else msg
        status.text(name)
        progress.progress((step + 1) / len(steps))

        # 显示耗时
        elapsed = time.time() - start_time
        if step > 0:
            avg_time = elapsed / (step + 1)
            remaining = avg_time * (len(steps) - step - 1)
            st.caption(f"⏱️ 已耗时: {format_time(elapsed)} | 预计剩余: {format_time(remaining)}")

    def complete(final_msg: str = "完成！"):
        elapsed = time.time() - start_time
        status.text(f"✅ {final_msg}")
        progress.progress(1.0)
        st.caption(f"⏱️ 总耗时: {format_time(elapsed)}")

    return update, complete
