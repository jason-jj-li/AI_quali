# -*- coding: utf-8 -*-
"""
QualInsight 性能监控和追踪模块
提供性能分析和监控功能
"""

import time
import functools
from typing import Callable, Dict, List, Optional
from collections import defaultdict
import streamlit as st


# ==================== 性能追踪器 ====================

class PerformanceTracker:
    """性能追踪器"""

    def __init__(self):
        self._metrics: Dict[str, List[float]] = defaultdict(list)
        self._call_counts: Dict[str, int] = defaultdict(int)

    def track(self, name: str, duration: float):
        """记录性能数据"""
        self._metrics[name].append(duration)
        self._call_counts[name] += 1

    def get_stats(self, name: str) -> Dict[str, float]:
        """获取指定名称的统计"""
        if name not in self._metrics:
            return {}

        durations = self._metrics[name]

        return {
            'count': len(durations),
            'total': sum(durations),
            'avg': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations),
        }

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """获取所有统计"""
        return {name: self.get_stats(name) for name in self._metrics}

    def reset(self):
        """重置所有数据"""
        self._metrics.clear()
        self._call_counts.clear()


# ==================== 性能装饰器 ====================

_global_tracker = PerformanceTracker()


def track_performance(name: Optional[str] = None):
    """
    性能追踪装饰器

    Args:
        name: 追踪名称（默认使用函数名）

    Returns:
        装饰后的函数
    """
    def decorator(func: Callable) -> Callable:
        tracker_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                _global_tracker.track(tracker_name, duration)

        return wrapper

    return decorator


def track_if_debug(func: Callable) -> Callable:
    """仅在调试模式下追踪性能"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if st.session_state.get('debug_mode', False):
            return track_performance()(func)(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    return wrapper


# ==================== 批量处理优化 ====================

class BatchProcessor:
    """批量处理器"""

    def __init__(self, batch_size: int = 10):
        """
        初始化批量处理器

        Args:
            batch_size: 批次大小
        """
        self.batch_size = batch_size

    def process_batch(
        self,
        items: List[Any],
        process_func: Callable,
        show_progress: bool = True
    ) -> List[Any]:
        """
        批量处理项目

        Args:
            items: 要处理的项目列表
            process_func: 处理函数
            show_progress: 是否显示进度

        Returns:
            处理结果列表
        """
        results = []
        total = len(items)
        batches = (total + self.batch_size - 1) // self.batch_size

        for i in range(batches):
            start_idx = i * self.batch_size
            end_idx = min((i + 1) * self.batch_size, total)
            batch = items[start_idx:end_idx]

            if show_progress:
                progress = (end_idx / total)
                st.progress(progress)
                st.caption(f"处理中: {end_idx}/{total}")

            # 处理批次
            batch_results = [process_func(item) for item in batch]
            results.extend(batch_results)

        if show_progress:
            st.progress(1.0)
            st.success(f"✅ 处理完成: {total} 项")

        return results

    def process_with_retries(
        self,
        items: List[Any],
        process_func: Callable,
        max_retries: int = 3,
        show_progress: bool = True
    ) -> List[Any]:
        """
        带重试的批量处理

        Args:
            items: 要处理的项目列表
            process_func: 处理函数
            max_retries: 最大重试次数
            show_progress: 是否显示进度

        Returns:
            处理结果列表
        """
        results = []
        failed_items = []

        for i, item in enumerate(items):
            if show_progress:
                st.progress((i + 1) / len(items))
                st.caption(f"处理中: {i + 1}/{len(items)}")

            # 带重试的处理
            for attempt in range(max_retries):
                try:
                    result = process_func(item)
                    results.append(result)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        failed_items.append((i, item, str(e)))
                    else:
                        time.sleep(1)  # 等待后重试

        if show_progress:
            st.progress(1.0)

            if failed_items:
                st.warning(f"⚠️ {len(failed_items)} 项处理失败")
            else:
                st.success(f"✅ 处理完成: {len(results)} 项")

        return results


# ==================== 并发处理 ====================

class ConcurrentProcessor:
    """并发处理器（简化版）"""

    def __init__(self, max_workers: int = 5):
        """
        初始化并发处理器

        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers

    def process_concurrent(
        self,
        items: List[Any],
        process_func: Callable,
        show_progress: bool = True
    ) -> List[Any]:
        """
        并发处理项目

        Args:
            items: 要处理的项目列表
            process_func: 处理函数
            show_progress: 是否显示进度

        Returns:
            处理结果列表
        """
        # 简化实现：顺序处理（实际应用可使用线程池）
        results = []

        for i, item in enumerate(items):
            if show_progress:
                st.progress((i + 1) / len(items))

            result = process_func(item)
            results.append(result)

        return results


# ==================== 性能报告 ====================

def show_performance_report():
    """显示性能报告"""
    stats = _global_tracker.get_all_stats()

    if not stats:
        st.info("📊 暂无性能数据")
        return

    st.write("### 📊 性能报告")

    # 按总耗时排序
    sorted_stats = sorted(
        stats.items(),
        key=lambda x: x[1].get('total', 0),
        reverse=True
    )

    for name, stat in sorted_stats:
        with st.expander(f"🔍 {name}"):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("调用次数", stat['count'])

            with col2:
                st.metric("总耗时", f"{stat['total']:.2f}s")

            with col3:
                st.metric("平均耗时", f"{stat['avg']:.2f}s")

            with col4:
                st.metric("最大耗时", f"{stat['max']:.2f}s")

    # 清除按钮
    if st.button("🗑️ 清除性能数据"):
        _global_tracker.reset()
        st.success("✅ 已清除")
        st.rerun()


def show_performance_summary():
    """显示性能摘要"""
    stats = _global_tracker.get_all_stats()

    if not stats:
        return

    total_calls = sum(s.get('count', 0) for s in stats.values())
    total_time = sum(s.get('total', 0) for s in stats.values())

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("总调用", total_calls)

    with col2:
        st.metric("总耗时", f"{total_time:.1f}s")

    with col3:
        avg_time = total_time / total_calls if total_calls > 0 else 0
        st.metric("平均耗时", f"{avg_time:.2f}s")


# ==================== 响应式布局 ====================

class ResponsiveLayout:
    """响应式布局管理器"""

    @staticmethod
    def get_layout_width() -> str:
        """获取当前布局宽度"""
        # Streamlit 不直接提供宽度信息，这里返回默认值
        return "wide"

    @staticmethod
    def should_use_single_column() -> bool:
        """判断是否应该使用单列布局"""
        # 在小屏幕上使用单列
        return False  # 简化实现

    @staticmethod
    def render_columns(items: List[Any], max_columns: int = 4):
        """
        根据屏幕大小渲染列

        Args:
            items: 要渲染的项目
            max_columns: 最大列数
        """
        if ResponsiveLayout.should_use_single_column():
            # 单列布局
            for item in items:
                st.write(item)
        else:
            # 多列布局
            columns = min(max_columns, len(items))
            cols = st.columns([1] * columns)

            for i, item in enumerate(items):
                col = cols[i % columns]
                with col:
                    st.write(item)


# ==================== 操作历史和撤销 ====================

class ActionHistory:
    """操作历史管理器"""

    def __init__(self, max_history: int = 50):
        """
        初始化操作历史

        Args:
            max_history: 最大历史记录数
        """
        self.history: List[Dict[str, Any]] = []
        self.max_history = max_history
        self.current_index = -1

    def add_action(
        self,
        action_type: str,
        description: str,
        data: Any = None,
        restore_func: Optional[Callable] = None
    ):
        """
        添加操作到历史

        Args:
            action_type: 操作类型
            description: 描述
            data: 数据
            restore_func: 恢复函数
        """
        action = {
            'type': action_type,
            'description': description,
            'data': data,
            'restore_func': restore_func,
            'timestamp': time.time(),
        }

        # 如果当前不在历史末尾，移除后面的记录
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]

        self.history.append(action)

        # 限制历史长度
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.current_index += 1

    def can_undo(self) -> bool:
        """是否可以撤销"""
        return self.current_index >= 0

    def can_redo(self) -> bool:
        """是否可以重做"""
        return self.current_index < len(self.history) - 1

    def undo(self) -> Optional[Dict[str, Any]]:
        """撤销"""
        if not self.can_undo():
            return None

        action = self.history[self.current_index]
        self.current_index -= 1

        return action

    def redo(self) -> Optional[Dict[str, Any]]:
        """重做"""
        if not self.can_redo():
            return None

        self.current_index += 1
        action = self.history[self.current_index]

        return action

    def get_history(self) -> List[Dict[str, Any]]:
        """获取历史记录"""
        return self.history.copy()


# ==================== 全局实例 ====================

_global_history: Optional[ActionHistory] = None


def get_action_history() -> ActionHistory:
    """获取全局操作历史实例"""
    global _global_history

    if _global_history is None:
        _global_history = ActionHistory()

    return _global_history


def show_undo_redo():
    """显示撤销/重做按钮"""
    history = get_action_history()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("↩️ 撤销", disabled=not history.can_undo()):
            action = history.undo()
            if action and action.get('restore_func'):
                action['restore_func'](action['data'])

    with col2:
        if st.button("↪️ 重做", disabled=not history.can_redo()):
            action = history.redo()
            if action and action.get('restore_func'):
                action['restore_func'](action['data'])
