# -*- coding: utf-8 -*-
"""
QualInsight Deep Analysis Page
深度分析页面
"""

import streamlit as st
from i18n import t


def render_deep_analysis():
    """
    渲染深度分析页面

    功能：
    - 情感分析
    - 话语分析
    - 叙事分析
    - 编码可靠性
    """
    st.title(f"🔬 {t('deep_analysis.title')}")

    # 检查数据
    if not st.session_state.get('raw_text'):
        st.warning(f"👈 {t('deep_analysis.no_data_warning')}")
        return

    # 分析类型选择
    tab1, tab2, tab3, tab4 = st.tabs([
        t("deep_analysis.tabs.sentiment"),
        t("deep_analysis.tabs.discourse"),
        t("deep_analysis.tabs.narrative"),
        t("deep_analysis.tabs.reliability")
    ])

    with tab1:
        _render_sentiment_analysis()

    with tab2:
        _render_discourse_analysis()

    with tab3:
        _render_narrative_analysis()

    with tab4:
        _render_reliability_analysis()


def _render_sentiment_analysis():
    """渲染情感分析"""
    st.subheader(t("deep_analysis.sentiment.title"))

    col1, col2 = st.columns([2, 1])

    with col1:
        mode = st.selectbox(
            t("deep_analysis.sentiment.mode"),
            [t("deep_analysis.sentiment.modes.overall"), t("deep_analysis.sentiment.modes.by_paragraph"), t("deep_analysis.sentiment.modes.by_code")]
        )

    with col2:
        if st.button(f"🚀 {t('deep_analysis.sentiment.start_btn')}", type="primary"):
            with st.spinner(t("deep_analysis.analyzing")):
                # TODO: 实现情感分析
                st.success(f"✅ {t('deep_analysis.sentiment.complete')}")


def _render_discourse_analysis():
    """渲染话语分析"""
    st.subheader(t("deep_analysis.discourse.title"))

    focus = st.selectbox(
        t("deep_analysis.discourse.focus"),
        [t("deep_analysis.discourse.focus_types.argument"), t("deep_analysis.discourse.focus_types.power"), t("deep_analysis.discourse.focus_types.ideology")]
    )

    if st.button(f"🔍 {t('deep_analysis.discourse.start_btn')}"):
        with st.spinner(t("deep_analysis.analyzing")):
            # TODO: 实现话语分析
            st.success(f"✅ {t('deep_analysis.discourse.complete')}")


def _render_narrative_analysis():
    """渲染叙事分析"""
    st.subheader(t("deep_analysis.narrative.title"))

    if st.button(f"📚 {t('deep_analysis.narrative.start_btn')}"):
        with st.spinner(t("deep_analysis.analyzing")):
            # TODO: 实现叙事分析
            st.success(f"✅ {t('deep_analysis.narrative.complete')}")


def _render_reliability_analysis():
    """渲染编码可靠性分析"""
    st.subheader(t("deep_analysis.reliability.title"))

    st.info(t("deep_analysis.reliability.description"))

    # 添加编码者数据
    with st.expander(t("deep_analysis.reliability.add_coder")):
        st.write(t("deep_analysis.reliability.coming_soon"))
