# -*- coding: utf-8 -*-
"""
QualInsight Visualization Page
可视化页面
"""

import streamlit as st
from i18n import t
import plotly.graph_objects as go
import plotly.express as px


def render_visualization():
    """
    渲染可视化页面

    功能：
    - 编码-文档热力图
    - 主题层级旭日图
    - 时间线可视化
    - 网络图
    """
    st.title(f"📊 {t('viz.title')}")

    # 检查数据
    codes = st.session_state.get('codes', [])
    themes = st.session_state.get('themes', [])

    if not codes and not themes:
        st.warning(f"👈 {t('viz.no_data_warning')}")
        st.info(t("viz.complete_analysis_first"))
        return

    # 可视化类型选择
    viz_type = st.selectbox(
        t("viz.choose_type"),
        [
            t("viz.types.heatmap"),
            t("viz.types.sunburst"),
            t("viz.types.timeline"),
            t("viz.types.network"),
            t("viz.types.bar")
        ]
    )

    if viz_type == t("viz.types.heatmap"):
        _render_heatmap()

    elif viz_type == t("viz.types.sunburst"):
        _render_sunburst()

    elif viz_type == t("viz.types.timeline"):
        _render_timeline()

    elif viz_type == t("viz.types.network"):
        _render_network()

    elif viz_type == t("viz.types.bar"):
        _render_bar_chart()


def _render_heatmap():
    """渲染热力图"""
    st.subheader(t("viz.heatmap.title"))

    codes = st.session_state.get('codes', [])

    if not codes:
        st.info(t("viz.heatmap.no_codes"))
        return

    # TODO: 实现热力图
    st.info(t("viz.coming_soon"))


def _render_sunburst():
    """渲染旭日图"""
    st.subheader(t("viz.sunburst.title"))

    themes = st.session_state.get('themes', [])

    if not themes:
        st.info(t("viz.sunburst.no_themes"))
        return

    # TODO: 实现旭日图
    st.info(t("viz.coming_soon"))


def _render_timeline():
    """渲染时间线"""
    st.subheader(t("viz.timeline.title"))
    st.info(t("viz.coming_soon"))


def _render_network():
    """渲染网络图"""
    st.subheader(t("viz.network.title"))
    st.info(t("viz.coming_soon"))


def _render_bar_chart():
    """渲染柱状图"""
    st.subheader(t("viz.bar.title"))

    codes = st.session_state.get('codes', [])

    if not codes:
        st.info(t("viz.bar.no_codes"))
        return

    # 提取编码名称和引用数
    code_names = [c.get('name', 'N/A') for c in codes]
    quote_counts = [len(c.get('quotes', [])) for c in codes]

    # 创建柱状图
    fig = px.bar(
        x=code_names,
        y=quote_counts,
        labels={'x': t("viz.bar.x_label"), 'y': t("viz.bar.y_label")},
        title=t("viz.bar.title")
    )

    st.plotly_chart(fig, use_container_width=True)
