# -*- coding: utf-8 -*-
"""
QualInsight 国际化翻译模块
提供中英文翻译支持
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st


# ==================== 翻译缓存 ====================

_translations: Dict[str, Dict[str, Any]] = {}


# ==================== 翻译文件加载 ====================

def load_translations(lang: str) -> Dict[str, Any]:
    """
    加载指定语言的翻译文件

    Args:
        lang: 语言代码 (zh_CN, en_US)

    Returns:
        翻译字典
    """
    global _translations

    if lang in _translations:
        return _translations[lang]

    translation_file = Path(__file__).parent / "translations" / f"{lang}.json"

    if translation_file.exists():
        with open(translation_file, 'r', encoding='utf-8') as f:
            _translations[lang] = json.load(f)
    else:
        _translations[lang] = {}

    return _translations[lang]


# ==================== 核心翻译函数 ====================

def t(key: str, **kwargs) -> str:
    """
    翻译函数 - 根据当前语言返回对应文本

    Args:
        key: 翻译键（支持嵌套，如 "nav.home"）
        **kwargs: 格式化参数

    Returns:
        翻译后的文本

    Examples:
        >>> t("nav.home")
        "首页"
        >>> t("welcome", name="用户")
        "欢迎，用户"
        >>> t("app.title")
        "QualInsight"
    """
    lang = get_current_language()
    translations = load_translations(lang)

    # 支持嵌套键 (如 "nav.dashboard")
    keys = key.split('.')
    result = translations

    for k in keys:
        if isinstance(result, dict) and k in result:
            result = result[k]
        else:
            # 找不到翻译，返回 key 本身
            return key

    # 支持参数格式化
    if kwargs and isinstance(result, str):
        try:
            return result.format(**kwargs)
        except (KeyError, ValueError):
            return result

    return result if isinstance(result, str) else key


def tn(key: str, count: int, **kwargs) -> str:
    """
    复数形式翻译函数

    Args:
        key: 翻译键
        count: 数量
        **kwargs: 格式化参数

    Returns:
        翻译后的文本（带复数处理）

    Examples:
        >>> tn("item", 1)
        "1 项"
        >>> tn("item", 5)
        "5 项"
    """
    lang = get_current_language()

    # 根据数量选择不同的键
    if lang == 'zh_CN':
        # 中文通常没有复数变化
        result_key = key
    else:
        # 英文复数处理
        if count == 1:
            result_key = f"{key}.singular"
        else:
            result_key = f"{key}.plural"

    return t(result_key, count=count, **kwargs)


# ==================== 语言管理 ====================

def get_current_language() -> str:
    """获取当前语言代码"""
    return st.session_state.get('lang', 'zh_CN')


def set_language(lang: str):
    """
    设置语言并重新加载页面

    Args:
        lang: 语言代码 (zh_CN, en_US)
    """
    if lang in get_available_languages():
        st.session_state.lang = lang
        st.rerun()


def get_available_languages() -> Dict[str, str]:
    """
    获取可用语言列表

    Returns:
        {语言代码: 显示名称}
    """
    return {
        'zh_CN': '🇨🇳 中文',
        'en_US': '🇺🇸 English',
    }


def get_language_name(lang: str) -> str:
    """获取语言显示名称"""
    languages = get_available_languages()
    return languages.get(lang, lang)


def is_rtl(language: Optional[str] = None) -> bool:
    """
    检查语言是否为从右到左（RTL）书写

    Args:
        language: 语言代码（默认使用当前语言）

    Returns:
        是否为 RTL 语言
    """
    if language is None:
        language = get_current_language()

    rtl_languages = {'ar', 'he', 'fa', 'ur'}
    return language in rtl_languages


# ==================== 翻译辅助函数 ====================

def translate_list(keys: list[str]) -> list[str]:
    """
    批量翻译列表

    Args:
        keys: 翻译键列表

    Returns:
        翻译结果列表
    """
    return [t(key) for key in keys]


def translate_dict(keys: Dict[str, str]) -> Dict[str, str]:
    """
    批量翻译字典

    Args:
        keys: {标识: 翻译键}

    Returns:
        {标识: 翻译结果}
    """
    return {k: t(v) for k, v in keys.items()}


def format_translation(key: str, **kwargs) -> str:
    """
    格式化翻译（带参数）

    Args:
        key: 翻译键
        **kwargs: 格式化参数

    Returns:
        格式化后的翻译文本
    """
    return t(key, **kwargs)


# ==================== 语言切换组件 ====================

def render_language_switch(position: str = "sidebar") -> None:
    """
    渲染语言切换按钮

    Args:
        position: 位置 ("sidebar", "top", "bottom")
    """
    current_lang = get_current_language()
    languages = get_available_languages()
    lang_codes = list(languages.keys())

    # 找到下一个语言
    current_index = lang_codes.index(current_lang)
    next_lang = lang_codes[(current_index + 1) % len(lang_codes)]

    button_label = f"🌐 {languages[next_lang]}"

    if position == "sidebar":
        if st.sidebar.button(button_label, key="lang_switch_sidebar", use_container_width=True):
            set_language(next_lang)
    else:
        if st.button(button_label, key="lang_switch_top"):
            set_language(next_lang)


def render_language_selector() -> None:
    """
    渲染语言选择器（下拉框）
    """
    languages = get_available_languages()
    current_lang = get_current_language()

    # 使用 selectbox 显示语言列表
    lang_names = list(languages.values())
    lang_codes = list(languages.keys())
    current_index = lang_codes.index(current_lang)

    selected_index = st.sidebar.selectbox(
        t("language.select"),
        range(len(lang_names)),
        format_func=lambda i: lang_names[i],
        index=current_index
    )

    if selected_index != current_index:
        set_language(lang_codes[selected_index])


# ==================== 翻译文件管理 ====================

def reload_translations(lang: Optional[str] = None) -> None:
    """
    重新加载翻译文件

    Args:
        lang: 指定语言（None 则重新加载所有）
    """
    global _translations

    if lang:
        if lang in _translations:
            del _translations[lang]
            load_translations(lang)
    else:
        _translations.clear()


def get_translation_coverage(lang: str) -> Dict[str, Any]:
    """
    获取翻译覆盖率统计

    Args:
        lang: 语言代码

    Returns:
        {总键数, 已翻译数, 覆盖率}
    """
    translations = load_translations(lang)
    base_translations = load_translations('zh_CN')

    def count_keys(d: Dict) -> int:
        count = 0
        for v in d.values():
            if isinstance(v, dict):
                count += count_keys(v)
            else:
                count += 1
        return count

    total = count_keys(base_translations)
    translated = count_keys(translations)

    return {
        'total': total,
        'translated': translated,
        'coverage': translated / total if total > 0 else 0,
    }


# ==================== 调试工具 ====================

def list_missing_translations(lang: str) -> list[str]:
    """
    列出缺失的翻译键

    Args:
        lang: 语言代码

    Returns:
        缺失的翻译键列表
    """
    base_translations = load_translations('zh_CN')
    target_translations = load_translations(lang)

    missing = []

    def check_missing(base: Dict, target: Dict, prefix: str = ""):
        for key, value in base.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if key not in target:
                missing.append(full_key)
            elif isinstance(value, dict):
                check_missing(value, target[key], full_key)

    check_missing(base_translations, target_translations)
    return missing


def show_translation_debug_info() -> None:
    """在 Streamlit 中显示翻译调试信息"""
    if not st.session_state.get('debug_mode', False):
        return

    st.write("### 🔍 翻译调试信息")

    current_lang = get_current_language()
    st.write(f"**当前语言**: {current_lang}")

    # 覆盖率统计
    for lang in get_available_languages().keys():
        coverage = get_translation_coverage(lang)
        st.write(f"**{lang}**: {coverage['translated']}/{coverage['total']} ({coverage['coverage']:.1%})")

    # 缺失翻译
    missing = list_missing_translations(current_lang)
    if missing:
        st.write(f"**缺失翻译** ({len(missing)}):")
        for key in missing[:10]:  # 只显示前10个
            st.write(f"- {key}")
        if len(missing) > 10:
            st.write(f"... 还有 {len(missing) - 10} 个")
