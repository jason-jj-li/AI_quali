# -*- coding: utf-8 -*-
"""
QualInsight 统一异常处理系统
提供自定义异常类和错误处理工具函数
"""

import streamlit as st
import traceback
from typing import Optional, Callable
from functools import wraps


# ==================== 自定义异常类 ====================

class QualInsightError(Exception):
    """QualInsight 基础异常类"""
    def __init__(self, message: str, user_message: Optional[str] = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)


class LLMError(QualInsightError):
    """LLM 调用相关异常"""
    def __init__(self, message: str, provider: str = ""):
        self.provider = provider
        user_msg = f"AI分析失败: {message}"
        if provider:
            user_msg += f" (服务商: {provider})"
        super().__init__(message, user_msg)


class DataValidationError(QualInsightError):
    """数据验证异常"""
    def __init__(self, message: str, field: str = ""):
        self.field = field
        user_msg = f"数据验证失败: {message}"
        if field:
            user_msg += f" (字段: {field})"
        super().__init__(message, user_msg)


class DataPersistenceError(QualInsightError):
    """数据持久化异常"""
    def __init__(self, message: str):
        user_msg = f"数据保存失败: {message}"
        super().__init__(message, user_msg)


class ConfigurationError(QualInsightError):
    """配置相关异常"""
    def __init__(self, message: str):
        user_msg = f"配置错误: {message}"
        super().__init__(message, user_msg)


class ProcessingError(QualInsightError):
    """数据处理异常"""
    def __init__(self, message: str, step: str = ""):
        self.step = step
        user_msg = f"处理失败: {message}"
        if step:
            user_msg += f" (步骤: {step})"
        super().__init__(message, user_msg)


class NetworkError(QualInsightError):
    """网络相关异常"""
    def __init__(self, message: str):
        user_msg = f"网络连接失败: {message}"
        super().__init__(message, user_msg)


class FileOperationError(QualInsightError):
    """文件操作异常"""
    def __init__(self, message: str, filename: str = ""):
        self.filename = filename
        user_msg = f"文件操作失败: {message}"
        if filename:
            user_msg += f" (文件: {filename})"
        super().__init__(message, user_msg)


# ==================== 错误处理工具函数 ====================

def handle_error(
    error: Exception,
    show_details: bool = False,
    context: str = ""
) -> None:
    """
    统一的错误处理和显示函数

    Args:
        error: 捕获的异常对象
        show_details: 是否显示详细错误信息（开发模式）
        context: 错误发生的上下文信息
    """
    # 如果是自定义异常，使用用户友好的消息
    if isinstance(error, QualInsightError):
        user_message = error.user_message
        suggestion = _get_error_suggestion(error)
    else:
        # 对于未知异常，提供通用消息
        user_message = f"操作失败: {str(error)}"
        suggestion = _get_generic_suggestion(error)

    # 显示错误消息
    error_msg = f"❌ {user_message}"
    if context:
        error_msg = f"❌ [{context}] {user_message}"

    st.error(error_msg)

    # 显示建议
    if suggestion:
        st.caption(f"💡 {suggestion}")

    # 在开发模式下显示详细信息
    if show_details or st.session_state.get('debug_mode', False):
        with st.expander("🔧 技术详情（开发模式）"):
            st.code(f"异常类型: {type(error).__name__}\n"
                   f"错误消息: {str(error)}\n\n"
                   f"堆栈追踪:\n{''.join(traceback.format_exception(type(error), error, error.__traceback__))}",
                   language="python")


def _get_error_suggestion(error: QualInsightError) -> str:
    """根据异常类型返回针对性建议"""
    suggestions = {
        LLMError: "请检查：①API密钥是否正确 ②网络连接是否正常 ③服务商配额是否充足",
        DataValidationError: "请检查输入数据格式是否正确，确保所有必填字段都已填写",
        DataPersistenceError: "建议手动保存当前数据，避免数据丢失",
        ConfigurationError: "请检查侧边栏配置设置，确保所有参数填写正确",
        ProcessingError: "尝试刷新页面或重新执行该操作",
        NetworkError: "请检查网络连接，或稍后重试",
        FileOperationError: "请检查文件路径是否正确，确保有读写权限",
    }
    return suggestions.get(type(error), "")


def _get_generic_suggestion(error: Exception) -> str:
    """为未知异常返回通用建议"""
    error_type = type(error).__name__

    # 常见错误的针对性建议
    if "Connection" in error_type or "Timeout" in error_type:
        return "请检查网络连接，或稍后重试"
    elif "KeyError" in error_type or "IndexError" in error_type:
        return "数据格式可能存在问题，请重新输入"
    elif "ValueError" in error_type:
        return "输入值可能不正确，请检查并重新输入"
    elif "Permission" in error_type:
        return "请检查文件或目录的访问权限"
    else:
        return "如果问题持续，请联系技术支持或刷新页面重试"


def safe_execute(
    func: Callable,
    error_message: str = "操作失败",
    context: str = "",
    show_details: bool = False,
    default_return=None
):
    """
    安全执行函数，自动处理异常

    Args:
        func: 要执行的函数
        error_message: 错误消息前缀
        context: 上下文信息
        show_details: 是否显示详细错误
        default_return: 发生异常时的默认返回值

    Returns:
        函数执行结果或默认返回值
    """
    try:
        return func()
    except Exception as e:
        handle_error(e, show_details=show_details, context=context)
        return default_return


def handle_llm_error(
    error: Exception,
    provider: str = "",
    show_details: bool = False
) -> None:
    """
    专门处理LLM调用错误的函数

    Args:
        error: 捕获的异常
        provider: LLM服务商名称
        show_details: 是否显示详细信息
    """
    # 转换为自定义异常
    if not isinstance(error, LLMError):
        error = LLMError(str(error), provider)

    handle_error(error, show_details=show_details)


# ==================== 装饰器 ====================

def catch_errors(
    context: str = "",
    show_details: bool = False,
    default_return=None,
    reraise: bool = False
):
    """
    异常捕获装饰器

    Args:
        context: 操作上下文
        show_details: 是否显示详细信息
        default_return: 异常时的默认返回值
        reraise: 是否重新抛出异常
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except QualInsightError as e:
                handle_error(e, show_details=show_details, context=context or func.__name__)
                if reraise:
                    raise
                return default_return
            except Exception as e:
                handle_error(e, show_details=show_details, context=context or func.__name__)
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator


def with_error_handling(error_type: type = QualInsightError, message: str = ""):
    """
    简化的错误处理装饰器

    Args:
        error_type: 要捕获的异常类型
        message: 自定义错误消息
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if message:
                    error = error_type(f"{message}: {str(e)}")
                else:
                    error = error_type(str(e))
                handle_error(error)
                return None
        return wrapper
    return decorator


# ==================== Streamlit 专用 ====================

class ErrorContainer:
    """错误容器，用于批量收集和显示错误"""

    def __init__(self):
        self.errors = []

    def add(self, error: Exception, context: str = ""):
        """添加错误"""
        self.errors.append((error, context))

    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.errors) > 0

    def display(self):
        """显示所有收集的错误"""
        if not self.has_errors():
            return

        st.error(f"❌ 发现 {len(self.errors)} 个问题:")

        for i, (error, context) in enumerate(self.errors, 1):
            with st.expander(f"问题 {i}: {context}"):
                if isinstance(error, QualInsightError):
                    st.write(error.user_message)
                    st.caption(_get_error_suggestion(error))
                else:
                    st.write(str(error))
                    st.caption(_get_generic_suggestion(error))

    def clear(self):
        """清空错误列表"""
        self.errors.clear()


# ==================== 辅助函数 ====================

def validate_required(value, field_name: str = ""):
    """
    验证必填字段

    Args:
        value: 要验证的值
        field_name: 字段名称

    Raises:
        DataValidationError: 如果值为空
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise DataValidationError(
            f"{'字段' if not field_name else field_name}不能为空",
            field=field_name
        )


def validate_length(value: str, min_length: int = 0, max_length: int = None, field_name: str = ""):
    """
    验证字符串长度

    Args:
        value: 要验证的字符串
        min_length: 最小长度
        max_length: 最大长度
        field_name: 字段名称

    Raises:
        DataValidationError: 如果长度不符合要求
    """
    length = len(value)

    if length < min_length:
        raise DataValidationError(
            f"{'字段' if not field_name else field_name}长度不能少于 {min_length} 个字符",
            field=field_name
        )

    if max_length and length > max_length:
        raise DataValidationError(
            f"{'字段' if not field_name else field_name}长度不能超过 {max_length} 个字符",
            field=field_name
        )


def is_api_key_valid(api_key: str) -> bool:
    """
    简单的API密钥格式验证

    Args:
        api_key: API密钥字符串

    Returns:
        bool: 是否看起来像有效的API密钥
    """
    if not api_key or not api_key.strip():
        return False

    # 常见API密钥格式：至少20个字符，包含字母和数字
    api_key = api_key.strip()
    if len(api_key) < 20:
        return False

    has_letter = any(c.isalpha() for c in api_key)
    has_digit = any(c.isdigit() for c in api_key)

    return has_letter and has_digit
