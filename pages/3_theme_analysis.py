# -*- coding: utf-8 -*-
"""
QualInsight Theme Analysis Page
主题分析页面
"""

import streamlit as st
from i18n import t


def render_theme_analysis():
    """
    渲染主题分析页面

    功能：
    - AI 主题识别
    - 主题层级管理
    - 主题关系分析
    - 跨案例分析
    """
    st.title(f"🎯 {t('theme.title')}")

    # 检查数据
    if not st.session_state.get('codes'):
        st.warning(f"👈 {t('theme.no_codes_warning')}")
        st.info(t("theme.complete_coding_first"))
        return

    # 开始主题识别按钮
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(t("theme.identify_title"))

    with col2:
        if st.button(f"🚀 {t('theme.start_ai_identify')}", type="primary", use_container_width=True):
            with st.spinner(t("theme.analyzing")):
                try:
                    # 获取编码数据
                    codes = st.session_state.get('codes', [])
                    research_question = st.session_state.get('research_question', '')

                    if not codes:
                        st.warning(t("theme.no_codes_warning"))
                        return

                    # 获取AI主题助手（使用正确的模型名称）
                    from src.llm.theme_assistant import get_ai_theme_assistant
                    assistant = get_ai_theme_assistant(model="qwen/qwen3-next-80b")

                    # 调用主题服务
                    from services.theme_service import ThemeService
                    service = ThemeService()

                    # 使用 AI 识别主题
                    results = assistant.identify_themes_from_codes(
                        codes=codes,
                        research_question=research_question,
                        max_themes=8,
                        approach="主题分析法"
                    )

                    # 保存主题到服务
                    for result in results:
                        if result.name and result.name != "错误":
                            # 准备引用数据
                            quotes = []
                            for quote_text in result.quotes[:3]:
                                quotes.append({
                                    "text": quote_text,
                                    "context": result.description
                                })

                            # 创建主题
                            service.create_theme(
                                name=result.name,
                                definition=result.definition or result.description,
                                supporting_quotes=quotes,
                                related_codes=result.related_codes
                            )

                    # 更新session state
                    st.session_state['themes'] = [t.to_dict() for t in service.get_all_themes()]

                    st.success(f"✅ {t('theme.identify_complete')} {len(results)} 个主题")

                except Exception as e:
                    import traceback
                    st.error(f"❌ {t('theme.identify_failed')}: {str(e)}")
                    st.error(traceback.format_exc())

    st.divider()

    # 主题管理标签页
    tab1, tab2, tab3 = st.tabs([
        t("theme.tabs.themes"),
        t("theme.tabs.relationships"),
        t("theme.tabs.cross_case")
    ])

    with tab1:
        _render_themes_list()

    with tab2:
        _render_relationships()

    with tab3:
        _render_cross_case_analysis()


def _render_themes_list():
    """渲染主题列表"""
    st.subheader(t("theme.themes_list.title"))

    themes = st.session_state.get('themes', [])

    if not themes:
        st.info(t("theme.themes_list.no_themes"))
        return

    for theme in themes:
        with st.expander(f"🎯 {theme.get('name', 'N/A')}", expanded=False):
            st.write(f"**{t('theme.definition')}**: {theme.get('definition', '')}")
            if theme.get('supporting_quotes'):
                st.write(f"**{t('theme.supporting_quotes')}** ({len(theme['supporting_quotes'])})")


def _render_relationships():
    """渲染主题关系"""
    st.subheader(t("theme.relationships.title"))

    if st.button(f"🔍 {t('theme.relationships.analyze_btn')}"):
        with st.spinner(t("theme.relationships.analyzing")):
            # TODO: 实现关系分析
            st.success(f"✅ {t('theme.relationships.analyze_complete')}")


def _render_cross_case_analysis():
    """渲染跨案例分析"""
    st.subheader(t("theme.cross_case.title"))

    st.info(t("theme.cross_case.coming_soon"))
