# -*- coding: utf-8 -*-
"""
QualInsight 缓存装饰器模块
提供智能缓存功能，提升LLM调用性能
"""

import functools
import hashlib
import json
import time
from typing import Callable, Any, Optional, Dict
from functools import wraps


# ==================== 缓存配置 ====================

DEFAULT_CACHE_TTL = 3600  # 默认缓存1小时
CACHE_VERSION = "v1"  # 缓存版本号


# ==================== 简单的内存缓存 ====================

class SimpleCache:
    """简单的内存缓存实现"""

    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key: (value, expire_time)
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0
        }

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self._cache:
            value, expire_time = self._cache[key]
            if expire_time is None or time.time() < expire_time:
                self._stats['hits'] += 1
                return value
            else:
                # 缓存过期
                del self._cache[key]
        self._stats['misses'] += 1
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        expire_time = time.time() + ttl if ttl else None
        self._cache[key] = (value, expire_time)
        self._stats['sets'] += 1

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()

    def get_stats(self) -> Dict[str, int]:
        """获取缓存统计"""
        total = self._stats['hits'] + self._stats['misses']
        hit_rate = self._stats['hits'] / total if total > 0 else 0
        return {
            **self._stats,
            'size': len(self._cache),
            'hit_rate': hit_rate
        }


# 全局缓存实例
_global_cache = SimpleCache()


# ==================== 缓存键生成 ====================

def generate_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """
    生成缓存键

    Args:
        func_name: 函数名
        args: 位置参数
        kwargs: 关键字参数

    Returns:
        缓存键
    """
    # 序列化参数
    key_parts = [
        CACHE_VERSION,
        func_name,
    ]

    # 添加位置参数（排除不可序列化的对象）
    for arg in args:
        if _is_json_serializable(arg):
            key_parts.append(json.dumps(arg, sort_keys=True, ensure_ascii=False))
        else:
            # 对于不可序列化的对象，使用其类型和ID
            key_parts.append(f"{type(arg).__name__}_{id(arg)}")

    # 添加关键字参数
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        for k, v in sorted_kwargs:
            if _is_json_serializable(v):
                key_parts.append(f"{k}:{json.dumps(v, sort_keys=True, ensure_ascii=False)}")
            else:
                key_parts.append(f"{k}:{type(v).__name__}_{id(v)}")

    # 生成哈希
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def _is_json_serializable(obj: Any) -> bool:
    """检查对象是否可以JSON序列化"""
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False


# ==================== 缓存装饰器 ====================

def cached(
    ttl: int = DEFAULT_CACHE_TTL,
    key_func: Optional[Callable] = None,
    cache_instance: Optional[SimpleCache] = None
) -> Callable:
    """
    缓存装饰器

    Args:
        ttl: 缓存生存时间（秒）
        key_func: 自定义缓存键生成函数
        cache_instance: 自定义缓存实例

    Returns:
        装饰后的函数

    Example:
        @cached(ttl=1800)
        def expensive_operation(param1, param2):
            return result
    """
    cache = cache_instance or _global_cache

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(func.__name__, args, kwargs)
            else:
                cache_key = generate_cache_key(func.__name__, args, kwargs)

            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 存入缓存
            cache.set(cache_key, result, ttl)

            return result

        # 添加缓存相关方法
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_stats = lambda: cache.get_stats()

        return wrapper

    return decorator


def cached_llm(ttl: int = 3600) -> Callable:
    """
    LLM调用专用缓存装饰器

    Args:
        ttl: 缓存生存时间（秒）

    Returns:
        装饰后的函数

    Example:
        @cached_llm(ttl=1800)
        def call_llm(prompt, model="gpt-3.5"):
            return response
    """
    return cached(ttl=ttl, cache_instance=_global_cache)


def cached_llm_with_key(key_func: Callable) -> Callable:
    """
    LLM调用专用缓存装饰器（使用自定义键）

    Args:
        key_func: 自定义缓存键生成函数

    Returns:
        装饰后的函数

    Example:
        def make_key(prompt, model):
            return f"{model}:{hashlib.md5(prompt.encode()).hexdigest()}"

        @cached_llm_with_key(make_key)
        def call_llm(prompt, model):
            return response
    """
    return cached(key_func=key_func, cache_instance=_global_cache)


# ==================== 条件缓存装饰器 ====================

def cached_if(condition: Callable[[...], bool], ttl: int = DEFAULT_CACHE_TTL) -> Callable:
    """
    条件缓存装饰器 - 仅在条件满足时缓存

    Args:
        condition: 条件函数，接受原函数参数
        ttl: 缓存生存时间

    Returns:
        装饰后的函数

    Example:
        @cached_if(lambda prompt: len(prompt) > 100)
        def call_llm(prompt):
            return response
    """
    cache = _global_cache

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查条件
            if not condition(*args, **kwargs):
                return func(*args, **kwargs)

            # 生成缓存键
            cache_key = generate_cache_key(func.__name__, args, kwargs)

            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 存入缓存
            cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


# ==================== 缓存管理 ====================

def clear_cache() -> None:
    """清空全局缓存"""
    _global_cache.clear()


def get_cache_stats() -> Dict[str, int]:
    """获取缓存统计信息"""
    return _global_cache.get_stats()


def display_cache_stats() -> str:
    """生成可读的缓存统计信息"""
    stats = get_cache_stats()
    total = stats['hits'] + stats['misses']

    return (
        f"缓存统计:\n"
        f"  命中: {stats['hits']}\n"
        f"  未命中: {stats['misses']}\n"
        f"  命中率: {stats['hit_rate']:.1%}\n"
        f"  缓存项: {stats['size']}"
    )


# ==================== Streamlit 集成 ====================

def show_cache_stats():
    """在 Streamlit 中显示缓存统计"""
    stats = get_cache_stats()

    st.markdown("### 📊 缓存性能")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("命中", stats['hits'])
    with col2:
        st.metric("未命中", stats['misses'])
    with col3:
        st.metric("命中率", f"{stats['hit_rate']:.1%}")
    with col4:
        st.metric("缓存项", stats['size'])

    # 清除按钮
    if st.button("🗑️ 清空缓存"):
        clear_cache()
        st.success("✅ 缓存已清空")
        st.rerun()


# ==================== 辅助函数 ====================

def make_hash_key(*args, **kwargs) -> str:
    """
    从参数创建哈希键

    Returns:
        MD5哈希字符串
    """
    key_parts = []

    for arg in args:
        if _is_json_serializable(arg):
            key_parts.append(json.dumps(arg, sort_keys=True))
        else:
            key_parts.append(str(arg))

    for k, v in sorted(kwargs.items()):
        if _is_json_serializable(v):
            key_parts.append(f"{k}:{json.dumps(v, sort_keys=True)}")
        else:
            key_parts.append(f"{k}:{str(v)}")

    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


# ==================== 批量操作缓存 ====================

def batch_cached(ttl: int = DEFAULT_CACHE_TTL) -> Callable:
    """
    批量操作缓存装饰器

    对于列表/数组类型的结果，缓存每个项目

    Args:
        ttl: 缓存生存时间

    Returns:
        装饰后的函数
    """
    cache = _global_cache

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 尝试从缓存获取
            cache_key = generate_cache_key(func.__name__, args, kwargs)
            cached_value = cache.get(cache_key)

            if cached_value is not None:
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 存入缓存
            cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator
