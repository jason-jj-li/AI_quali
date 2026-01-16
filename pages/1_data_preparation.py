# -*- coding: utf-8 -*-
"""
QualInsight Data Preparation Page
数据准备页面 - 研究问题和文本输入
"""

import streamlit as st
from i18n import t
from utils import (
    handle_error,
    handle_llm_error,
    validate_required,
    validate_research_question,
    validate_text_content,
    sanitize_html,
    DataValidationError,
)


def render_data_preparation():
    """
    渲染数据准备页面

    功能：
    - 研究问题输入与 AI 优化
    - 文本输入与验证
    - 访谈提纲生成
    - HTML 清洗
    """
    st.title(f"📝 {t('data_prep.title')}")

    tab1, tab2 = st.tabs([t("data_prep.tabs.text_input"), t("data_prep.tabs.interview_outline")])

    with tab1:
        # 研究问题
        st.subheader(t("data.research_question"))
        research_question = st.text_area(
            t("data.research_question"),
            value=st.session_state.get('research_question', ''),
            placeholder=t("data_prep.question_placeholder"),
            height=100,
            key="research_question_input"
        )

        # AI优化研究问题
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"💡 {t('data_prep.ai_optimize_tip')}")
        with col2:
            if st.button(f"✨ {t('data_prep.ai_optimize_btn')}", key="optimize_question"):
                if not research_question:
                    st.warning(t("data_prep.enter_question_first"))
                else:
                    with st.spinner(t("data_prep.ai_optimizing")):
                        try:
                            # 验证研究问题
                            validate_required(research_question, t("data.research_question"))

                            from src.llm.research_assistant import get_ai_research_assistant
                            assistant = get_ai_research_assistant()
                            result = assistant.optimize_research_question(research_question)

                            st.session_state.research_question = result.get('improved_question', research_question)
                            st.success(f"✅ {t('data_prep.optimized')}")

                            with st.expander(t("data_prep.view_suggestions")):
                                st.write(f"**{t('data_prep.suggestions')}**:")
                                for suggestion in result.get('suggestions', []):
                                    st.caption(f"- {suggestion}")
                                st.write(f"{t('data_prep.clarity_score')}: {result.get('clarity_score', 0):.0%}")
                                st.write(f"{t('data_prep.feasibility_score')}: {result.get('feasibility_score', 0):.0%}")
                        except Exception as e:
                            handle_llm_error(e, show_details=st.session_state.get('debug_mode', False))

        # 文本输入
        st.divider()
        st.subheader(t("data.text_input"))
        raw_text = st.text_area(
            t("data.text_input"),
            value=st.session_state.get('raw_text', ''),
            placeholder=t("data_prep.text_placeholder"),
            height=400,
            key="raw_text_input"
        )

        # 文本统计
        if raw_text:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(t("data_prep.char_metric"), len(raw_text))
            with col2:
                st.metric(t("data_prep.word_metric"), len(raw_text.split()))
            with col3:
                st.metric(t("data_prep.paragraph_metric"), raw_text.count('\n\n') + 1)
            with col4:
                st.metric(t("data_prep.reading_time"), f"{len(raw_text)//500} {t('data_prep.reading_time_unit')}")

        # 保存按钮
        st.divider()
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(f"💾 {t('data_prep.save_continue')}", type="primary"):
                try:
                    # 验证和清洗研究问题
                    if research_question:
                        validated_question = validate_research_question(research_question)
                        st.session_state.research_question = validated_question
                    else:
                        st.session_state.research_question = ""

                    # 验证和清洗文本内容
                    if not raw_text or not raw_text.strip():
                        raise DataValidationError(t("data_prep.enter_text_first"), field=t("data.text_input"))

                    validated_text = validate_text_content(raw_text, min_length=50)
                    # 清洗HTML标签（如果有）
                    cleaned_text = sanitize_html(validated_text)
                    st.session_state.raw_text = cleaned_text

                    st.success(f"✅ {t('data_prep.saved_goto_coding')}")

                except DataValidationError as e:
                    handle_error(e, show_details=st.session_state.get('debug_mode', False))
        with col2:
            # 清空数据按钮（带二次确认）
            confirm_clear = st.session_state.get("confirm_clear_page_data", False)

            if confirm_clear:
                # 显示确认界面
                col2a, col2b = st.columns(2)
                with col2a:
                    if st.button(f"✅ {t('data_prep.confirm_clear')}", key="do_clear_page", type="primary"):
                        st.session_state.raw_text = ""
                        st.session_state.research_question = ""
                        st.session_state.confirm_clear_page_data = False
                        st.success(f"✅ {t('data_prep.cleared')}")
                        st.rerun()
                with col2b:
                    if st.button(f"❌ {t('actions.cancel')}", key="cancel_clear_page"):
                        st.session_state.confirm_clear_page_data = False
                        st.rerun()
                st.caption(f"⚠️ {t('data_prep.will_clear_page')}")
            else:
                if st.button(f"🗑️ {t('data_prep.clear_page')}"):
                    st.session_state.confirm_clear_page_data = True
                    st.rerun()

    with tab2:
        st.subheader(t("data_prep.outline.title"))

        st.info(f"💡 {t('data_prep.outline.tip')}")

        current_rq = st.session_state.get('research_question') or research_question
        if not current_rq:
            st.warning(f"👈 {t('data_prep.outline.enter_question_first')}")
        else:
            st.write(f"**{t('data_prep.outline.current_question')}**: {current_rq}")

            # 生成选项
            col1, col2, col3 = st.columns(3)
            with col1:
                participant_type = st.selectbox(
                    t("data_prep.outline.participant_type"),
                    [t("data_prep.outline.participants.students"),
                     t("data_prep.outline.participants.professionals"),
                     t("data_prep.outline.participants.patients"),
                     t("data_prep.outline.participants.experts"),
                     t("data_prep.outline.participants.other")]
                )
            with col2:
                interview_duration = st.selectbox(
                    t("data_prep.outline.duration"),
                    [t("data_prep.outline.durations.30min"),
                     t("data_prep.outline.durations.1hour"),
                     t("data_prep.outline.durations.1_5hours"),
                     t("data_prep.outline.durations.2hours")]
                )
            with col3:
                question_count = st.slider(t("data_prep.outline.question_count"), 5, 20, 10)

            if st.button(f"✨ {t('data_prep.outline.generate_btn')}"):
                with st.spinner(t("data_prep.outline.generating")):
                    try:
                        from src.llm.research_assistant import get_ai_research_assistant
                        assistant = get_ai_research_assistant()

                        guide = assistant.generate_interview_guide(
                            research_question=current_rq,
                            participant_type=participant_type,
                            duration=interview_duration,
                            question_count=question_count
                        )

                        st.session_state.interview_guide = guide
                    except Exception as e:
                        st.error(f"❌ {t('data.generate_failed')}: {str(e)}")

            # 显示提纲
            if st.session_state.get('interview_guide'):
                st.divider()
                st.write(f"**📋 {t('data.generated_outline')}**")

                for i, section in enumerate(st.session_state.interview_guide.get('sections', []), 1):
                    with st.expander(f"{i}. {section['title']}", expanded=True):
                        st.write(f"**{t('data.purpose')}**: {section.get('purpose', '')}")
                        st.write(f"**{t('data.questions')}**:")
                        for j, q in enumerate(section.get('questions', []), 1):
                            st.caption(f"{j}. {q}")

                # 导出按钮
                if st.button(f"📥 {t('data.copy_outline')}"):
                    guide_text = "\n".join([
                        f"{s['title']}\n" + "\n".join([f"- {q}" for q in s['questions']])
                        for s in st.session_state.interview_guide.get('sections', [])
                    ])
                    st.session_state.clipboard_guide = guide_text
                    st.success(f"✅ {t('data.outline_ready')}")
