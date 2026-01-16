# -*- coding: utf-8 -*-
"""
QualInsight 工具模块
"""

from .exceptions import (
    QualInsightError,
    LLMError,
    DataValidationError,
    DataPersistenceError,
    ConfigurationError,
    ProcessingError,
    NetworkError,
    FileOperationError,
    handle_error,
    handle_llm_error,
    safe_execute,
    catch_errors,
    with_error_handling,
    ErrorContainer,
    validate_required,
    validate_length,
    is_api_key_valid,
)

from .validators import (
    validate_research_question,
    validate_text_content,
    validate_code_name,
    validate_theme_name,
    validate_api_key,
    validate_email,
    validate_url,
    clean_text,
    sanitize_html,
    normalize_quotes,
    validate_batch,
    validate,
    is_empty,
    truncate,
    safe_int,
    safe_float,
)

from .cache import (
    cached,
    cached_llm,
    clear_cache,
    get_cache_stats,
    show_cache_stats,
    SimpleCache,
)

__all__ = [
    # 异常处理
    "QualInsightError",
    "LLMError",
    "DataValidationError",
    "DataPersistenceError",
    "ConfigurationError",
    "ProcessingError",
    "NetworkError",
    "FileOperationError",
    "handle_error",
    "handle_llm_error",
    "safe_execute",
    "catch_errors",
    "with_error_handling",
    "ErrorContainer",
    "validate_required",
    "validate_length",
    "is_api_key_valid",
    # 输入验证
    "validate_research_question",
    "validate_text_content",
    "validate_code_name",
    "validate_theme_name",
    "validate_api_key",
    "validate_email",
    "validate_url",
    "clean_text",
    "sanitize_html",
    "normalize_quotes",
    "validate_batch",
    "validate",
    "is_empty",
    "truncate",
    "safe_int",
    "safe_float",
    # 缓存
    "cached",
    "cached_llm",
    "clear_cache",
    "get_cache_stats",
    "show_cache_stats",
    "SimpleCache",
]
