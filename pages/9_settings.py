# -*- coding: utf-8 -*-
"""
QualInsight Settings Page
设置页面
"""

import streamlit as st
from i18n import t, render_language_switch


def render_settings():
    """
    渲染设置页面

    功能：
    - LLM 配置
    - API 密钥管理
    - 语言设置
    - 调试模式
    - 使用帮助
    """
    st.title(f"⚙️ {t('settings.title')}")

    # LLM 配置
    st.subheader(t('settings.llm_config.title'))

    provider = st.selectbox(
        t('settings.llm_config.provider'),
        ["lm_studio", "openai", "deepseek", "anthropic"],
        index=["lm_studio", "openai", "deepseek", "anthropic"].index(
            st.session_state.get('llm_provider', 'lm_studio')
        )
    )

    st.session_state.llm_provider = provider

    if provider == "lm_studio":
        _render_lm_studio_config()
    elif provider == "openai":
        _render_openai_config()
    elif provider == "deepseek":
        _render_deepseek_config()
    elif provider == "anthropic":
        _render_anthropic_config()

    st.divider()

    # 其他设置
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(t('settings.language.title'))
        render_language_switch()

    with col2:
        st.subheader(t('settings.advanced.title'))
        debug_mode = st.checkbox(
            t('settings.advanced.debug_mode'),
            value=st.session_state.get('debug_mode', False)
        )
        st.session_state.debug_mode = debug_mode

    st.divider()

    # 使用帮助
    st.subheader(t('settings.help.title'))
    _render_help()


def _render_lm_studio_config():
    """渲染 LM Studio 配置"""
    st.info(t('settings.llm_config.lm_studio.help'))

    base_url = st.text_input(
        t('settings.llm_config.base_url'),
        value=st.session_state.get('llm_base_url', 'http://localhost:1234/v1')
    )
    st.session_state.llm_base_url = base_url

    model = st.text_input(
        t('settings.llm_config.model'),
        value=st.session_state.get('llm_model', 'qwen/qwen3-next-80b')
    )
    st.session_state.llm_model = model


def _render_openai_config():
    """渲染 OpenAI 配置"""
    api_key = st.text_input(
        t('settings.llm_config.api_key'),
        type="password",
        value=st.session_state.get('llm_api_key', '')
    )
    st.session_state.llm_api_key = api_key

    model = st.selectbox(
        t('settings.llm_config.model'),
        ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"].index(
            st.session_state.get('llm_model', 'gpt-4o-mini')
        )
    )
    st.session_state.llm_model = model


def _render_deepseek_config():
    """渲染 Deepseek 配置"""
    api_key = st.text_input(
        t('settings.llm_config.api_key'),
        type="password",
        value=st.session_state.get('llm_api_key', '')
    )
    st.session_state.llm_api_key = api_key

    model = st.selectbox(
        t('settings.llm_config.model'),
        ["deepseek-chat", "deepseek-coder"],
        index=["deepseek-chat", "deepseek-coder"].index(
            st.session_state.get('llm_model', 'deepseek-chat')
        )
    )
    st.session_state.llm_model = model


def _render_anthropic_config():
    """渲染 Anthropic 配置"""
    api_key = st.text_input(
        t('settings.llm_config.api_key'),
        type="password",
        value=st.session_state.get('llm_api_key', '')
    )
    st.session_state.llm_api_key = api_key

    model = st.selectbox(
        t('settings.llm_config.model'),
        ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
        index=["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"].index(
            st.session_state.get('llm_model', 'claude-3-5-sonnet-20241022')
        )
    )
    st.session_state.llm_model = model


def _render_help():
    """渲染使用帮助"""
    with st.expander(t('settings.help.workflow'), expanded=False):
        st.markdown("""
        ### 📋 工作流程

        1. **数据准备** → 输入研究问题和文本
        2. **AI编码** → 选择编码模式，开始编码
        3. **主题分析** → 从编码中识别主题
        4. **可视化** → 查看分析结果图表
        5. **报告生成** → 生成学术报告
        6. **导出下载** → 导出数据和结果
        """)

    with st.expander(t('settings.help.llm'), expanded=False):
        st.markdown("""
        ### 🤖 LLM 配置

        - **LM Studio**: 本地模型，需先启动 LM Studio
        - **OpenAI**: 需要有效 API 密钥
        - **Deepseek**: 需要有效 API 密钥
        - **Anthropic**: 需要有效 API 密钥

        **推荐**: 学习阶段使用 LM Studio，正式研究使用 GPT-4o
        """)

    with st.expander(t('settings.help.tips'), expanded=False):
        st.markdown("""
        ### 💡 使用技巧

        - 定期使用「导出下载」保存工作
        - 编码时先使用归纳式，再建立层级结构
        - 主题分析建议多次迭代优化
        - 使用缓存可以加速重复操作
        """)
