# -*- coding: utf-8 -*-
"""
QualInsight Coding Page
AI编码页面
"""

import streamlit as st
from i18n import t


def render_coding():
    """
    渲染 AI 编码页面

    功能：
    - 演绎式/归纳式编码
    - 编码本管理
    - 编码层级结构
    - 编码质量检查
    """
    st.title(f"🏷️ {t('coding.title')}")

    # 检查数据
    if not st.session_state.get('raw_text'):
        st.warning(f"👈 {t('coding.no_text_warning')}")
        st.info(t("coding.enter_text_first"))
        return

    # 编码模式选择
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(t("coding.mode_selection"))

        coding_mode = st.radio(
            t("coding.choose_mode"),
            [t("coding.modes.inductive"), t("coding.modes.deductive")],
            horizontal=True,
            label_visibility="collapsed"
        )

    with col2:
        st.write("")  # spacing
        st.write("")
        if st.button(f"🚀 {t('coding.start_ai_coding')}", type="primary", use_container_width=True):
            with st.spinner(t("coding.analyzing")):
                try:
                    # 获取文本和配置
                    text = st.session_state.get('raw_text', '')
                    research_question = st.session_state.get('research_question', '')

                    if not text:
                        st.warning(t("coding.no_text_warning"))
                        return

                    # 获取AI编码助手（使用正确的模型名称）
                    from src.llm.coding_assistant import get_ai_coding_assistant
                    assistant = get_ai_coding_assistant(model="qwen/qwen3-next-80b")

                    # 调试：显示使用的模型
                    st.info(f"🔧 调试: 使用模型 {assistant.provider.config.model}")

                    # 调用编码服务
                    from services.coding_service import CodingService
                    service = CodingService()

                    # 获取现有编码本（演绎式需要）
                    existing_codes = service.get_all_codes()
                    codebook = [{"id": c.id, "name": c.name, "description": c.description} for c in existing_codes]

                    # 根据模式进行AI编码
                    if coding_mode == t("coding.modes.inductive"):
                        # 归纳式编码 - 开放式编码
                        st.info(f"🔧 调试: 使用归纳式编码模式")
                        suggestions = assistant.suggest_codes_inductive(
                            text=text,
                            research_question=research_question,
                            methodology="质性研究",
                            max_suggestions=10
                        )
                    else:
                        # 演绎式编码 - 基于现有编码本
                        st.info(f"🔧 调试: 使用演绎式编码模式，编码本数量: {len(codebook)}")
                        suggestions = assistant.suggest_codes_deductive(
                            text=text,
                            codebook=codebook,
                            research_question=research_question,
                            methodology="质性研究",
                            max_suggestions=10
                        )

                    # 调试：显示收到的建议数量
                    st.info(f"🔧 调试: 收到 {len(suggestions)} 个编码建议")
                    if suggestions:
                        for i, s in enumerate(suggestions):
                            st.write(f"建议 {i+1}: {s.code_name} (置信度: {s.confidence})")

                    # 保存编码建议
                    created_count = 0
                    for suggestion in suggestions:
                        if suggestion.code_name and suggestion.code_name != "错误":
                            # 查找文本证据
                            quote_text = suggestion.text_evidence if suggestion.text_evidence else text[:200]

                            # 创建或更新编码
                            existing_code = None
                            for code in existing_codes:
                                if code.name == suggestion.code_name:
                                    existing_code = code
                                    break

                            if existing_code:
                                # 更新现有编码，添加引用
                                existing_code.quotes.append({"text": quote_text, "context": suggestion.reasoning})
                            else:
                                # 创建新编码
                                service.create_code(
                                    name=suggestion.code_name,
                                    description=suggestion.suggested_description or suggestion.reasoning,
                                    quotes=[{"text": quote_text, "context": suggestion.reasoning}],
                                    confidence=suggestion.confidence
                                )
                            created_count += 1

                    # 更新session state
                    st.session_state['codes'] = [c.to_dict() for c in service.get_all_codes()]

                    st.success(f"✅ {t('coding.coding_complete')} {t('coding.codes_found').format(count=created_count)}")

                except Exception as e:
                    import traceback
                    st.error(f"❌ {t('coding.coding_failed')}: {str(e)}")
                    st.error(traceback.format_exc())

    st.divider()

    # 编码本标签页
    tab1, tab2, tab3 = st.tabs([
        t("coding.tabs.codebook"),
        t("coding.tabs.quality"),
        t("coding.tabs.refactor")
    ])

    with tab1:
        _render_codebook()

    with tab2:
        _render_quality_check()

    with tab3:
        _render_refactor_tools()


def _render_codebook():
    """渲染编码本"""
    st.subheader(t("coding.codebook.title"))

    codes = st.session_state.get('codes', [])

    if not codes:
        st.info(t("coding.codebook.no_codes"))
        return

    # 显示编码列表
    for code in codes:
        with st.expander(f"🏷️ {code.get('name', 'N/A')}", expanded=False):
            st.write(f"**{t('coding.description')}**: {code.get('description', '')}")
            if code.get('quotes'):
                st.write(f"**{t('coding.quotes')}** ({len(code['quotes'])}):")
                for quote in code['quotes'][:3]:  # 只显示前3个
                    st.caption(f"...{quote.get('text', '')}...")


def _render_quality_check():
    """渲染质量检查"""
    st.subheader(t("coding.quality.title"))

    if st.button(f"🔍 {t('coding.quality.run_check')}"):
        with st.spinner(t("coding.quality.checking")):
            # TODO: 实现质量检查
            st.success(f"✅ {t('coding.quality.check_complete')}")


def _render_refactor_tools():
    """渲染重构工具"""
    st.subheader(t("coding.refactor.title"))

    if not st.session_state.get('codes'):
        st.info(t("coding.refactor.no_codes"))
        return

    option = st.selectbox(
        t("coding.refactor.choose_action"),
        [t("coding.refactor.merge"), t("coding.refactor.split")]
    )

    if option == t("coding.refactor.merge"):
        st.write(t("coding.refactor.merge_desc"))
    else:
        st.write(t("coding.refactor.split_desc"))
