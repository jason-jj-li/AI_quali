# -*- coding: utf-8 -*-
"""
QualInsight 输入验证和清洗模块
提供全面的数据验证、清洗和 sanitization 功能
"""

import re
import html
from typing import Optional, List, Any, Union
from datetime import datetime
from .exceptions import DataValidationError


# ==================== 基础验证函数 ====================

def validate_required(value: Any, field_name: str = "") -> None:
    """
    验证必填字段

    Args:
        value: 要验证的值
        field_name: 字段名称

    Raises:
        DataValidationError: 如果值为空
    """
    if value is None:
        raise DataValidationError(
            f"{'字段' if not field_name else field_name}不能为空",
            field=field_name
        )

    if isinstance(value, str) and not value.strip():
        raise DataValidationError(
            f"{'字段' if not field_name else field_name}不能为空",
            field=field_name
        )

    if isinstance(value, (list, dict)) and len(value) == 0:
        raise DataValidationError(
            f"{'字段' if not field_name else field_name}不能为空",
            field=field_name
        )


def validate_length(
    value: str,
    min_length: int = 0,
    max_length: Optional[int] = None,
    field_name: str = ""
) -> None:
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
            f"{'字段' if not field_name else field_name}长度不能少于 {min_length} 个字符（当前：{length}）",
            field=field_name
        )

    if max_length and length > max_length:
        raise DataValidationError(
            f"{'字段' if not field_name else field_name}长度不能超过 {max_length} 个字符（当前：{length}）",
            field=field_name
        )


def validate_range(
    value: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    field_name: str = ""
) -> None:
    """
    验证数值范围

    Args:
        value: 要验证的数值
        min_value: 最小值
        max_value: 最大值
        field_name: 字段名称

    Raises:
        DataValidationError: 如果数值超出范围
    """
    if min_value is not None and value < min_value:
        raise DataValidationError(
            f"{'字段' if not field_name else field_name}不能小于 {min_value}（当前：{value}）",
            field=field_name
        )

    if max_value is not None and value > max_value:
        raise DataValidationError(
            f"{'字段' if not field_name else field_name}不能大于 {max_value}（当前：{value}）",
            field=field_name
        )


def validate_pattern(value: str, pattern: str, field_name: str = "") -> None:
    """
    验证字符串是否匹配正则表达式

    Args:
        value: 要验证的字符串
        pattern: 正则表达式
        field_name: 字段名称

    Raises:
        DataValidationError: 如果不匹配
    """
    if not re.match(pattern, value):
        raise DataValidationError(
            f"{'字段' if not field_name else field_name}格式不正确",
            field=field_name
        )


# ==================== 专门的验证函数 ====================

def validate_research_question(question: str) -> str:
    """
    验证并清洗研究问题

    Args:
        question: 研究问题字符串

    Returns:
        清洗后的研究问题

    Raises:
        DataValidationError: 如果验证失败
    """
    # 清洗
    question = clean_text(question)

    # 验证
    validate_required(question, "研究问题")
    validate_length(question, min_length=10, max_length=500, field_name="研究问题")

    # 检查是否包含问号或疑问词
    question_words = ["如何", "为什么", "什么", "怎样", "是否", "how", "why", "what", "whether"]
    has_question_mark = "?" in question or "？" in question
    has_question_word = any(word in question.lower() for word in question_words)

    if not (has_question_mark or has_question_word):
        # 不强制要求，但给出警告
        pass

    return question


def validate_text_content(text: str, min_length: int = 50) -> str:
    """
    验证并清洗文本内容

    Args:
        text: 文本内容
        min_length: 最小长度

    Returns:
        清洗后的文本

    Raises:
        DataValidationError: 如果验证失败
    """
    # 清洗
    text = clean_text(text)

    # 验证
    validate_required(text, "文本内容")
    validate_length(text, min_length=min_length, field_name="文本内容")

    # 检查中文字符占比
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(text.strip())
    if total_chars > 0:
        chinese_ratio = chinese_chars / total_chars
        if chinese_ratio < 0.1:
            # 至少10%的中文字符（或者允许纯英文）
            pass

    return text


def validate_code_name(name: str) -> str:
    """
    验证编码名称

    Args:
        name: 编码名称

    Returns:
        清洗后的名称
    """
    name = clean_text(name)
    validate_required(name, "编码名称")
    validate_length(name, min_length=2, max_length=100, field_name="编码名称")
    return name


def validate_theme_name(name: str) -> str:
    """
    验证主题名称

    Args:
        name: 主题名称

    Returns:
        清洗后的名称
    """
    name = clean_text(name)
    validate_required(name, "主题名称")
    validate_length(name, min_length=2, max_length=100, field_name="主题名称")
    return name


def validate_api_key(api_key: str) -> str:
    """
    验证API密钥格式

    Args:
        api_key: API密钥

    Returns:
        清洗后的API密钥

    Raises:
        DataValidationError: 如果格式不正确
    """
    if not api_key or not api_key.strip():
        raise DataValidationError("API密钥不能为空", field="API密钥")

    api_key = api_key.strip()

    # 基本长度验证
    if len(api_key) < 20:
        raise DataValidationError(
            f"API密钥长度不足（至少需要20个字符，当前：{len(api_key)}）",
            field="API密钥"
        )

    # 检查是否包含字母和数字
    has_letter = any(c.isalpha() for c in api_key)
    has_digit = any(c.isdigit() for c in api_key)

    if not (has_letter and has_digit):
        raise DataValidationError(
            "API密钥格式不正确，应包含字母和数字",
            field="API密钥"
        )

    return api_key


def validate_email(email: str) -> str:
    """
    验证电子邮件格式

    Args:
        email: 电子邮件地址

    Returns:
        清洗后的电子邮件
    """
    email = clean_text(email)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if email and not re.match(email_pattern, email):
        raise DataValidationError("电子邮件格式不正确", field="电子邮件")

    return email


def validate_url(url: str) -> str:
    """
    验证URL格式

    Args:
        url: URL字符串

    Returns:
        清洗后的URL
    """
    url = clean_text(url)

    if url and not (url.startswith('http://') or url.startswith('https://')):
        raise DataValidationError("URL必须以 http:// 或 https:// 开头", field="URL")

    return url


# ==================== 清洗函数 ====================

def clean_text(text: str) -> str:
    """
    清洗文本内容

    Args:
        text: 要清洗的文本

    Returns:
        清洗后的文本
    """
    if not text:
        return ""

    # 解码HTML实体
    text = html.unescape(text)

    # 移除控制字符（保留换行和制表符）
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # 规范化空白字符
    text = re.sub(r'[ \t]+', ' ', text)  # 多个空格/制表符 -> 单个空格
    text = re.sub(r'\n{3,}', '\n\n', text)  # 多个换行 -> 最多两个

    # 去除首尾空白
    text = text.strip()

    return text


def sanitize_html(text: str) -> str:
    """
    移除潜在的HTML标签（保留安全内容）

    Args:
        text: 可能包含HTML的文本

    Returns:
        移除HTML标签的文本
    """
    if not text:
        return ""

    # 移除脚本和样式
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)

    # 移除所有HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # 解码HTML实体
    text = html.unescape(text)

    return text


def remove_extra_whitespaces(text: str) -> str:
    """
    移除多余的空白字符

    Args:
        text: 要处理的文本

    Returns:
        处理后的文本
    """
    if not text:
        return ""

    # 移除所有空白字符
    text = re.sub(r'\s+', '', text)

    return text


def normalize_quotes(text: str) -> str:
    """
    规范化引号

    Args:
        text: 要处理的文本

    Returns:
        规范化后的文本
    """
    if not text:
        return ""

    # 中文引号互换
    text = text('"', '"')
    text = text('"', '"')
    text = text(''', "'")
    text = text(''', "'")

    return text


# ==================== 批量验证 ====================

def validate_batch(items: List[Any], validator_func, field_name: str = "") -> List[Any]:
    """
    批量验证列表中的项目

    Args:
        items: 要验证的项目列表
        validator_func: 验证函数
        field_name: 字段名称

    Returns:
        验证后的项目列表

    Raises:
        DataValidationError: 如果任一项目验证失败
    """
    validated_items = []
    errors = []

    for i, item in enumerate(items):
        try:
            validated_item = validator_func(item)
            validated_items.append(validated_item)
        except DataValidationError as e:
            errors.append(f"项目 {i + 1}: {e.message}")

    if errors:
        raise DataValidationError(
            f"批量验证失败:\n" + "\n".join(errors),
            field=field_name
        )

    return validated_items


# ==================== 条件验证 ====================

class ValidationBuilder:
    """
    验证构建器 - 支持链式调用
    """

    def __init__(self, value: Any, field_name: str = ""):
        self.value = value
        self.field_name = field_name
        self.errors = []

    def required(self) -> 'ValidationBuilder':
        """验证必填"""
        try:
            validate_required(self.value, self.field_name)
        except DataValidationError as e:
            self.errors.append(e.message)
        return self

    def length(self, min_length: int = 0, max_length: Optional[int] = None) -> 'ValidationBuilder':
        """验证长度"""
        try:
            validate_length(self.value, min_length, max_length, self.field_name)
        except DataValidationError as e:
            self.errors.append(e.message)
        return self

    def pattern(self, pattern: str) -> 'ValidationBuilder':
        """验证正则"""
        try:
            validate_pattern(self.value, pattern, self.field_name)
        except DataValidationError as e:
            self.errors.append(e.message)
        return self

    def custom(self, validator_func, *args, **kwargs) -> 'ValidationBuilder':
        """自定义验证函数"""
        try:
            validator_func(self.value, *args, **kwargs)
        except DataValidationError as e:
            self.errors.append(e.message)
        return self

    def validate(self) -> Any:
        """
        执行所有验证

        Returns:
            验证通过的值

        Raises:
            DataValidationError: 如果有任何验证失败
        """
        if self.errors:
            raise DataValidationError(
                "\n".join(self.errors),
                field=self.field_name
            )

        return self.value


def validate(value: Any, field_name: str = "") -> ValidationBuilder:
    """
    创建验证构建器

    Args:
        value: 要验证的值
        field_name: 字段名称

    Returns:
        ValidationBuilder 实例

    Example:
        validate(email, "电子邮件").required().pattern(r'^[^@]+@[^@]+$').validate()
    """
    return ValidationBuilder(value, field_name)


# ==================== 辅助函数 ====================

def is_empty(value: Any) -> bool:
    """检查值是否为空"""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, dict, tuple)) and len(value) == 0:
        return True
    return False


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断文本到指定长度

    Args:
        text: 要截断的文本
        max_length: 最大长度
        suffix: 截断后添加的后缀

    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def safe_int(value: Any, default: int = 0) -> int:
    """
    安全转换为整数

    Args:
        value: 要转换的值
        default: 转换失败时的默认值

    Returns:
        整数
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全转换为浮点数

    Args:
        value: 要转换的值
        default: 转换失败时的默认值

    Returns:
        浮点数
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
