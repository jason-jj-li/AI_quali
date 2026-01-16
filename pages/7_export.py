# -*- coding: utf-8 -*-
"""
QualInsight Export Page
导出下载页面
"""

import streamlit as st
from i18n import t
import json
from io import StringIO


def render_export():
    """
    渲染导出下载页面

    功能：
    - 编码本导出
    - 主题导出
    - 报告导出
    - 完整项目打包
    """
    st.title(f"💾 {t('export.title')}")

    # 导出选项标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        t("export.tabs.codebook"),
        t("export.tabs.themes"),
        t("export.tabs.report"),
        t("export.tabs.full_project")
    ])

    with tab1:
        _render_codebook_export()

    with tab2:
        _render_themes_export()

    with tab3:
        _render_report_export()

    with tab4:
        _render_full_project_export()


def _render_codebook_export():
    """渲染编码本导出"""
    st.subheader(t("export.codebook.title"))

    codes = st.session_state.get('codes', [])

    if not codes:
        st.info(t("export.codebook.no_codes"))
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(f"📊 {t('export.codebook.csv')}"):
            csv_data = _export_codes_csv(codes)
            st.download_button(
                label=t("export.download"),
                data=csv_data,
                file_name="codebook.csv",
                mime="text/csv"
            )

    with col2:
        if st.button(f"📋 {t('export.codebook.json')}"):
            json_data = json.dumps(codes, ensure_ascii=False, indent=2)
            st.download_button(
                label=t("export.download"),
                data=json_data,
                file_name="codebook.json",
                mime="application/json"
            )

    with col3:
        if st.button(f"📄 {t('export.codebook.md')}"):
            md_data = _export_codes_markdown(codes)
            st.download_button(
                label=t("export.download"),
                data=md_data,
                file_name="codebook.md",
                mime="text/markdown"
            )


def _render_themes_export():
    """渲染主题导出"""
    st.subheader(t("export.themes.title"))

    themes = st.session_state.get('themes', [])

    if not themes:
        st.info(t("export.themes.no_themes"))
        return

    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"📋 {t('export.themes.json')}"):
            json_data = json.dumps(themes, ensure_ascii=False, indent=2)
            st.download_button(
                label=t("export.download"),
                data=json_data,
                file_name="themes.json",
                mime="application/json"
            )

    with col2:
        if st.button(f"📄 {t('export.themes.md')}"):
            md_data = _export_themes_markdown(themes)
            st.download_button(
                label=t("export.download"),
                data=md_data,
                file_name="themes.md",
                mime="text/markdown"
            )


def _render_report_export():
    """渲染报告导出"""
    st.subheader(t("export.report.title"))

    if not st.session_state.get('report'):
        st.info(t("export.report.no_report"))
        return

    if st.button(f"📄 {t('export.report.md')}"):
        # TODO: 导出报告
        st.success(t("export.export_success"))


def _render_full_project_export():
    """渲染完整项目导出"""
    st.subheader(t("export.full_project.title"))

    st.info(t("export.full_project.description"))

    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"📦 {t('export.full_project.export_btn')}", type="primary"):
            # 打包完整项目
            project_data = {
                "version": "4.1",
                "research_question": st.session_state.get('research_question', ''),
                "raw_text": st.session_state.get('raw_text', ''),
                "codes": st.session_state.get('codes', []),
                "themes": st.session_state.get('themes', []),
                "exported_at": st.session_state.get('last_action_time', '')
            }

            json_data = json.dumps(project_data, ensure_ascii=False, indent=2)

            st.download_button(
                label=t("export.download"),
                data=json_data,
                file_name="qualinsight_project.json",
                mime="application/json"
            )

    with col2:
        if st.button(f"📂 {t('export.full_project.import_btn')}"):
            uploaded_file = st.file_uploader(
                t("export.full_project.upload"),
                type=["json"]
            )

            if uploaded_file:
                try:
                    project_data = json.load(uploaded_file)

                    # 恢复项目数据
                    st.session_state.research_question = project_data.get('research_question', '')
                    st.session_state.raw_text = project_data.get('raw_text', '')
                    st.session_state.codes = project_data.get('codes', [])
                    st.session_state.themes = project_data.get('themes', [])

                    st.success(f"✅ {t('export.full_project.import_success')}")
                except Exception as e:
                    st.error(f"❌ {t('export.full_project.import_failed')}: {str(e)}")


def _export_codes_csv(codes):
    """导出编码为 CSV"""
    output = StringIO()
    output.write("Name,Description,Quotes Count\n")

    for code in codes:
        output.write(f"{code.get('name', '')},{code.get('description', '')},{len(code.get('quotes', []))}\n")

    return output.getvalue()


def _export_codes_markdown(codes):
    """导出编码为 Markdown"""
    lines = ["# Coding Book\n\n"]

    for code in codes:
        lines.append(f"## {code.get('name', 'N/A')}\n")
        lines.append(f"{code.get('description', '')}\n")
        lines.append(f"Quotes: {len(code.get('quotes', []))}\n\n")

    return "".join(lines)


def _export_themes_markdown(themes):
    """导出主题为 Markdown"""
    lines = ["# Themes Analysis\n\n"]

    for theme in themes:
        lines.append(f"## {theme.get('name', 'N/A')}\n")
        lines.append(f"{theme.get('definition', '')}\n\n")

    return "".join(lines)
