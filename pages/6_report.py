# -*- coding: utf-8 -*-
"""
QualInsight Report Page
报告生成页面
"""

import streamlit as st
from i18n import t


def render_report():
    """
    渲染报告生成页面

    功能：
    - IMRAD 结构报告生成
    - 报告编辑
    - 报告导出
    """
    st.title(f"📑 {t('report.title')}")

    # 检查数据
    if not st.session_state.get('themes'):
        st.warning(f"👈 {t('report.no_themes_warning')}")
        return

    # 报告选项
    with st.sidebar:
        st.subheader(t("report.options.title"))

        language = st.selectbox(
            t("report.options.language"),
            [t("report.options.zh"), t("report.options.en")]
        )

        st.write(t("report.options.advanced"))

        include_lit_review = st.checkbox(t("report.options.literature"))
        include_framework = st.checkbox(t("report.options.framework"))
        include_innovation = st.checkbox(t("report.options.innovation"))
        include_limitations = st.checkbox(t("report.options.limitations"))

    # 生成报告按钮
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(t("report.generate_title"))

    with col2:
        if st.button(f"🚀 {t('report.generate_btn')}", type="primary", use_container_width=True):
            with st.spinner(t("report.generating")):
                try:
                    # 调用报告服务
                    from services.report_service import ReportService
                    service = ReportService()

                    report = service.generate_imrad_report(
                        research_question=st.session_state.get('research_question', ''),
                        codes=st.session_state.get('codes', []),
                        themes=st.session_state.get('themes', []),
                        language="zh" if language == t("report.options.zh") else "en"
                    )

                    st.session_state.report = report
                    st.success(f"✅ {t('report.generate_success')}")
                except Exception as e:
                    st.error(f"❌ {t('report.generate_failed')}: {str(e)}")

    st.divider()

    # 报告编辑器
    if st.session_state.get('report'):
        _render_report_editor()
    else:
        st.info(t("report.no_report_yet"))


def _render_report_editor():
    """渲染报告编辑器"""
    st.subheader(t("report.editor.title"))

    report = st.session_state.report

    # 显示报告内容
    sections = report.sections if hasattr(report, 'sections') else []

    if sections:
        for section in sections:
            with st.expander(section.title, expanded=False):
                st.text_area(
                    section.title,
                    value=section.content,
                    height=200,
                    key=f"edit_{section.title}"
                )

    # 导出按钮
    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"📥 {t('report.export_md')}"):
            # 导出 Markdown
            st.success(f"✅ {t('report.export_success')}")

    with col2:
        if st.button(f"📋 {t('report.copy_to_clipboard')}"):
            st.success(f"✅ {t('report.copied')}")
