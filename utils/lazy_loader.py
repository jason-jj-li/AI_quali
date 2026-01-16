# -*- coding: utf-8 -*-
"""
QualInsight 懒加载模块
实现NLP模型和其他大型资源的延迟加载
"""

import functools
from typing import Callable, Any, Optional, Dict
import threading


# ==================== 懒加载类 ====================

class LazyLoader:
    """
    懒加载器 - 延迟加载大型资源直到首次使用

    Example:
        model = LazyLoader(lambda: spacy.load("zh_core_web_sm"))
        # 模型不会立即加载
        result = model().process(text)  # 首次调用时才加载
    """

    def __init__(self, load_func: Callable, name: Optional[str] = None):
        """
        初始化懒加载器

        Args:
            load_func: 加载资源的函数
            name: 资源名称（用于调试）
        """
        self._load_func = load_func
        self._name = name or load_func.__name__
        self._instance = None
        self._loaded = False
        self._lock = threading.Lock()

    def __call__(self) -> Any:
        """获取加载的资源"""
        if self._loaded:
            return self._instance

        with self._lock:
            # 双重检查锁定模式
            if self._loaded:
                return self._instance

            self._instance = self._load_func()
            self._loaded = True

        return self._instance

    def is_loaded(self) -> bool:
        """检查是否已加载"""
        return self._loaded

    def reset(self):
        """重置（卸载资源）"""
        with self._lock:
            self._instance = None
            self._loaded = False

    def preload(self):
        """预加载资源"""
        _ = self()


class LazyDict:
    """
    懒加载字典 - 按需加载字典中的值

    Example:
        models = LazyDict({
            "spacy": lambda: spacy.load("zh_core_web_sm"),
            "nltk": lambda: nltk.download("punkt")
        })
        spacy_model = models["spacy"]  # 首次访问时加载
    """

    def __init__(self, load_dict: Dict[str, Callable]):
        """
        初始化懒加载字典

        Args:
            load_dict: {key: load_func} 字典
        """
        self._load_funcs = load_dict
        self._instances = {}
        self._locks = {key: threading.Lock() for key in load_dict}

    def __getitem__(self, key: str) -> Any:
        """获取并加载指定键的值"""
        if key in self._instances:
            return self._instances[key]

        if key not in self._load_funcs:
            raise KeyError(f"Key '{key}' not found")

        with self._locks[key]:
            if key in self._instances:
                return self._instances[key]

            self._instances[key] = self._load_funcs[key]()

        return self._instances[key]

    def get(self, key: str, default: Any = None) -> Any:
        """安全获取值"""
        try:
            return self[key]
        except KeyError:
            return default

    def is_loaded(self, key: str) -> bool:
        """检查指定键是否已加载"""
        return key in self._instances

    def preload(self, key: str):
        """预加载指定键"""
        _ = self[key]

    def preload_all(self):
        """预加载所有项"""
        for key in self._load_funcs:
            self.preload(key)


# ==================== 装饰器 ====================

def lazy_load(load_func: Optional[Callable] = None, name: Optional[str] = None):
    """
    懒加载装饰器

    Args:
        load_func: 加载函数（如果作为装饰器使用）
        name: 资源名称

    Example:
        @lazy_load(name="spacy_model")
        def get_spacy():
            import spacy
            return spacy.load("zh_core_web_sm")

        model = get_spacy()  # 首次调用时加载
    """
    def decorator(func: Callable) -> Callable:
        loader = LazyLoader(func, name or func.__name__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return loader()

        wrapper.is_loaded = lambda: loader.is_loaded()
        wrapper.reset = lambda: loader.reset()
        wrapper.preload = lambda: loader.preload()

        return wrapper

    if load_func is not None:
        return decorator(load_func)

    return decorator


def cached_property(load_func: Optional[Callable] = None):
    """
    缓存属性装饰器 - 首次访问后缓存结果

    Example:
        class MyClass:
            @cached_property
            def expensive_resource(self):
                return load_heavy_resource()

        obj = MyClass()
        resource = obj.expensive_resource  # 首次加载
        resource = obj.expensive_resource  # 使用缓存
    """
    attr_name = f"_cached_{load_func.__name__ if load_func else 'property'}"

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self):
            if not hasattr(self, attr_name):
                setattr(self, attr_name, func(self))
            return getattr(self, attr_name)

        # 添加重置方法
        def reset(self):
            if hasattr(self, attr_name):
                delattr(self, attr_name)

        wrapper.reset = reset

        return property(wrapper)

    if load_func is not None:
        return decorator(load_func)

    return decorator


# ==================== 全局懒加载实例 ====================

# NLP模型懒加载器
_nlp_models = LazyDict({
    "spacy_zh": lambda: __import__("spacy").load("zh_core_web_sm"),
    "spacy_en": lambda: __import__("spacy").load("en_core_web_sm"),
})


def get_nlp_model(model_name: str = "spacy_zh"):
    """
    获取NLP模型（懒加载）

    Args:
        model_name: 模型名称

    Returns:
        加载的模型
    """
    return _nlp_models[model_name]


def preload_nlp_model(model_name: str = "spacy_zh"):
    """预加载NLP模型"""
    _nlp_models.preload(model_name)


# ==================== 上下文管理器 ====================

class AutoCleanup:
    """
    自动清理资源

    Example:
        with AutoCleanup(lambda: load_resource(), cleanup=lambda r: r.close()):
            resource = AutoCleanup.get()
            # 使用资源
        # 退出时自动清理
    """

    def __init__(self, load_func: Callable, cleanup_func: Optional[Callable] = None):
        """
        初始化

        Args:
            load_func: 加载函数
            cleanup_func: 清理函数
        """
        self._load_func = load_func
        self._cleanup_func = cleanup_func
        self._resource = None

    def __enter__(self):
        self._resource = self._load_func()
        return self._resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._cleanup_func and self._resource:
            self._cleanup_func(self._resource)
            self._resource = None


# ==================== 辅助函数 ====================

def create_lazy_instance(import_path: str, name: Optional[str] = None):
    """
    从导入路径创建懒加载实例

    Args:
        import_path: 模块导入路径（如 "spacy:load"）
        name: 实例名称

    Returns:
        LazyLoader 实例

    Example:
        spacy_load = create_lazy_instance("spacy:load", "spacy")
        nlp = spacy_load("zh_core_web_sm")
    """
    def _load():
        if ":" in import_path:
            module_path, func_name = import_path.split(":", 1)
        else:
            module_path, func_name = import_path, None

        module = __import__(module_path, fromlist=[func_name] if func_name else None)

        if func_name:
            return getattr(module, func_name)
        return module

    return LazyLoader(_load, name)


def safe_import(module_name: str, lazy: bool = True):
    """
    安全导入模块（支持懒加载）

    Args:
        module_name: 模块名称
        lazy: 是否懒加载

    Returns:
        模块或懒加载器
    """
    def _import():
        try:
            return __import__(module_name)
        except ImportError as e:
            raise ImportError(f"无法导入模块 '{module_name}': {e}")

    if lazy:
        return LazyLoader(_import, module_name)
    return _import()
