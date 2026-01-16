# -*- coding: utf-8 -*-
"""
QualInsight 国际化模块
提供中英文翻译支持

使用示例:
    from i18n import t, set_language, get_current_language

    # 翻译文本
    st.write(t("nav.home"))  # 首页 / Dashboard

    # 带参数的翻译
    st.write(t("welcome", name="用户"))

    # 获取当前语言
    lang = get_current_language()  # 'zh_CN' or 'en_US'

    # 切换语言
    set_language('en_US')
"""

from .translator import (
    # 核心翻译函数
    t,
    tn,

    # 语言管理
    get_current_language,
    set_language,
    get_available_languages,
    get_language_name,
    is_rtl,

    # 翻译辅助
    translate_list,
    translate_dict,
    format_translation,

    # UI组件
    render_language_switch,
    render_language_selector,

    # 翻译文件管理
    reload_translations,
    get_translation_coverage,
    list_missing_translations,

    # 调试工具
    show_translation_debug_info,
)

__all__ = [
    # 核心翻译函数
    't',
    'tn',

    # 语言管理
    'get_current_language',
    'set_language',
    'get_available_languages',
    'get_language_name',
    'is_rtl',

    # 翻译辅助
    'translate_list',
    'translate_dict',
    'format_translation',

    # UI组件
    'render_language_switch',
    'render_language_selector',

    # 翻译文件管理
    'reload_translations',
    'get_translation_coverage',
    'list_missing_translations',

    # 调试工具
    'show_translation_debug_info',
]
