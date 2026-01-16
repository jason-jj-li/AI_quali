"""
AI辅助质性研究平台 v4.0 - 全新UI/UX设计
基于Streamlit构建

特点：
- 现代化UI设计系统
- 直观的工作流程引导
- Dashboard首页概览
- 无需数据库，使用Session State存储
- 轻量级、易使用
"""
import streamlit as st
from pathlib import Path
from typing import Optional
import sys
import uuid
import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入配置
import config

# 导入UI组件
from src.utils.ui_components import (
    render_card,
    render_stat_card,
    render_highlight_card,
    render_badge,
    render_smart_tip,
    render_empty_state,
    render_loading_message
)

# 导入统一异常处理系统
from utils import (
    handle_error,
    handle_llm_error,
    safe_execute,
    catch_errors,
    LLMError,
    DataValidationError,
    ProcessingError,
    validate_required,
    validate_research_question,
    validate_text_content,
    validate_code_name,
    validate_theme_name,
    validate_api_key,
    clean_text,
    sanitize_html,
    is_api_key_valid,
    is_empty,
    ErrorContainer
)

# 导入缓存装饰器
from utils.cache import (
    cached,
    cached_llm,
    clear_cache,
    get_cache_stats,
    show_cache_stats,
    SimpleCache
)

# 导入国际化模块
from i18n import (
    t,
    get_current_language,
    set_language,
    get_available_languages,
    render_language_switch
)

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="QualInsight - AI质性分析平台",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==================== 学术杂志风格 CSS ====================
def inject_academic_css():
    """注入学术杂志风格的CSS样式"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+Pro:wght@300;400;600;700&display=swap');

    /* ========== 配色系统 - 优化对比度 ========== */
    :root {
        --primary-dark: #1e3a5f;      /* 深蓝 */
        --primary: #2d5a87;           /* 中蓝 */
        --primary-light: #4a7ab0;     /* 浅蓝 */
        --accent: #d4a537;            /* 金棕色 */
        --accent-light: #f0c056;      /* 浅金 */

        --bg-paper: #faf8f3;          /* 暖白 */
        --bg-card: #ffffff;           /* 纯白 */
        --bg-subtle: #f0ebe3;         /* 浅米 */

        --text-primary: #1a202c;      /* 深墨 */
        --text-secondary: #2d3748;    /* 灰墨 */
        --text-muted: #4a5568;        /* 中灰 */

        --border-subtle: #e2d8c8;     /* 浅棕边 */
        --border-card: #d4c8b0;       /* 卡片边 */

        --shadow-soft: 0 2px 12px rgba(26, 54, 93, 0.06);
        --shadow-card: 0 4px 24px rgba(26, 54, 93, 0.1);

        --gradient-primary: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        --gradient-accent: linear-gradient(135deg, #d4a537 0%, #f0c056 100%);
    }

    /* ========== 全局样式 ========== */
    .main {
        background: var(--bg-paper) !important;
        padding: 0 !important;
    }

    [data-testid="stAppViewContainer"] {
        background: var(--bg-paper) !important;
    }

    /* 隐藏Streamlit默认元素 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ========== 增强型顶部导航栏 ========== */
    .enhanced-top-nav {
        position: sticky;
        top: 0;
        z-index: 999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
        padding: 1rem 1.5rem;
        background: var(--primary-dark);
        box-shadow: 0 4px 20px rgba(26, 54, 93, 0.2);
        border-bottom: 3px solid var(--accent);
    }

    /* 品牌区域 */
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex-shrink: 0;
    }

    .nav-icon {
        font-size: 2rem;
        line-height: 1;
    }

    .nav-title {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin: 0 !important;
        letter-spacing: -0.02em;
    }

    .nav-version {
        font-family: 'Source Sans Pro', sans-serif !important;
        font-size: 0.65rem !important;
        font-weight: 700 !important;
        background: var(--accent);
        color: var(--primary-dark);
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* 导航标签区域 */
    .nav-tabs {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex: 1;
        justify-content: center;
        flex-wrap: nowrap;
        overflow-x: auto;
        overflow-y: hidden;
        scrollbar-width: none; /* Firefox */
        -ms-overflow-style: none; /* IE/Edge */
    }

    .nav-tabs::-webkit-scrollbar {
        display: none; /* Chrome/Safari */
    }

    .nav-tab {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.25rem;
        padding: 0.6rem 0.8rem;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        color: rgba(255, 255, 255, 0.7);
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.25s ease;
        min-width: 70px;
        white-space: nowrap;
        text-decoration: none;
    }

    .nav-tab:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.3);
        color: #ffffff;
        transform: translateY(-2px);
    }

    .nav-tab-active {
        background: var(--accent) !important;
        border-color: var(--accent-light) !important;
        color: var(--primary-dark) !important;
        box-shadow: 0 4px 12px rgba(212, 165, 55, 0.4);
    }

    .nav-tab-icon {
        font-size: 1.4rem;
        line-height: 1;
    }

    .nav-tab-label {
        font-size: 0.7rem;
        line-height: 1.2;
        text-align: center;
    }

    /* 导航操作区域 */
    .nav-actions {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex-shrink: 0;
    }

    .nav-lang-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.5rem 1rem;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: #ffffff;
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.25s ease;
        white-space: nowrap;
    }

    .nav-lang-btn:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }

    .lang-icon {
        font-size: 1rem;
    }

    /* 响应式调整 */
    @media (max-width: 1200px) {
        .nav-tab {
            padding: 0.5rem 0.6rem;
            min-width: 60px;
        }

        .nav-tab-label {
            font-size: 0.65rem;
        }
    }

    @media (max-width: 900px) {
        .enhanced-top-nav {
            flex-wrap: wrap;
            gap: 1rem;
        }

        .nav-tabs {
            order: 3;
            width: 100%;
            justify-content: flex-start;
        }

        .nav-brand {
            order: 1;
        }

        .nav-actions {
            order: 2;
        }
    }

    /* ========== 流程进度条 ========== */
    .workflow-progress-container {
        background: var(--bg-subtle);
        padding: 1.5rem 2rem;
        border-bottom: 1px solid var(--border-subtle);
    }

    .workflow-progress {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        max-width: 100%;
        margin: 0 auto;
    }

    .workflow-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
    }

    .workflow-step.active .step-icon {
        background: var(--primary) !important;
        color: var(--bg-card) !important;
        box-shadow: 0 4px 12px rgba(44, 82, 130, 0.3) !important;
    }

    .workflow-step.completed .step-icon {
        background: var(--accent) !important;
        color: var(--primary-dark) !important;
    }

    .workflow-step.active .step-label {
        color: var(--primary) !important;
        font-weight: 700 !important;
    }

    .step-icon {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: var(--bg-card);
        border: 2px solid var(--border-card);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        transition: all 0.3s ease;
        position: relative;
        z-index: 2;
    }

    .step-label {
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .workflow-connector {
        flex: 1;
        height: 2px;
        background: var(--border-card);
        min-width: 2rem;
        max-width: 4rem;
    }

    .workflow-connector.completed {
        background: var(--accent);
    }

    /* ========== 主要内容区域 ========== */
    .main-content-container {
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    .content-card {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: var(--shadow-card);
        border: 1px solid var(--border-card);
        margin-bottom: 1.5rem;
    }

    .content-card-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--primary-dark);
        margin-bottom: 0.5rem;
    }

    .content-card-subtitle {
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 0.95rem;
        color: var(--text-muted);
        margin-bottom: 1.5rem;
    }

    /* ========== Tab样式 ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        padding: 0;
        border-bottom: 2px solid var(--border-subtle);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 0;
        padding: 1rem 1.5rem;
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-muted);
        background: transparent;
        border-bottom: 3px solid transparent;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        background: transparent !important;
        border-bottom: 3px solid var(--primary) !important;
    }

    /* ========== 按钮样式 ========== */
    .stButton > button {
        font-family: 'Source Sans Pro', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }

    .stButton > button[kind="primary"] {
        background: var(--gradient-primary) !important;
        color: white !important;
        box-shadow: var(--shadow-soft) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-card) !important;
    }

    /* ========== 输入框样式 ========== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px !important;
        border: 2px solid var(--border-card) !important;
        font-family: 'Source Sans Pro', sans-serif !important;
        background: var(--bg-subtle) !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(44, 82, 130, 0.1) !important;
    }

    /* ========== 侧边栏样式（高对比度配色 - 加深背景和纯黑文字）========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #b8b2a7 0%, #a9a398 100%) !important;
        width: 280px !important;
        border-right: 2px solid #7a7468 !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.5rem !important;
    }

    /* 侧边栏所有文字使用纯黑色 + 文字阴影 - 最高优先级 */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > *,
    [data-testid="stSidebar"] > * > *,
    [data-testid="stSidebar"] > * > * > *,
    [data-testid="stSidebar"] > * > * > * > * {
        color: #000000 !important;
        text-shadow: 0 0 1px rgba(255,255,255,0.3) !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div:not([role="button"]):not([role="tab"]):not([role="option"]) {
        color: #000000 !important;
        text-shadow: 0 0 1px rgba(255,255,255,0.3) !important;
    }

    [data-testid="stSidebar"] label {
        font-weight: 800 !important;
        color: #000000 !important;
        text-shadow: 0 0 2px rgba(255,255,255,0.5) !important;
    }

    [data-testid="stSidebar"] .css-1d391kg,
    [data-testid="stSidebar"] .css-1lcbmhc,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
        color: #000000 !important;
        font-weight: 700 !important;
        text-shadow: 0 0 2px rgba(255,255,255,0.4) !important;
    }

    [data-testid="stSidebar"] [role="option"] {
        background: #ffffff !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] button[kind="primary"] {
        background: var(--primary) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] button[kind="header"] {
        background: transparent !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border: none !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
        color: #000000 !important;
        font-weight: 900 !important;
    }

    /* 针对流式文本容器的额外规则 */
    section[data-testid="stSidebar"] > div:has(> div) {
        color: #000000 !important;
    }

    /* ========== 指标卡片 ========== */
    [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: var(--primary) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'Source Sans Pro', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ========== 动画 ========== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animate-fade-in {
        animation: fadeInUp 0.6s ease-out;
    }

    /* ========== 警告/信息框 ========== */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        padding: 1.25rem 1.5rem !important;
        font-family: 'Source Sans Pro', sans-serif !important;
    }

    /* ========== 进度条 ========== */
    .stProgress > div > div > div > div {
        background: var(--gradient-primary) !important;
        border-radius: 10px !important;
    }

    /* ========== 工作流步骤按钮样式 ========== */
    /* 工作流容器 */
    .stHorizontalBlock > div {
        gap: 0.5rem !important;
    }

    /* 工作流步骤按钮基础样式 */
    button[kind="secondary"]:has(div) {
        min-height: 70px !important;
        padding: 0.75rem 0.5rem !important;
        border-radius: 12px !important;
        border: 2px solid !important;
        font-weight: 600 !important;
        font-size: 0.7rem !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.25rem !important;
        transition: all 0.3s ease !important;
        white-space: pre-line !important;
        line-height: 1.4 !important;
    }

    button[kind="secondary"]:has(div):hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }

    /* 激活状态 - 第一个按钮 */
    button[data-testid="baseButton-secondary-0"] {
        background-color: #2c5282 !important;
        border-color: #2c5282 !important;
        color: #ffffff !important;
    }

    /* 默认状态 - 其他按钮 */
    button[data-testid="baseButton-secondary-1"],
    button[data-testid="baseButton-secondary-2"],
    button[data-testid="baseButton-secondary-3"],
    button[data-testid="baseButton-secondary-4"],
    button[data-testid="baseButton-secondary-5"],
    button[data-testid="baseButton-secondary-6"] {
        background-color: #f7f5f0 !important;
        border-color: #e2dace !important;
        color: #718096 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== 初始化Session State ====================
def init_session_state():
    """初始化Session State"""
    # LLM配置（默认使用本地模型）
    if 'llm_provider' not in st.session_state:
        st.session_state.llm_provider = "lm_studio"
    if 'llm_model' not in st.session_state:
        st.session_state.llm_model = "local-model"
    if 'llm_api_key' not in st.session_state:
        st.session_state.llm_api_key = ""
    if 'llm_base_url' not in st.session_state:
        st.session_state.llm_base_url = "http://localhost:1234/v1"

    # 基础数据
    if 'raw_text' not in st.session_state:
        st.session_state.raw_text = ""
    if 'research_question' not in st.session_state:
        st.session_state.research_question = ""
    if 'interview_guide' not in st.session_state:
        st.session_state.interview_guide = None
    if 'methodology' not in st.session_state:
        st.session_state.methodology = "主题分析法"

    # 编码数据
    if 'codes' not in st.session_state:
        st.session_state.codes = []
    if 'coding_quality_report' not in st.session_state:
        st.session_state.coding_quality_report = None

    # 主题数据
    if 'themes' not in st.session_state:
        st.session_state.themes = []
    if 'theme_relationships' not in st.session_state:
        st.session_state.theme_relationships = None

    # 报告数据
    if 'report' not in st.session_state:
        st.session_state.report = None
    if 'deep_analysis' not in st.session_state:
        st.session_state.deep_analysis = None
    
    # 高级分析数据
    if 'sentiment_analysis' not in st.session_state:
        st.session_state.sentiment_analysis = None
    if 'discourse_analysis' not in st.session_state:
        st.session_state.discourse_analysis = None
    if 'narrative_analysis' not in st.session_state:
        st.session_state.narrative_analysis = None
    if 'coding_evolution' not in st.session_state:
        st.session_state.coding_evolution = []  # 编码本演进历史
    if 'multiple_coders' not in st.session_state:
        st.session_state.multiple_coders = {}  # {编码者名称: 编码列表}
    
    # UI状态
    if 'workflow_step' not in st.session_state:
        st.session_state.workflow_step = 0  # 0=数据准备, 1=编码分析, 2=主题分析, 3=可视化, 4=深度分析, 5=报告生成, 6=导出下载
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1  # 保留兼容性
    if 'last_action' not in st.session_state:
        st.session_state.last_action = None
    if 'last_action_time' not in st.session_state:
        st.session_state.last_action_time = None

    # 语言设置（i18n）
    if 'lang' not in st.session_state:
        st.session_state.lang = "zh_CN"  # 默认中文


# ==================== 增强型顶部导航栏 ====================
def render_horizontal_nav():
    """渲染增强型水平导航栏 - 使用Streamlit原生组件"""
    current_step = st.session_state.get('workflow_step', 0)

    # 定义导航项（step 值与 page_map 对应）
    nav_items = [
        {"icon": "📋", "label": t("workflow_steps.data_preparation"), "step": 1, "key": "nav_data"},
        {"icon": "🏷️", "label": t("workflow_steps.coding_analysis"), "step": 2, "key": "nav_coding"},
        {"icon": "🎯", "label": t("workflow_steps.theme_identification"), "step": 3, "key": "nav_theme"},
        {"icon": "📊", "label": t("workflow_steps.visualization"), "step": 4, "key": "nav_viz"},
        {"icon": "🔬", "label": t("workflow_steps.advanced_analysis"), "step": 5, "key": "nav_deep"},
        {"icon": "📑", "label": t("workflow_steps.report_generation"), "step": 6, "key": "nav_report"},
        {"icon": "💾", "label": t("workflow_steps.export"), "step": 7, "key": "nav_export"},
    ]

    # 品牌区域 + 导航 + 语言切换
    brand_col, *nav_cols, lang_col = st.columns([1.5, 1, 1, 1, 1, 1, 1, 1, 0.8])

    with brand_col:
        # 品牌按钮 - 点击返回主页
        if st.button(f"🔬 {t('app.title')}", key="nav_brand", help="返回主页 / Back to Home", use_container_width=True):
            st.session_state.workflow_step = 0
            st.rerun()

    # 导航按钮
    for col, item in zip(nav_cols, nav_items):
        with col:
            is_active = (current_step == item["step"])
            button_type = "primary" if is_active else "secondary"
            button_label = item["icon"]
            button_help = item["label"]

            if st.button(button_label, key=item["key"], help=button_help, use_container_width=True, type=button_type):
                st.session_state.workflow_step = item["step"]
                st.rerun()

    with lang_col:
        # 语言切换按钮
        current_lang = get_current_language()
        languages = get_available_languages()
        lang_codes = list(languages.keys())
        current_index = lang_codes.index(current_lang)
        next_lang = lang_codes[(current_index + 1) % len(lang_codes)]
        next_lang_name = languages[next_lang]

        if st.button(next_lang_name, key="top_lang_switch", use_container_width=True):
            set_language(next_lang)

    st.markdown("""
    <style>
    .nav-brand-inline {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0;
    }
    .nav-title-inline {
        font-family: 'Playfair Display', serif !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: var(--primary-dark) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ==================== 工作流程进度组件 ====================
def render_workflow_steps():
    """渲染工作流程步骤导航 - 使用可点击的 Streamlit 按钮"""
    current_step = st.session_state.get('workflow_step', 0)

    steps = [
        {"icon": "📋", "label": t("workflow_steps.data_preparation"), "key": "data"},
        {"icon": "🏷️", "label": t("workflow_steps.coding_analysis"), "key": "coding"},
        {"icon": "🎯", "label": t("workflow_steps.theme_identification"), "key": "theme"},
        {"icon": "📊", "label": t("workflow_steps.visualization"), "key": "visual"},
        {"icon": "🔬", "label": t("workflow_steps.advanced_analysis"), "key": "deep"},
        {"icon": "📑", "label": t("workflow_steps.report_generation"), "key": "report"},
        {"icon": "💾", "label": t("workflow_steps.export"), "key": "export"},
    ]

    # 使用列布局创建可点击的步骤按钮
    cols = st.columns([1] * len(steps))

    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            # 创建按钮 - 使用纯文本
            button_label = f"{step['icon']}\n{step['label']}"
            if st.button(button_label, key=f"workflow_step_{i}", help=f"{t('actions.jump_to')} {step['label']}", use_container_width=True):
                st.session_state.workflow_step = i
                st.rerun()


# ==================== 数据持久化状态组件 ====================
def render_data_persistence_status():
    """
    渲染数据持久化状态提示组件
    显示当前数据保存状态、最后保存时间、并提供快速保存选项
    """
    import json
    from pathlib import Path
    from datetime import datetime

    # 检查是否有数据
    has_data = bool(st.session_state.get('raw_text') or
                   st.session_state.get('codes') or
                   st.session_state.get('themes'))

    # 获取最后保存时间
    last_saved = st.session_state.get('last_saved_time')

    # 计算数据大小
    data_size = 0
    if has_data:
        try:
            data_dict = {
                'raw_text': st.session_state.get('raw_text', ''),
                'research_question': st.session_state.get('research_question', ''),
                'codes': st.session_state.get('codes', []),
                'themes': st.session_state.get('themes', []),
            }
            data_size = len(json.dumps(data_dict, ensure_ascii=False))
        except:
            data_size = 0

    # 渲染状态卡片
    if has_data:
        # 有数据时的状态显示
        status_color = "#F39C12"  # 警告色 - 内存中
        status_icon = "⚠️"
        status_text = t("status.data_in_memory")
        status_detail = t("status.close_window_lost")

        if last_saved:
            status_color = "#26C281"  # 成功色 - 已保存
            status_icon = "✅"
            status_text = t("status.data_saved")
            if isinstance(last_saved, str):
                status_detail = f"{t('status.last_saved')}: {last_saved}"
            else:
                status_detail = f"{t('status.last_saved')}: {last_saved.strftime('%H:%M')}"

        # 使用 HTML 渲染状态卡片
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {status_color}15, {status_color}05);
            border-left: 4px solid {status_color};
            border-radius: 8px;
            padding: 0.75rem;
            margin: 0.5rem 0;
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem;">{status_icon}</span>
                <span style="font-weight: 600; color: var(--text-primary); font-size: 0.9rem;">
                    {status_text}
                </span>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-muted); line-height: 1.4;">
                {status_detail}<br/>
                {t('status.data_size')}: ~{data_size / 1024:.1f} KB
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 快速保存按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"💾 {t('status.save_now')}", key="quick_save", use_container_width=True):
                try:
                    # 创建保存目录
                    save_dir = Path("saved_data")
                    save_dir.mkdir(exist_ok=True)

                    # 生成文件名
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"qualinsight_data_{timestamp}.json"
                    filepath = save_dir / filename

                    # 准备保存数据
                    save_data = {
                        'version': '4.1',
                        'saved_at': datetime.now().isoformat(),
                        'research_question': st.session_state.get('research_question', ''),
                        'raw_text': st.session_state.get('raw_text', ''),
                        'codes': st.session_state.get('codes', []),
                        'themes': st.session_state.get('themes', []),
                        'interview_guide': st.session_state.get('interview_guide'),
                    }

                    # 保存到文件
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(save_data, f, ensure_ascii=False, indent=2)

                    # 更新保存时间
                    st.session_state.last_saved_time = datetime.now()
                    st.session_state.last_saved_path = str(filepath)

                    st.success(f"✅ {t('status.saved_to')} {filename}")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ {t('status.save_failed')}: {str(e)}")

        with col2:
            # 导出按钮
            if st.button(f"📤 {t('status.export_json')}", key="quick_export", use_container_width=True):
                try:
                    save_data = {
                        'version': '4.1',
                        'exported_at': datetime.now().isoformat(),
                        'research_question': st.session_state.get('research_question', ''),
                        'raw_text': st.session_state.get('raw_text', ''),
                        'codes': st.session_state.get('codes', []),
                        'themes': st.session_state.get('themes', []),
                    }

                    json_str = json.dumps(save_data, ensure_ascii=False, indent=2)
                    st.download_button(
                        label=f"⬇️ {t('status.download_file')}",
                        data=json_str,
                        file_name=f"qualinsight_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="download_json"
                    )
                except Exception as e:
                    st.error(f"❌ {t('status.export_failed')}: {str(e)}")

        # 显示保存提示
        st.caption(f"💡 {t('status.save_tip')}")

    else:
        # 无数据时的提示
        st.markdown(f"""
        <div style="
            background: var(--bg-subtle);
            border-radius: 8px;
            padding: 0.75rem;
            margin: 0.5rem 0;
            text-align: center;
        ">
            <div style="font-size: 0.85rem; color: var(--text-muted);">
                📭 {t('status.no_data')}<br/>
                <span style="font-size: 0.75rem;">{t('status.no_data_hint')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==================== 二次确认机制 ====================
def confirm_dangerous_action(
    action_name: str,
    warning_message: str,
    confirm_label: str = t('confirm_action.confirm'),
    cancel_label: str = t('confirm_action.cancel')
) -> bool:
    """
    为危险操作提供二次确认机制

    Args:
        action_name: 操作名称（用于 session_state key）
        warning_message: 警告消息
        confirm_label: 确认按钮标签
        cancel_label: 取消按钮标签

    Returns:
        bool: 用户是否确认了操作
    """
    # 使用 session_state 追踪确认状态
    confirm_key = f"confirm_{action_name}"

    # 检查是否已确认
    if st.session_state.get(confirm_key, False):
        # 显示最终确认按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✅ {confirm_label}", key=f"do_{action_name}", type="primary"):
                # 重置确认状态
                st.session_state[confirm_key] = False
                return True
        with col2:
            if st.button(f"❌ {cancel_label}", key=f"cancel_{action_name}"):
                # 重置确认状态
                st.session_state[confirm_key] = False
                st.rerun()
        return False
    else:
        # 显示初始按钮
        if st.button(f"🗑️ {action_name}", key=f"init_{action_name}"):
            st.session_state[confirm_key] = True
            st.rerun()
        return False


def show_confirmation_dialog(
    title: str,
    message: str,
    action_name: str,
    danger_level: str = "warning"
) -> bool:
    """
    显示确认对话框

    Args:
        title: 对话框标题
        message: 确认消息
        action_name: 操作名称
        danger_level: 危险级别 (warning, danger, critical)

    Returns:
        bool: 用户是否确认
    """
    confirm_key = f"confirm_dialog_{action_name}"

    # 根据危险级别选择颜色
    colors = {
        "warning": "#F39C12",
        "danger": "#E74C3C",
        "critical": "#8B0000"
    }
    icons = {
        "warning": "⚠️",
        "danger": "🚨",
        "critical": "☠️"
    }

    color = colors.get(danger_level, "#F39C12")
    icon = icons.get(danger_level, "⚠️")

    if st.session_state.get(confirm_key, False):
        # 显示确认对话框
        st.markdown(f"""
        <div style="
            background: {color}15;
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        ">
            <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">
                {icon} <strong>{title}</strong>
            </div>
            <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;">
                {message}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✅ {t('confirm_dialog.confirm_execute')}", key=f"confirm_{action_name}", type="primary"):
                st.session_state[confirm_key] = False
                return True
        with col2:
            if st.button(f"❌ {t('confirm_dialog.cancel')}", key=f"cancel_{action_name}"):
                st.session_state[confirm_key] = False
                st.rerun()

        return False
    else:
        return False


def require_confirmation(
    action_name: str,
    callback,
    warning_message: Optional[str] = None,
    danger_level: str = "warning"
):
    """
    要求用户确认后才执行操作

    Args:
        action_name: 操作名称
        callback: 确认后要执行的函数
        warning_message: 警告消息
        danger_level: 危险级别
    """
    if warning_message is None:
        warning_message = t("confirm_dialog.irreversible_warning")
    confirm_key = f"confirm_{action_name}"

    if not st.session_state.get(confirm_key, False):
        # 显示初始按钮
        if st.button(f"🗑️ {action_name}", key=f"init_{action_name}"):
            st.session_state[confirm_key] = True
            st.rerun()
    else:
        # 显示确认界面
        st.warning(f"⚠️ {warning_message}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✅ {t('confirm_dialog.confirm_execute')}", key=f"do_{action_name}", type="primary"):
                st.session_state[confirm_key] = False
                callback()
        with col2:
            if st.button(f"❌ {t('confirm_dialog.cancel')}", key=f"cancel_{action_name}"):
                st.session_state[confirm_key] = False
                st.rerun()


# ==================== Dashboard 首页 ====================
def page_dashboard():
    """主页 - 项目介绍、LLM配置、教程"""

    # 项目标题和介绍
    st.title(f"🔬 {t('app.title')} - {t('app.subtitle')}")

    # 语言切换
    from i18n import render_language_switch
    render_language_switch()

    st.divider()

    # 项目介绍（中英双语）
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        ### 📖 {t('home.intro_title')}

        {t('home.intro_zh')}

        ### 🎯 {t('home.features_title')}

        - 📝 {t('home.feature1')}
        - 🏷️ {t('home.feature2')}
        - 🎯 {t('home.feature3')}
        - 📑 {t('home.feature4')}
        """)

    with col2:
        st.markdown(f"""
        ### 📖 Project Introduction

        {t('home.intro_en')}

        ### 🎯 Key Features

        - ✨ {t('home.feature1_en')}
        - 🏷️ {t('home.feature2_en')}
        - 🎯 {t('home.feature3_en')}
        - 📑 {t('home.feature4_en')}
        """)

    st.divider()

    # LLM 配置
    st.subheader(f"⚙️ {t('home.llm_config_title')}")

    # 获取当前provider，如果不在列表中则使用默认值
    current_provider = st.session_state.get('llm_provider', 'lm_studio')
    provider_list = ["lm_studio", "openai", "deepseek"]
    if current_provider not in provider_list:
        current_provider = 'lm_studio'

    provider = st.selectbox(
        t('settings.llm_config.provider'),
        provider_list,
        index=provider_list.index(current_provider)
    )
    st.session_state.llm_provider = provider

    if provider == "lm_studio":
        _render_lm_studio_config_sidebar()
    elif provider == "openai":
        _render_openai_config_sidebar()
    elif provider == "deepseek":
        _render_deepseek_config_sidebar()

    # 测试连接按钮
    if st.button(f"🔍 {t('home.test_connection')}"):
        with st.spinner(f"🔄 正在连接 {provider}..."):
            try:
                # 获取 provider 实例
                model = st.session_state.get('llm_model')
                api_key = st.session_state.get('llm_api_key')
                base_url = st.session_state.get('llm_base_url')

                llm_provider = _get_provider_instance(provider, model, api_key, base_url)

                # 调用模型进行自我介绍
                response = llm_provider.generate(
                    "请用一句话介绍你自己。你是什么模型？",
                    temperature=0.7,
                    max_tokens=100
                )

                st.success(f"✅ {t('settings.connection_success')}")
                st.info(f"🤖 **模型回复:**\n\n{response.content}")

            except Exception as e:
                st.error(f"❌ 连接失败: {str(e)}")

    st.divider()

    # 使用教程 - 双语详细版本（可折叠）
    with st.expander(f"📚 {t('home.tutorial_title')} / User Guide", expanded=False):
        tab1, tab2 = st.tabs(["🇨🇳 中文教程", "🇺🇸 English Guide"])

        with tab1:
            st.markdown("""
            ## 📋 完整工作流程

            ### 第一步：数据准备
            - 输入研究问题：明确您的研究目的和问题
            - 输入研究文本：粘贴访谈记录、文档等质性数据
            - 支持导入：可从 JSON 文件导入已有数据

            ### 第二步：AI 编码
            - 选择编码模式：
              - **归纳式编码**：从文本中自动发现新编码（推荐首次使用）
              - **演绎式编码**：基于已有编码本进行编码
            - 点击"开始 AI 编码"按钮
            - AI 将自动识别文本中的关键概念和主题
            - 审查和编辑生成的编码

            ### 第三步：主题分析
            - 确保已完成编码步骤
            - 点击"AI 识别主题"按钮
            - AI 将基于编码结果识别核心主题
            - 每个主题包含：
              - 主题名称
              - 主题定义
              - 支持引用
              - 相关编码

            ### 第四步：可视化
            - 查看编码和主题的图表展示
            - 支持多种图表类型：
              - 词云图
              - 编码网络图
              - 主题层级图
              - 编码频率图

            ### 第五步：深度分析
            - 编码关系分析
            - 跨案例分析
            - 编码一致性检验

            ### 第六步：报告生成
            - 选择报告语言（中文/英文）
            - 选择要包含的章节：
              - 文献综述
              - 理论框架
              - 研究创新点
              - 研究局限性
            - 生成 IMRAD 格式的学术报告
            - 编辑和导出报告

            ### 第七步：导出下载
            - 导出完整项目数据（JSON 格式）
            - 导出编码本
            - 导出主题列表
            - 导出可视化图表
            """)

        with tab2:
            st.markdown("""
            ## 📋 Complete Workflow

            ### Step 1: Data Preparation
            - **Research Question**: Enter your research purpose and questions
            - **Research Text**: Paste qualitative data (interviews, documents, etc.)
            - **Import**: Import existing data from JSON files

            ### Step 2: AI Coding
            - **Choose Coding Mode**:
              - **Inductive Coding**: Discover new codes from text (recommended for first-time use)
              - **Deductive Coding**: Apply existing codebook to text
            - Click "Start AI Coding" button
            - AI automatically identifies key concepts and themes
            - Review and edit generated codes

            ### Step 3: Theme Analysis
            - Ensure coding step is completed
            - Click "AI Identify Themes" button
            - AI identifies core themes based on codes
            - Each theme includes:
              - Theme name
              - Theme definition
              - Supporting quotes
              - Related codes

            ### Step 4: Visualization
            - View charts of codes and themes
            - Multiple chart types:
              - Word cloud
              - Code network graph
              - Theme hierarchy diagram
              - Code frequency chart

            ### Step 5: Advanced Analysis
            - Code relationship analysis
            - Cross-case analysis
            - Inter-coder reliability

            ### Step 6: Report Generation
            - Select report language (Chinese/English)
            - Choose sections to include:
              - Literature review
              - Theoretical framework
              - Research innovations
              - Research limitations
            - Generate IMRAD format academic report
            - Edit and export report

            ### Step 7: Export & Download
            - Export complete project data (JSON format)
            - Export codebook
            - Export theme list
            - Export visualization charts
            """)

    # 页脚
    st.divider()
    st.markdown("""
    <div style="text-align: center; padding: 20px 0; color: #666; font-size: 14px;">
        <p style="margin-bottom: 10px;">
            <strong>QualInsight</strong> - AI辅助质性研究平台 v4.1
        </p>
        <p style="margin-bottom: 10px;">
            © 2025 QualInsight Project. All rights reserved.
        </p>
        <p style="margin-bottom: 5px;">
            <a href="#" style="color: #666; text-decoration: none;">使用条款</a> •
            <a href="#" style="color: #666; text-decoration: none;">隐私政策</a> •
            <a href="https://github.com" style="color: #666; text-decoration: none;">GitHub</a> •
            <a href="mailto:support@qualinsight.com" style="color: #666; text-decoration: none;">联系我们</a>
        </p>
        <p style="margin-top: 10px; font-size: 12px; color: #999;">
            本项目采用 MIT 许可证开源 • 基于 Streamlit 构建
        </p>
    </div>
    """, unsafe_allow_html=True)


def _render_lm_studio_config_sidebar():
    """渲染 LM Studio 配置"""
    st.info(t('settings.llm_config.lm_studio.help'))

    base_url = st.text_input(
        t('settings.llm_config.base_url'),
        value=st.session_state.get('llm_base_url', 'http://localhost:1234/v1')
    )
    st.session_state.llm_base_url = base_url

    # 获取当前模型，如果为空或无效则使用默认值
    current_model = st.session_state.get('llm_model', 'qwen/qwen3-next-80b')
    if not current_model or current_model == 'local-model':
        current_model = 'qwen/qwen3-next-80b'

    model = st.text_input(
        t('settings.llm_config.model'),
        value=current_model
    )
    st.session_state.llm_model = model


def _render_openai_config_sidebar():
    """渲染 OpenAI 配置"""
    api_key = st.text_input(
        t('settings.llm_config.api_key'),
        type="password",
        value=st.session_state.get('llm_api_key', '')
    )
    st.session_state.llm_api_key = api_key

    # 获取当前模型，如果不在列表中则使用默认值
    current_model = st.session_state.get('llm_model', 'gpt-4o-mini')
    model_list = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    if current_model not in model_list:
        current_model = 'gpt-4o-mini'

    model = st.selectbox(
        t('settings.llm_config.model'),
        model_list,
        index=model_list.index(current_model)
    )
    st.session_state.llm_model = model


def _render_deepseek_config_sidebar():
    """渲染 Deepseek 配置"""
    api_key = st.text_input(
        t('settings.llm_config.api_key'),
        type="password",
        value=st.session_state.get('llm_api_key', '')
    )
    st.session_state.llm_api_key = api_key

    # 获取当前模型，如果不在列表中则使用默认值
    current_model = st.session_state.get('llm_model', 'deepseek-chat')
    model_list = ["deepseek-chat", "deepseek-coder"]
    if current_model not in model_list:
        current_model = 'deepseek-chat'

    model = st.selectbox(
        t('settings.llm_config.model'),
        model_list,
        index=model_list.index(current_model)
    )
    st.session_state.llm_model = model


def _get_provider_instance(provider, model, api_key, base_url=None):
    """获取provider实例（内部函数）"""
    from src.llm.base import LLMConfig
    from src.llm.openai import OpenAIProvider
    from src.llm.lm_studio import LMStudioProvider
    from src.llm.deepseek import DeepseekProvider

    # 确保模型不为空
    if not model:
        model = "qwen/qwen3-next-80b" if provider == "lm_studio" else "gpt-4o-mini"

    if provider == "lm_studio":
        config = LLMConfig(
            provider="lm_studio",
            model=model,
            api_key="not-needed",
            base_url=base_url or "http://localhost:1234/v1"
        )
        return LMStudioProvider(config)
    elif provider == "openai":
        config = LLMConfig(
            provider="openai",
            model=model,
            api_key=api_key
        )
        return OpenAIProvider(config)
    elif provider == "deepseek":
        config = LLMConfig(
            provider="deepseek",
            model=model,
            api_key=api_key,
            base_url=base_url or "https://api.deepseek.com/v1"
        )
        return DeepseekProvider(config)
    else:
        raise ValueError(f"不支持的 LLM 提供商: {provider}")


# ==================== 页面1: 文本输入 ====================
def page_text_input():
    """文本输入页面"""
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


# ==================== 页面2: AI编码 ====================
def page_coding():
    """AI编码页面（包含质量检查）"""
    st.title(f"🏷️ {t('coding.title')}")

    # 检查数据
    if not st.session_state.get('raw_text'):
        st.warning(f"👈 {t('coding.no_text_warning')}")
        return

    st.info(f"📄 {t('coding.text_length')}: {len(st.session_state.raw_text)} {t('coding.characters_unit')}")

    tab1, tab2, tab3 = st.tabs([t("coding.tabs.ai_coding"), t("coding.tabs.quality_check"), t("coding.tabs.codebook")])

    # Tab1: AI编码
    with tab1:
        st.subheader(t("coding.tabs.ai_coding"))

        # 显示当前LLM配置
        col1, col2 = st.columns(2)
        with col1:
            coding_mode = st.radio(
                t("coding.mode"),
                [t("coding.modes.deductive"), t("coding.modes.inductive")]
            )
        with col2:
            # 显示当前LLM配置（来自侧边栏）
            from config import SUPPORTED_LLM_PROVIDERS
            provider_name = SUPPORTED_LLM_PROVIDERS.get(st.session_state.get('llm_provider', 'lm_studio'), {}).get("name", "Unknown")
            st.info(f"🤖 {t('coding.using')}: {provider_name} ({st.session_state.get('llm_model', 'N/A')})")

        # 显示已有编码
        if st.session_state.codes:
            st.write(f"**{t('coding.existing_codes')}**:")
            code_tags = ", ".join([f"🏷️ {c['name']}" for c in st.session_state.codes[:5]])
            if len(st.session_state.codes) > 5:
                code_tags += f" ... (+{len(st.session_state.codes)-5}{t('coding.more_codes')})"
            st.caption(code_tags)

        # 开始AI编码
        if st.button(f"🚀 {t('coding.start_coding')}", type="primary", key="start_coding"):
            with st.spinner(t("coding.analyzing")):
                try:
                    from src.llm.coding_assistant import get_ai_coding_assistant

                    # 使用session state中的LLM配置
                    assistant = get_ai_coding_assistant()

                    if t("coding.modes.deductive") in coding_mode and st.session_state.codes:
                        # 演绎式编码
                        results = assistant.deductive_coding(
                            text=st.session_state.raw_text,
                            codebook=st.session_state.codes,
                            research_question=st.session_state.get('research_question', '')
                        )
                    else:
                        # 归纳式编码
                        results = assistant.inductive_coding(
                            text=st.session_state.raw_text,
                            research_question=st.session_state.get('research_question', '')
                        )

                    # 保存结果
                    for result in results:
                        st.session_state.codes.append({
                            'id': str(uuid.uuid4()),
                            'name': result.name,
                            'description': result.description,
                            'quotes': result.quotes if hasattr(result, 'quotes') else [],
                            'created_by': 'ai',
                            'confidence': result.confidence if hasattr(result, 'confidence') else 0.8
                        })

                    st.success(f"✅ {t('coding.coding_complete')} {len(results)} {t('coding.codes_found')}")

                except Exception as e:
                    handle_error(e, context=t("coding.tabs.ai_coding"), show_details=st.session_state.get('debug_mode', False))

        # 显示编码结果
        if st.session_state.codes:
            st.divider()
            st.write(f"**{t('coding.code_list')}** ({t('coding.total_codes')} {len(st.session_state.codes)} {t('coding.more_codes')})")

            for i, code in enumerate(st.session_state.codes):
                with st.expander(
                    f"🏷️ {code['name']} "
                    f"({len(code.get('quotes', []))} {t('coding.quotes_count')}) "
                    f"{'🤖' if code.get('created_by') == 'ai' else '👤'}",
                    expanded=False
                ):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**{t('coding.description')}**: {code['description']}")

                        if code.get('confidence'):
                            conf = code['confidence']
                            st.progress(conf, text=f"{t('coding.ai_confidence')}: {conf:.0%}")

                        if code.get('quotes'):
                            st.write(f"**{t('coding.quote_examples')}**:")
                            for quote in code['quotes'][:2]:
                                st.caption(f"- \"{quote[:80]}...\"")

                    with col2:
                        if st.button("🗑️", key=f"del_code_{i}"):
                            st.session_state.codes.pop(i)
                            st.success(t("coding.deleted"))
                            st.rerun()

    # Tab2: 质量检查
    with tab2:
        st.subheader(f"🔍 {t('coding.quality_check.title')}")

        st.info(f"💡 {t('coding.quality_check.tip')}")

        # 检查项
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(f"📊 {t('coding.quality_check.saturation')}", key="saturation_check"):
                with st.spinner(t("coding.quality_check.checking_saturation")):
                    try:
                        from src.llm.quality_checker import get_ai_quality_checker
                        checker = get_ai_quality_checker()

                        report = checker.check_saturation(
                            codes=st.session_state.codes,
                            text=st.session_state.raw_text
                        )

                        st.session_state.coding_quality_report = report

                        if report.get('is_saturated'):
                            st.success(f"✅ {t('coding.quality_check.saturated')}！")
                            st.write(f"**{t('coding.quality_check.analysis')}**:")
                            st.write(report.get('analysis', ''))
                        else:
                            st.warning(f"⚠️ {t('coding.quality_check.not_saturated')}")
                            st.write(f"**{t('coding.quality_check.suggestions')}**:")
                            for suggestion in report.get('suggestions', []):
                                st.caption(f"- {suggestion}")
                    except Exception as e:
                        st.error(f"❌ {t('coding.quality_check.check_failed')}: {str(e)}")

        with col2:
            if st.button(f"🔍 {t('coding.quality_check.consistency')}", key="consistency_check"):
                st.info(f"💡 {t('coding.quality_check.single_coder_note')}")
                st.write(t('coding.quality_check.single_coder_note'))

                with st.spinner(t("coding.quality_check.checking_consistency")):
                    try:
                        from src.llm.quality_checker import get_ai_quality_checker
                        checker = get_ai_quality_checker()

                        report = checker.check_internal_consistency(
                            codes=st.session_state.codes,
                            text=st.session_state.raw_text
                        )

                        st.session_state.coding_quality_report = report

                        st.metric(t("coding.quality_check.consistency_score"), f"{report.get('score', 0):.0%}")
                        st.write(f"**{t('coding.quality_check.analysis')}**:")
                        st.write(report.get('analysis', ''))

                        if report.get('issues'):
                            st.warning(f"**{t('coding.quality_check.potential_issues')}**:")
                            for issue in report['issues']:
                                st.caption(f"- {issue}")
                    except Exception as e:
                        st.error(f"❌ {t('coding.quality_check.check_failed')}: {str(e)}")

        with col3:
            if st.button(f"🔍 {t('coding.quality_check.deviant_cases')}", key="deviant_check"):
                with st.spinner(t("coding.quality_check.checking_deviant")):
                    try:
                        from src.llm.quality_checker import get_ai_quality_checker
                        checker = get_ai_quality_checker()

                        report = checker.identify_deviant_cases(
                            codes=st.session_state.codes,
                            text=st.session_state.raw_text
                        )

                        st.session_state.coding_quality_report = report

                        st.success(f"✅ {t('coding.quality_check.deviant_found')} {len(report.get('deviant_cases', []))} {t('coding.quality_check.deviant_cases_count')}")

                        if report.get('deviant_cases'):
                            st.write(f"**{t('coding.quality_check.deviant_cases_title')}**（{t('coding.quality_check.deviant_cases_subtitle')}）:")
                            for i, case in enumerate(report['deviant_cases'], 1):
                                with st.expander(f"{t('coding.quality_check.case')} {i}: {case.get('title', '')}"):
                                    st.write(f"**{t('coding.description')}**: {case.get('description', '')}")
                                    st.write(f"**{t('coding.quality_check.quote')}**: \"{case.get('quote', '')}\"")
                                    st.write(f"**{t('coding.quality_check.significance')}**: {case.get('significance', '')}")
                    except Exception as e:
                        st.error(f"❌ {t('coding.quality_check.identification_failed')}: {str(e)}")

        # 显示质量报告摘要
        if st.session_state.get('coding_quality_report'):
            st.divider()
            st.write(f"**{t('coding.quality_report_summary')}**")
            report = st.session_state.coding_quality_report

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(t('coding.code_count'), len(st.session_state.codes))
            with col2:
                st.metric(t('coding.total_quotes'), sum(len(c.get('quotes', [])) for c in st.session_state.codes))
            with col3:
                avg_conf = sum(c.get('confidence', 0.8) for c in st.session_state.codes) / max(len(st.session_state.codes), 1)
                st.metric(t('coding.avg_confidence'), f"{avg_conf:.0%}")
            with col4:
                if 'score' in report:
                    st.metric(t('coding.quality_score'), f"{report['score']:.0%}")

    # Tab3: 编码本
    with tab3:
        st.subheader(t('coding.codebook_management'))

        # 手动添加编码
        with st.expander(f"➕ {t('coding.add_manual_code')}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                manual_code_name = st.text_input(t('coding.code_name_required'), key="manual_code_name")

            with col2:
                # 层级编码：选择父编码
                parent_options = [t('coding.no_parent_code')] + [c['name'] for c in st.session_state.codes]
                parent_code = st.selectbox(t('coding.parent_code'), parent_options, key="parent_code_select")

            manual_code_desc = st.text_area(t('coding.code_description'), key="manual_code_desc", height=100)

            if st.button(t('coding.add_code_button'), key="add_manual_code"):
                if manual_code_name:
                    parent_id = None
                    if parent_code != t('coding.no_parent_code'):
                        parent_id = next((c['id'] for c in st.session_state.codes if c['name'] == parent_code), None)

                    st.session_state.codes.append({
                        'id': str(uuid.uuid4()),
                        'name': manual_code_name,
                        'description': manual_code_desc,
                        'quotes': [],
                        'created_by': 'human',
                        'parent_id': parent_id
                    })
                    st.success(f"✅ {t('coding.code_added')}")
                    st.rerun()
                else:
                    st.warning(t('coding.enter_code_name'))

        # 编码重构工具
        with st.expander(f"🔧 {t('coding.refactoring_tools')}"):
            st.write(f"**{t('coding.merge_codes')}**")

            if len(st.session_state.codes) >= 2:
                col1, col2 = st.columns(2)

                with col1:
                    merge_source = st.multiselect(
                        t('coding.select_codes_to_merge'),
                        [c['name'] for c in st.session_state.codes],
                        key="merge_source"
                    )

                with col2:
                    merge_target_name = st.text_input(
                        t('coding.new_code_name'),
                        key="merge_target_name"
                    )

                if st.button(t('coding.merge_button')) and merge_source and merge_target_name:
                    # 收集所有引用
                    all_quotes = []
                    all_descriptions = []
                    
                    for code in st.session_state.codes:
                        if code['name'] in merge_source:
                            all_quotes.extend(code.get('quotes', []))
                            if code.get('description'):
                                all_descriptions.append(code['description'])
                    
                    # 创建新编码
                    new_code = {
                        'id': str(uuid.uuid4()),
                        'name': merge_target_name,
                        'description': " | ".join(all_descriptions),
                        'quotes': list(set(all_quotes)),  # 去重
                        'created_by': 'human',
                        'merged_from': merge_source
                    }
                    
                    # 删除旧编码
                    st.session_state.codes = [c for c in st.session_state.codes if c['name'] not in merge_source]

                    # 添加新编码
                    st.session_state.codes.append(new_code)

                    st.success(f"✅ {t('coding.merged_success')} {len(merge_source)} {t('coding.codes_unit')} {t('coding.merged_into')} {merge_target_name}")
                    st.rerun()

            st.divider()
            st.write(f"**{t('coding.split_codes')}**")

            if st.session_state.codes:
                split_code_name = st.selectbox(
                    t('coding.select_code_to_split'),
                    [c['name'] for c in st.session_state.codes],
                    key="split_code_select"
                )

                col1, col2 = st.columns(2)

                with col1:
                    split_name1 = st.text_input(t('coding.split_code_1'), key="split_name1")

                with col2:
                    split_name2 = st.text_input(t('coding.split_code_2'), key="split_name2")

                if st.button(t('coding.split_button')) and split_name1 and split_name2:
                    original = next((c for c in st.session_state.codes if c['name'] == split_code_name), None)

                    if original:
                        quotes = original.get('quotes', [])
                        mid = len(quotes) // 2

                        # 创建两个新编码
                        code1 = {
                            'id': str(uuid.uuid4()),
                            'name': split_name1,
                            'description': f"{t('coding.split_from')} {split_code_name}",
                            'quotes': quotes[:mid],
                            'created_by': 'human'
                        }

                        code2 = {
                            'id': str(uuid.uuid4()),
                            'name': split_name2,
                            'description': f"{t('coding.split_from')} {split_code_name}",
                            'quotes': quotes[mid:],
                            'created_by': 'human'
                        }

                        # 删除原编码
                        st.session_state.codes = [c for c in st.session_state.codes if c['name'] != split_code_name]

                        # 添加新编码
                        st.session_state.codes.extend([code1, code2])

                        st.success(f"✅ {t('coding.split_success')} {split_code_name} {t('coding.split_into_two')}")
                        st.rerun()

        # 显示所有编码（层级结构）
        if st.session_state.codes:
            st.write(f"**{t('coding.codebook_label')}** ({len(st.session_state.codes)} {t('coding.codes_count_unit')}):")

            # 构建层级结构
            top_level_codes = [c for c in st.session_state.codes if not c.get('parent_id')]
            child_codes = [c for c in st.session_state.codes if c.get('parent_id')]

            def render_code_tree(code, level=0):
                """递归渲染编码树"""
                indent = "　" * level
                icon = "📁" if any(c.get('parent_id') == code['id'] for c in st.session_state.codes) else "🏷️"

                with st.expander(f"{indent}{icon} {code['name']} ({len(code.get('quotes', []))}{t('coding.quotes_unit')})", expanded=False):
                    st.caption(f"**{t('coding.description_label')}**: {code.get('description', t('coding.none_label'))}")
                    st.caption(f"**{t('coding.created_by_label')}**: {t('coding.ai') if code.get('created_by') == 'ai' else t('coding.manual')}")

                    if code.get('quotes'):
                        st.caption(f"**{t('coding.quote_examples')}:**")
                        for quote in code['quotes'][:2]:
                            quote_text = quote if isinstance(quote, str) else str(quote)
                            st.caption(f"- \"{quote_text[:60]}...\"")
                    
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button("🗑️", key=f"del_code_{code['id']}"):
                            st.session_state.codes = [c for c in st.session_state.codes if c['id'] != code['id']]
                            st.rerun()
                
                # 渲染子编码
                children = [c for c in st.session_state.codes if c.get('parent_id') == code['id']]
                for child in children:
                    render_code_tree(child, level + 1)
            
            # 渲染顶层编码
            for code in top_level_codes:
                render_code_tree(code)

            # 导出选项
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"📋 {t('coding.export_codebook')}"):
                    codebook_text = f"# {t('coding.codebook_title')}\n\n"
                    for code in st.session_state.codes:
                        codebook_text += f"## {code['name']}\n"
                        codebook_text += f"{code.get('description', '')}\n\n"
                    st.session_state.export_codebook = codebook_text
                    st.success(f"✅ {t('coding.codebook_ready')}")

        else:
            st.info(t('coding.no_codes_hint'))


# ==================== 页面3: 主题分析 ====================
def page_themes():
    """主题分析页面（包含关系分析）"""
    st.title(f"🎯 {t('themes.title')}")

    # 检查数据
    if not st.session_state.get('codes'):
        st.warning(t('themes.warning_no_codes'))
        return

    st.info(f"📊 {t('themes.current_codes')}: {len(st.session_state.codes)}")

    tab1, tab2, tab3, tab4 = st.tabs([t("themes.tabs.ai_identify"), t("themes.tabs.relations"), t("themes.tabs.visualization"), t("themes.tabs.management")])

    # Tab1: AI主题识别
    with tab1:
        st.subheader(t('themes.ai_identify.subtitle'))

        # 获取当前全局 LLM 配置
        current_provider = st.session_state.get('llm_provider', 'lm_studio')

        col1, col2, col3 = st.columns(3)
        with col1:
            max_themes = st.slider(t('themes.ai_identify.max_themes'), 3, 15, 8)
        with col2:
            # 根据当前配置设置默认值
            provider_options = ["openai", "anthropic", "lm_studio"]
            default_index = provider_options.index(current_provider) if current_provider in provider_options else 2
            ai_provider = st.selectbox(
                t('themes.ai_identify.provider'),
                provider_options,
                index=default_index,
                key="theme_provider",
                help=f"默认使用全局配置: {current_provider}"
            )
        with col3:
            approach = st.selectbox(t('themes.ai_identify.approach'), [t('themes.ai_identify.approaches.thematic'), t('themes.ai_identify.approaches.grounded'), t('themes.ai_identify.approaches.phenomenological')])

        if st.button(f"🚀 {t('themes.ai_identify.start')}", type="primary", key="start_theme"):
            with st.spinner(t('themes.ai_identify.spinner')):
                try:
                    from src.llm.theme_assistant import get_ai_theme_assistant

                    assistant = get_ai_theme_assistant(ai_provider)

                    suggestions = assistant.identify_themes_from_codes(
                        codes=st.session_state.codes,
                        research_question=st.session_state.get('research_question', ''),
                        max_themes=max_themes,
                        approach=approach
                    )

                    # 保存主题
                    for suggestion in suggestions:
                        st.session_state.themes.append({
                            'id': str(uuid.uuid4()),
                            'name': suggestion.name,
                            'description': suggestion.description,
                            'definition': suggestion.definition,
                            'codes': suggestion.related_codes,
                            'quotes': suggestion.quotes,
                            'created_by': 'ai',
                            'confidence': suggestion.confidence
                        })

                    st.success(f"✅ {t('themes.ai_identify.success')}: {len(suggestions)}")

                except Exception as e:
                    st.error(f"❌ {t('themes.ai_identify.failed')}: {str(e)}")

        # 显示主题
        if st.session_state.themes:
            st.divider()
            for i, theme in enumerate(st.session_state.themes):
                with st.expander(
                    f"🎯 {theme['name']} "
                    f"({len(theme.get('codes', []))} {t('themes.display.codes_count')}) "
                    f"{'🤖' if theme.get('created_by') == 'ai' else '👤'}",
                    expanded=False
                ):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**{t('themes.display.description')}**: {theme['description']}")
                        st.write(f"**{t('themes.display.definition')}**: {theme.get('definition', t('themes.display.not_provided'))}")

                        if theme.get('codes'):
                            st.write(f"**{t('themes.display.related_codes')}**:")
                            for code_name in theme['codes'][:5]:
                                st.caption(f"- 🏷️ {code_name}")

                        if theme.get('quotes'):
                            st.write(f"**{t('themes.display.quotes')}**:")
                            for quote in theme['quotes'][:2]:
                                st.caption(f"- \"{str(quote)[:80]}...\"")

                    with col2:
                        if st.button("🗑️", key=f"del_theme_{i}"):
                            st.session_state.themes.pop(i)
                            st.success(t('themes.display.deleted'))
                            st.rerun()

    # Tab2: 主题关系
    with tab2:
        st.subheader(f"🔗 {t('themes.relations.subtitle')}")

        st.info(f"💡 {t('themes.relations.info')}")

        col1, col2 = st.columns(2)
        with col1:
            analysis_type = st.selectbox(
                t('themes.relations.analysis_type'),
                [t('themes.relations.types.correlation'), t('themes.relations.types.conflict'), t('themes.relations.types.hierarchy')]
            )
        with col2:
            if st.button(f"🔍 {t('themes.relations.start')}", key="analyze_relationships"):
                with st.spinner(t('themes.relations.spinner')):
                    try:
                        from src.llm.theme_analyzer import get_ai_theme_analyzer

                        analyzer = get_ai_theme_analyzer()

                        relationships = analyzer.analyze_theme_relationships(
                            themes=st.session_state.themes,
                            codes=st.session_state.codes,
                            analysis_type=analysis_type,
                            research_question=st.session_state.get('research_question', '')
                        )

                        st.session_state.theme_relationships = relationships

                    except Exception as e:
                        st.error(f"❌ {t('themes.relations.failed')}: {str(e)}")

        # 显示关系分析结果
        if st.session_state.get('theme_relationships'):
            st.divider()
            st.write(f"**{t('themes.relations.results.title')}**:")

            relationships = st.session_state.theme_relationships

            # 关系网络
            if relationships.get('network'):
                st.write(f"**{t('themes.relations.results.network')}**:")
                for rel in relationships['network']:
                    rel_type = rel.get('type', 'related')
                    emoji = {"support": "🔄", "contrast": "⚔️", "hierarchy": "📊"}.get(rel_type, "🔗")
                    st.caption(f"{emoji} {rel['theme1']} ──{rel_type}── {rel['theme2']}")
                    if rel.get('explanation'):
                        st.caption(f"   {t('themes.relations.results.reason')}: {rel['explanation']}")

            # 关系矩阵
            if relationships.get('matrix'):
                st.write(f"**{t('themes.relations.results.matrix')}**:")
                import pandas as pd
                df = pd.DataFrame(relationships['matrix'])
                st.dataframe(df)

            # 洞察
            if relationships.get('insights'):
                st.write(f"**{t('themes.relations.results.insights')}**:")
                for insight in relationships['insights']:
                    st.caption(f"💡 {insight}")

    # Tab3: 可视化
    with tab3:
        st.subheader(f"📊 {t('themes.viz.subtitle')}")

        viz_type = st.radio(
            t('themes.viz.type'),
            [t('themes.viz.types.code_frequency'), t('themes.viz.types.theme_distribution')]
        )

        if viz_type == t('themes.viz.types.code_frequency'):
            st.write(f"**{t('themes.viz.code_frequency.title')}**")
            if st.session_state.codes:
                import plotly.express as px
                import pandas as pd

                code_names = [c['name'] for c in st.session_state.codes]
                code_counts = [len(c.get('quotes', [])) for c in st.session_state.codes]

                fig = px.bar(
                    x=code_names,
                    y=code_counts,
                    labels={'x': t('themes.viz.code_frequency.x'), 'y': t('themes.viz.code_frequency.y')},
                    title=t('themes.viz.code_frequency.title')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(t('themes.viz.no_codes'))

        else:  # 主题-编码分布
            st.write(f"**{t('themes.viz.theme_distribution.title')}**")
            if st.session_state.themes:
                import plotly.express as px
                import pandas as pd

                theme_names = [t['name'] for t in st.session_state.themes]
                code_counts = [len(t.get('codes', [])) for t in st.session_state.themes]

                fig = px.pie(
                    values=code_counts,
                    names=theme_names,
                    title=t('themes.viz.theme_distribution.title')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(t('themes.viz.no_themes'))

    # Tab4: 主题管理
    with tab4:
        st.subheader(t('themes.management.subtitle'))

        if st.session_state.themes:
            st.write(f"{t('themes.management.total')}: {len(st.session_state.themes)}")

            # 手动添加主题（支持层级）
            with st.expander(f"➕ {t('themes.management.add_manual')}"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    manual_theme_name = st.text_input(t('themes.management.name_required'), key="manual_theme_name")

                with col2:
                    # 层级主题：选择父主题
                    parent_theme_options = [t('themes.management.no_parent')] + [t['name'] for t in st.session_state.themes]
                    parent_theme = st.selectbox(t('themes.management.parent_theme'), parent_theme_options, key="parent_theme_select")

                manual_theme_desc = st.text_area(t('themes.management.description'), key="manual_theme_desc", height=100)
                manual_theme_def = st.text_area(t('themes.management.academic_definition'), key="manual_theme_def", height=150)

                if st.button(t('themes.management.add'), key="add_manual_theme"):
                    if manual_theme_name:
                        parent_id = None
                        if parent_theme != t('themes.management.no_parent'):
                            parent_id = next((t['id'] for t in st.session_state.themes if t['name'] == parent_theme), None)

                        st.session_state.themes.append({
                            'id': str(uuid.uuid4()),
                            'name': manual_theme_name,
                            'description': manual_theme_desc,
                            'definition': manual_theme_def,
                            'codes': [],
                            'quotes': [],
                            'created_by': 'human',
                            'parent_id': parent_id
                        })
                        st.success(f"✅ {t('themes.management.added')}")
                        st.rerun()

            # 主题层级结构可视化
            st.divider()
            st.write(f"**{t('themes.management.hierarchy.title')}**")

            # 构建层级
            top_level_themes = [t for t in st.session_state.themes if not t.get('parent_id')]

            def render_theme_tree(theme, level=0):
                """递归渲染主题树"""
                indent = "　" * level
                icon = "📂" if any(t.get('parent_id') == theme['id'] for t in st.session_state.themes) else "🎯"

                with st.expander(f"{indent}{icon} {theme['name']}", expanded=False):
                    st.write(f"**{t('themes.management.description')}**: {theme.get('description', t('themes.management.none'))}")
                    st.write(f"**{t('themes.management.definition')}**: {theme.get('definition', t('themes.management.none'))}")

                    if theme.get('codes'):
                        st.write(f"**{t('themes.display.related_codes')}** ({len(theme['codes'])}{t('themes.management.count_unit')}):")
                        st.caption(", ".join(theme['codes'][:5]))

                    if st.button("🗑️", key=f"del_theme_{theme['id']}"):
                        st.session_state.themes = [t for t in st.session_state.themes if t['id'] != theme['id']]
                        st.rerun()

                # 渲染子主题
                children = [t for t in st.session_state.themes if t.get('parent_id') == theme['id']]
                for child in children:
                    render_theme_tree(child, level + 1)

            # 渲染顶层主题
            for theme in top_level_themes:
                render_theme_tree(theme)

            # 跨案例分析
            st.divider()
            st.subheader(f"📊 {t('themes.management.cross_case.title')}")

            with st.expander(t('themes.management.cross_case.execute')):
                st.info(f"💡 {t('themes.management.cross_case.info')}")

                # 选择要对比的主题
                compare_themes = st.multiselect(
                    t('themes.management.cross_case.select'),
                    [t['name'] for t in st.session_state.themes],
                    default=[t['name'] for t in st.session_state.themes[:2]] if len(st.session_state.themes) >= 2 else []
                )

                if st.button(f"🔍 {t('themes.management.cross_case.start')}") and len(compare_themes) >= 2:
                    with st.spinner(t('themes.management.cross_case.spinner')):
                        try:
                            from src.llm.theme_analyzer import get_ai_theme_analyzer
                            
                            analyzer = get_ai_theme_analyzer()
                            
                            # 准备对比数据
                            selected_themes = [t for t in st.session_state.themes if t['name'] in compare_themes]

                            comparison = analyzer.compare_themes(
                                themes=selected_themes,
                                codes=st.session_state.codes
                            )

                            st.success(f"✅ {t('themes.management.cross_case.success')}")

                            # 显示对比结果
                            st.write(f"**{t('themes.management.cross_case.comparison')}**:")

                            if 'comparison_matrix' in comparison:
                                import pandas as pd
                                df = pd.DataFrame(comparison['comparison_matrix'])
                                st.dataframe(df)

                            if 'insights' in comparison:
                                st.write(f"**{t('themes.management.cross_case.insights')}**:")
                                for insight in comparison['insights']:
                                    st.caption(f"💡 {insight}")

                            if 'patterns' in comparison:
                                st.write(f"**{t('themes.management.cross_case.patterns')}**:")
                                for pattern in comparison['patterns']:
                                    st.caption(f"🔍 {pattern}")

                        except Exception as e:
                            st.error(f"{t('themes.management.cross_case.failed')}: {str(e)}")
        else:
            st.info(t('themes.management.no_themes_hint'))


# ==================== 页面4: 报告生成 ====================
def page_reports():
    """报告生成页面（包含高级分析）"""
    st.title(f"📑 {t('reports.title')}")

    # 检查数据
    if not st.session_state.get('themes'):
        st.warning(t('reports.warning_no_themes'))
        return

    st.info(f"📊 {t('reports.current_themes')}: {len(st.session_state.themes)}")

    tab1, tab2, tab3 = st.tabs([t("reports.tabs.generate"), t("reports.tabs.edit"), t("reports.tabs.deep_analysis")])

    # Tab1: 生成报告
    with tab1:
        st.subheader(t('reports.generate.subtitle'))

        # 基础选项
        col1, col2, col3 = st.columns(3)
        with col1:
            report_type = st.selectbox(
                t('reports.generate.type'),
                [t('reports.generate.types.academic'), t('reports.generate.types.research'), t('reports.generate.types.thesis')]
            )
        with col2:
            language = st.selectbox(t('reports.generate.language'), [t('reports.generate.languages.zh'), t('reports.generate.languages.en')])
        with col3:
            ai_provider = st.selectbox(
                t('reports.generate.provider'),
                ["openai", "anthropic", "lm_studio"],
                key="report_provider"
            )

        st.divider()

        # 高级选项
        st.write(f"**{t('reports.generate.advanced_options')}**:")
        st.info(f"💡 {t('reports.generate.advanced_info')}")

        col1, col2 = st.columns(2)

        with col1:
            enable_literature = st.checkbox(f"📚 {t('reports.generate.literature')}", value=True, help=t('reports.generate.literature_help'))
            enable_theory = st.checkbox(f"🎓 {t('reports.generate.theory')}", value=True, help=t('reports.generate.theory_help'))
            enable_novelty = st.checkbox(f"✨ {t('reports.generate.novelty')}", value=True, help=t('reports.generate.novelty_help'))

        with col2:
            enable_limitation = st.checkbox(f"⚠️ {t('reports.generate.limitation')}", value=True, help=t('reports.generate.limitation_help'))
            enable_rigor = st.checkbox(f"🔬 {t('reports.generate.rigor')}", value=True, help=t('reports.generate.rigor_help'))
            enable_counter = st.checkbox(f"🔍 {t('reports.generate.counter')}", value=True, help=t('reports.generate.counter_help'))

        st.divider()

        # 生成按钮
        if st.button(f"🚀 {t('reports.generate.generate_button')}", type="primary", key="generate_report"):
            progress_container = st.container()
            with progress_container:
                st.info(f"🔄 {t('reports.generate.preparing')}")
                progress_bar = st.progress(0)
                status_text = st.empty()

            try:
                import time

                # 准备数据
                status_text.text(f"📊 {t('reports.generate.preparing_data')}...")
                progress_bar.progress(10)

                report_data = {
                    'research_question': st.session_state.get('research_question', ''),
                    'methodology': st.session_state.get('methodology', t('reports.generate.default_methodology')),
                    'themes': st.session_state.themes,
                    'codes': st.session_state.codes,
                    'raw_text': st.session_state.raw_text,
                    'doc_count': 1,
                    'data_source': t('reports.generate.data_source')
                }

                # 获取AI助手
                from src.llm.report_assistant import get_ai_report_assistant
                assistant = get_ai_report_assistant(ai_provider)

                # 生成基础报告
                status_text.text(f"📝 {t('reports.generate.generating_base')}...")
                progress_bar.progress(30)

                lang_code = 'zh' if language == t('reports.generate.languages.zh') else 'en'

                report = {
                    'abstract': assistant.generate_abstract(report_data, st.session_state.themes, lang_code),
                    'introduction': assistant.generate_introduction(report_data, st.session_state.themes, lang_code),
                    'methods': assistant.generate_methods(report_data, st.session_state.themes, lang_code),
                    'results': assistant.generate_results(report_data, st.session_state.themes, lang_code),
                    'discussion': assistant.generate_discussion(report_data, st.session_state.themes, lang_code),
                    'conclusion': assistant.generate_conclusion(report_data, st.session_state.themes, lang_code),
                }

                # 高级分析
                status_text.text(f"🔬 {t('reports.generate.deep_analysis')}...")
                progress_bar.progress(50)

                findings_summary = [f"{t('reports.generate.theme_label')}: {t['name']}" for t in st.session_state.themes]

                if enable_literature:
                    status_text.text(f"📚 {t('reports.generate.literature_analyzing')}...")
                    report['literature_review'] = assistant.literature_dialogue(
                        findings=findings_summary,
                        research_question=report_data['research_question'],
                        language=lang_code
                    )
                    progress_bar.progress(55)

                if enable_theory:
                    status_text.text(f"🎓 {t('reports.generate.theory_aligning')}...")
                    report['theoretical_framework'] = assistant.theoretical_alignment(
                        themes=st.session_state.themes,
                        research_question=report_data['research_question'],
                        language=lang_code
                    )
                    progress_bar.progress(60)

                if enable_novelty:
                    status_text.text(f"✨ {t('reports.generate.novelty_extracting')}...")
                    report['novelty_analysis'] = assistant.extract_novelty(
                        findings=findings_summary,
                        literature=report.get('literature_review', ''),
                        language=lang_code
                    )
                    progress_bar.progress(65)

                if enable_limitation:
                    status_text.text(f"⚠️ {t('reports.generate.limitation_analyzing')}...")
                    report['limitations'] = assistant.analyze_limitations(
                        study_design=report_data,
                        findings=findings_summary,
                        language=lang_code
                    )
                    progress_bar.progress(70)

                if enable_rigor:
                    status_text.text(f"🔬 {t('reports.generate.rigor_checking')}...")
                    report['rigor_assessment'] = assistant.assess_rigor(
                        themes=st.session_state.themes,
                        codes=st.session_state.codes,
                        findings=findings_summary,
                        language=lang_code
                    )
                    progress_bar.progress(75)

                if enable_counter:
                    status_text.text(f"🔍 {t('reports.generate.counter_finding')}...")
                    report['counter_examples'] = assistant.find_counter_examples(
                        findings=findings_summary,
                        raw_text=report_data['raw_text'],
                        language=lang_code
                    )
                    progress_bar.progress(80)

                # 完成
                status_text.text(f"💾 {t('reports.generate.saving')}...")
                progress_bar.progress(95)
                time.sleep(0.5)

                st.session_state.report = report
                progress_bar.progress(100)
                status_text.text(f"✅ {t('reports.generate.complete')}!")

                time.sleep(0.5)
                progress_container.empty()

                st.success(f"🎉 {t('reports.generate.success')}！")
                st.info(f"💡 {t('reports.generate.view_edit_hint')}")

            except Exception as e:
                progress_container.empty()
                st.error(f"❌ {t('reports.generate.failed')}: {str(e)}")

    # Tab2: 在线编辑
    with tab2:
        if st.session_state.get('report'):
            st.write(f"📄 **{t('reports.edit.generated_report')}**")

            report = st.session_state.report

            # 基础章节
            with st.expander(f"📋 {t('reports.edit.abstract')}", expanded=True):
                edited_abstract = st.text_area(
                    t('reports.edit.abstract_label'),
                    report.get('abstract', ''),
                    height=200,
                    key="edit_abstract"
                )
                if st.button(f"💾 {t('reports.edit.save_abstract')}", key="save_abstract"):
                    st.session_state.report['abstract'] = edited_abstract
                    st.success(f"✅ {t('reports.edit.saved')}")

            with st.expander(f"📖 {t('reports.edit.introduction')}"):
                edited_intro = st.text_area(
                    t('reports.edit.introduction_label'),
                    report.get('introduction', ''),
                    height=300,
                    key="edit_intro"
                )

            with st.expander(f"🔬 {t('reports.edit.methods')}"):
                edited_methods = st.text_area(
                    t('reports.edit.methods_label'),
                    report.get('methods', ''),
                    height=300,
                    key="edit_methods"
                )

            with st.expander(f"📊 {t('reports.edit.results')}"):
                st.write(f"**{t('reports.edit.theme_results')}**:")
                for theme in st.session_state.themes:
                    st.write(f"- {theme.get('name', '')}")

            # 高级分析章节
            if report.get('literature_review'):
                with st.expander(f"📚 {t('reports.edit.literature')}"):
                    st.markdown(report['literature_review'])

            if report.get('theoretical_framework'):
                with st.expander(f"🎓 {t('reports.edit.theory')}"):
                    st.markdown(report['theoretical_framework'])

            if report.get('novelty_analysis'):
                with st.expander(f"✨ {t('reports.edit.novelty')}"):
                    st.markdown(report['novelty_analysis'])

            if report.get('limitations'):
                with st.expander(f"⚠️ {t('reports.edit.limitations')}"):
                    st.markdown(report['limitations'])

            if report.get('rigor_assessment'):
                with st.expander(f"🔬 {t('reports.edit.rigor')}"):
                    st.markdown(report['rigor_assessment'])

            if report.get('counter_examples'):
                with st.expander(f"🔍 {t('reports.edit.counter')}"):
                    st.markdown(report['counter_examples'])

            # 导出按钮
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📋 {t('reports.edit.copy_full')}"):
                    full_text = "\n\n".join([
                        report.get('abstract', ''),
                        report.get('introduction', ''),
                        report.get('methods', ''),
                        report.get('results', ''),
                        report.get('discussion', ''),
                        report.get('conclusion', '')
                    ])
                    st.session_state.export_full_text = full_text
                    st.success(f"✅ {t('reports.edit.ready_to_copy')}")

        else:
            st.info(t('reports.edit.generate_first'))

    # Tab3: 深度分析
    with tab3:
        st.subheader(f"🔬 {t('reports.deep_analysis.subtitle')}")

        st.info(f"💡 {t('reports.deep_analysis.info')}")

        col1, col2 = st.columns(2)

        with col1:
            analysis_type = st.selectbox(
                t('reports.deep_analysis.type'),
                [
                    t('reports.deep_analysis.types.cross_theme'),
                    t('reports.deep_analysis.types.code_mapping'),
                    t('reports.deep_analysis.types.saturation'),
                    t('reports.deep_analysis.types.framework')
                ]
            )

        with col2:
            if st.button(f"🔍 {t('reports.deep_analysis.start')}", key="deep_analysis"):
                if not st.session_state.get('themes'):
                    st.warning(t('reports.deep_analysis.no_themes_warning'))
                else:
                    with st.spinner(t('reports.deep_analysis.analyzing')):
                        try:
                            from src.llm.deep_analyzer import get_ai_deep_analyzer
                            analyzer = get_ai_deep_analyzer()

                            result = analyzer.analyze(
                                analysis_type=analysis_type,
                                report=st.session_state.get('report', {}),
                                session_state=st.session_state
                            )

                            st.session_state.deep_analysis = result
                            st.success(f"✅ {t('reports.deep_analysis.complete')}")
                        except Exception as e:
                            st.error(f"❌ {t('reports.deep_analysis.failed')}: {str(e)}")

        # 显示深度分析结果
        if st.session_state.get('deep_analysis'):
            st.divider()
            st.write(f"**{t('reports.deep_analysis.results')}**:")

            result = st.session_state.deep_analysis

            if result.get('findings'):
                st.write(f"**{t('reports.deep_analysis.findings')}**:")
                for finding in result['findings']:
                    st.caption(f"• {finding}")

            if result.get('recommendations'):
                st.write(f"**{t('reports.deep_analysis.recommendations')}**:")
                for rec in result['recommendations']:
                    st.caption(f"→ {rec}")


# ==================== 页面5: 高级可视化 ====================
def page_advanced_viz():
    """高级可视化页面"""
    st.title(f"📊 {t('viz.title')}")

    tab1, tab2, tab3, tab4 = st.tabs([t("viz.tabs.heatmap"), t("viz.tabs.hierarchy"), t("viz.tabs.timeline"), t("viz.tabs.network")])

    # Tab1: 编码-文档热力图
    with tab1:
        st.subheader(t('viz.heatmap.subtitle'))

        if not st.session_state.get('codes'):
            st.warning(t('viz.heatmap.no_codes_warning'))
        else:
            from src.visualization_advanced import create_code_document_heatmap
            
            try:
                fig = create_code_document_heatmap(st.session_state.codes)
                st.plotly_chart(fig, use_container_width=True)

                st.caption(f"💡 {t('viz.heatmap.caption')}")
            except Exception as e:
                st.error(f"{t('viz.heatmap.failed')}: {str(e)}")

    # Tab2: 主题层级旭日图
    with tab2:
        st.subheader(t('viz.hierarchy.subtitle'))

        if not st.session_state.get('themes'):
            st.warning(t('viz.hierarchy.no_themes_warning'))
        else:
            from src.visualization_advanced import create_theme_hierarchy_sunburst
            
            try:
                fig = create_theme_hierarchy_sunburst(
                    st.session_state.themes,
                    st.session_state.codes
                )
                st.plotly_chart(fig, use_container_width=True)

                st.caption(f"💡 {t('viz.hierarchy.caption')}")

                # 添加主题对比雷达图
                st.divider()
                st.subheader(t('viz.hierarchy.comparison_title'))

                from src.visualization_advanced import create_theme_comparison_radar
                fig2 = create_theme_comparison_radar(st.session_state.themes)
                st.plotly_chart(fig2, use_container_width=True)

            except Exception as e:
                st.error(f"{t('viz.hierarchy.failed')}: {str(e)}")

    # Tab3: 时间线可视化
    with tab3:
        st.subheader(t('viz.timeline.subtitle'))

        st.info(f"💡 {t('viz.timeline.info')}")
        
        # 检查是否有叙事分析结果
        if st.session_state.get('narrative_analysis') and \
           'timeline' in st.session_state.narrative_analysis:
            from src.visualization_advanced import create_timeline_visualization
            
            timeline_data = st.session_state.narrative_analysis['timeline']
            
            try:
                fig = create_timeline_visualization(timeline_data)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"{t('viz.timeline.failed')}: {str(e)}")
        else:
            st.caption(t('viz.timeline.no_narrative_hint'))

            # 提供手动输入时间线的选项
            with st.expander(f"✏️ {t('viz.timeline.manual_create')}"):
                st.write(t('viz.timeline.manual_format'))
                timeline_text = st.text_area(
                    t('viz.timeline.event_list'),
                    placeholder=t('viz.timeline.placeholder'),
                    height=150
                )

                if st.button(t('viz.timeline.generate_button')) and timeline_text:
                    events = []
                    for line in timeline_text.split('\n'):
                        if '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 2:
                                events.append({
                                    'time': parts[0].strip(),
                                    'event': parts[1].strip(),
                                    'category': parts[2].strip() if len(parts) > 2 else t('viz.timeline.uncategorized')
                                })

                    if events:
                        from src.visualization_advanced import create_timeline_visualization
                        fig = create_timeline_visualization(events)
                        st.plotly_chart(fig, use_container_width=True)

        # 情感时间线
        if st.session_state.get('sentiment_analysis'):
            st.divider()
            st.subheader(t('viz.timeline.sentiment_title'))

            from src.visualization_advanced import create_sentiment_timeline

            try:
                fig = create_sentiment_timeline(st.session_state.sentiment_analysis)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"{t('viz.timeline.sentiment_failed')}: {str(e)}")

    # Tab4: 网络分析
    with tab4:
        st.subheader(t('viz.network.subtitle'))

        if not st.session_state.get('codes'):
            st.warning(t('viz.network.no_codes_warning'))
        else:
            from src.visualization_advanced import create_code_cooccurrence_network

            min_cooccur = st.slider(t('viz.network.min_cooccur'), 1, 10, 2)

            try:
                fig = create_code_cooccurrence_network(
                    st.session_state.codes,
                    min_cooccurrence=min_cooccur
                )
                st.plotly_chart(fig, use_container_width=True)

                st.caption(f"💡 {t('viz.network.caption')}")
            except Exception as e:
                st.error(f"{t('viz.network.failed')}: {str(e)}")

        # 编码演进图
        if st.session_state.get('coding_evolution'):
            st.divider()
            st.subheader(t('viz.network.evolution_title'))

            from src.visualization_advanced import create_coding_evolution_chart

            try:
                fig = create_coding_evolution_chart(st.session_state.coding_evolution)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"{t('viz.network.evolution_failed')}: {str(e)}")


# ==================== 页面6: 高级分析 ====================
def page_advanced_analysis():
    """高级分析页面"""
    st.title(f"🔬 {t('analysis.title')}")

    tab1, tab2, tab3, tab4 = st.tabs([t("analysis.tabs.sentiment"), t("analysis.tabs.discourse"), t("analysis.tabs.narrative"), t("analysis.tabs.reliability")])

    # Tab1: 情感分析
    with tab1:
        st.subheader(f"💭 {t('analysis.sentiment.subtitle')}")

        st.info(f"💡 {t('analysis.sentiment.info')}")

        if not st.session_state.get('raw_text'):
            st.warning(t('analysis.sentiment.no_text_warning'))
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                analysis_mode = st.radio(
                    t('analysis.sentiment.mode'),
                    [t('analysis.sentiment.modes.full_text'), t('analysis.sentiment.modes.by_paragraph'), t('analysis.sentiment.modes.by_code')]
                )

            with col2:
                if st.button(f"🚀 {t('analysis.sentiment.start')}", type="primary"):
                    with st.spinner(t('analysis.sentiment.spinner')):
                        try:
                            from src.llm.sentiment_analyzer import get_sentiment_analyzer
                            
                            analyzer = get_sentiment_analyzer()

                            if analysis_mode == t('analysis.sentiment.modes.full_text'):
                                result = analyzer.analyze_sentiment(st.session_state.raw_text)

                                st.success(f"✅ {t('analysis.sentiment.analysis_complete')}")

                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric(t('analysis.sentiment.sentiment'), result.sentiment)
                                with col2:
                                    st.metric(t('analysis.sentiment.intensity'), f"{result.intensity:.2f}")
                                with col3:
                                    st.metric(t('analysis.sentiment.dominant_emotion'),
                                             max(result.emotions, key=result.emotions.get) if result.emotions else t('analysis.sentiment.none'))

                                st.write(f"**{t('analysis.sentiment.specific_emotions')}**:")
                                for emotion, score in sorted(result.emotions.items(), key=lambda x: x[1], reverse=True):
                                    st.progress(score, text=f"{emotion}: {score:.2f}")

                                with st.expander(t('analysis.sentiment.reasoning')):
                                    st.write(result.reasoning)
                            
                            elif analysis_mode == t('analysis.sentiment.modes.by_paragraph'):
                                paragraphs = [p.strip() for p in st.session_state.raw_text.split('\n\n') if p.strip()]

                                results = analyzer.batch_analyze(paragraphs)

                                # 情感演化分析
                                evolution = analyzer.analyze_sentiment_evolution(
                                    paragraphs,
                                    labels=[f"{t('analysis.sentiment.paragraph')} {i+1}" for i in range(len(paragraphs))]
                                )

                                st.session_state.sentiment_analysis = evolution

                                st.success(f"✅ {t('analysis.sentiment.analyzed_n_paragraphs')}: {len(paragraphs)}")

                                # 显示统计
                                st.write(f"**{t('analysis.sentiment.distribution')}**:")
                                for sentiment, count in evolution['statistics']['sentiment_distribution'].items():
                                    st.caption(f"- {sentiment}: {count} {t('analysis.sentiment.paragraphs_unit')}")

                                st.write(f"**{t('analysis.sentiment.avg_intensity')}**: {evolution['statistics']['average_intensity']:.2f}")

                                # 显示转折点
                                if evolution['turning_points']:
                                    st.write(f"**{t('analysis.sentiment.turning_points')}**:")
                                    for tp in evolution['turning_points']:
                                        st.caption(f"- {tp['label']}: {tp['from']} → {tp['to']}")
                            
                            else:  # 按编码片段
                                if not st.session_state.codes:
                                    st.warning(t('analysis.sentiment.no_codes_warning'))
                                else:
                                    # 提取所有引用文本
                                    texts = []
                                    for code in st.session_state.codes:
                                        texts.extend(code.get('quotes', []))

                                    if texts:
                                        results = analyzer.batch_analyze(texts[:20])  # 限制数量

                                        st.success(f"✅ {t('analysis.sentiment.analyzed_n_fragments')}: {len(results)}")

                                        # 按编码汇总情感
                                        code_sentiments = {}
                                        for code in st.session_state.codes:
                                            code_name = code['name']
                                            code_quotes = code.get('quotes', [])
                                            if code_quotes:
                                                quote_results = analyzer.batch_analyze(code_quotes[:5])
                                                sentiments = [r.sentiment for r in quote_results]
                                                avg_intensity = sum(r.intensity for r in quote_results) / len(quote_results)

                                                code_sentiments[code_name] = {
                                                    'dominant_sentiment': max(set(sentiments), key=sentiments.count),
                                                    'average_intensity': avg_intensity
                                                }

                                        st.write(f"**{t('analysis.sentiment.code_emotions')}**:")
                                        for code_name, sentiment_info in code_sentiments.items():
                                            st.caption(f"- {code_name}: {sentiment_info['dominant_sentiment']} "
                                                     f"({t('analysis.sentiment.intensity')} {sentiment_info['average_intensity']:.2f})")
                                    else:
                                        st.warning(t('analysis.sentiment.no_quotes_warning'))
                        
                        except Exception as e:
                            st.error(f"{t('analysis.sentiment.failed')}: {str(e)}")

            # 显示已保存的分析结果
            if st.session_state.get('sentiment_analysis'):
                st.divider()
                st.write(f"**{t('analysis.sentiment.saved_results')}**")

                with st.expander(t('analysis.sentiment.view_details')):
                    st.json(st.session_state.sentiment_analysis)

    # Tab2: 话语分析
    with tab2:
        st.subheader(f"🗣️ {t('analysis.discourse.subtitle')}")

        st.info(f"💡 {t('analysis.discourse.info')}")

        if not st.session_state.get('raw_text'):
            st.warning(t('analysis.discourse.no_text_warning'))
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                discourse_focus = st.selectbox(
                    t('analysis.discourse.focus'),
                    ["argumentation", "power", "ideology"],
                    format_func=lambda x: {
                        "argumentation": t('analysis.discourse.focuses.argumentation'),
                        "power": t('analysis.discourse.focuses.power'),
                        "ideology": t('analysis.discourse.focuses.ideology')
                    }[x]
                )

            with col2:
                if st.button(f"🔍 {t('analysis.discourse.start')}", type="primary"):
                    with st.spinner(t('analysis.discourse.spinner')):
                        try:
                            from src.llm.discourse_analyzer import get_discourse_analyzer
                            
                            analyzer = get_discourse_analyzer()
                            result = analyzer.analyze_discourse(
                                st.session_state.raw_text,
                                focus=discourse_focus
                            )
                            
                            st.session_state.discourse_analysis = result

                            st.success(f"✅ {t('analysis.discourse.complete')}")

                            if discourse_focus == "argumentation":
                                st.write(f"**{t('analysis.discourse.argumentation.title')}**:")

                                if 'claims' in result:
                                    st.write(f"**{t('analysis.discourse.argumentation.claims')}**:")
                                    for claim in result['claims']:
                                        st.caption(f"- {claim}")

                                if 'data' in result:
                                    st.write(f"**{t('analysis.discourse.argumentation.data')}**:")
                                    for data in result['data']:
                                        st.caption(f"- {data}")

                                if 'warrants' in result:
                                    st.write(f"**{t('analysis.discourse.argumentation.warrants')}**:")
                                    for warrant in result['warrants']:
                                        st.caption(f"- {warrant}")

                                if 'argument_strength' in result:
                                    st.metric(t('analysis.discourse.argumentation.strength'), f"{result['argument_strength']:.0%}")

                            elif discourse_focus == "power":
                                st.write(f"**{t('analysis.discourse.power.title')}**:")

                                if 'dominant_voices' in result:
                                    st.write(f"**{t('analysis.discourse.power.dominant')}**:")
                                    for voice in result['dominant_voices']:
                                        st.caption(f"- {voice}")

                                if 'marginalized_voices' in result:
                                    st.write(f"**{t('analysis.discourse.power.marginalized')}**:")
                                    for voice in result['marginalized_voices']:
                                        st.caption(f"- {voice}")

                                if 'power_dynamics' in result:
                                    st.write(f"**{t('analysis.discourse.power.dynamics')}**:")
                                    st.write(result['power_dynamics'])

                            else:  # ideology
                                st.write(f"**{t('analysis.discourse.ideology.title')}**:")

                                if 'value_judgments' in result:
                                    st.write(f"**{t('analysis.discourse.ideology.value_judgments')}**:")
                                    for vj in result['value_judgments']:
                                        st.caption(f"- {vj}")

                                if 'assumptions' in result:
                                    st.write(f"**{t('analysis.discourse.ideology.assumptions')}**:")
                                    for assumption in result['assumptions']:
                                        st.caption(f"- {assumption}")

                                if 'ideological_orientation' in result:
                                    st.write(f"**{t('analysis.discourse.ideology.orientation')}**:")
                                    st.write(result['ideological_orientation'])

                            if 'analysis' in result:
                                with st.expander(t('analysis.discourse.comprehensive')):
                                    st.write(result['analysis'])

                        except Exception as e:
                            st.error(f"{t('analysis.discourse.failed')}: {str(e)}")
            
            # 会话分析
            st.divider()
            st.subheader(f"💬 {t('analysis.discourse.conversation.title')}")

            with st.expander(t('analysis.discourse.conversation.input')):
                st.write(t('analysis.discourse.conversation.format'))
                conv_text = st.text_area(
                    t('analysis.discourse.conversation.content'),
                    placeholder=t('analysis.discourse.conversation.placeholder'),
                    height=150
                )

                if st.button(t('analysis.discourse.conversation.analyze')) and conv_text:
                    conversation = []
                    for line in conv_text.split('\n'):
                        if '|' in line:
                            speaker, text = line.split('|', 1)
                            conversation.append({
                                'speaker': speaker.strip(),
                                'text': text.strip()
                            })
                    
                    if conversation:
                        with st.spinner(t('analysis.discourse.conversation.analyzing')):
                            try:
                                from src.llm.discourse_analyzer import get_discourse_analyzer

                                analyzer = get_discourse_analyzer()
                                result = analyzer.analyze_conversation(conversation)

                                st.success(f"✅ {t('analysis.discourse.conversation.complete')}")

                                if 'basic_stats' in result:
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric(t('analysis.discourse.conversation.total_turns'), result['basic_stats']['total_turns'])
                                    with col2:
                                        st.metric(t('analysis.discourse.conversation.speaker_count'), len(result['basic_stats']['speakers']))
                                    with col3:
                                        st.metric(t('analysis.discourse.conversation.avg_length'),
                                                f"{result['basic_stats']['average_turn_length']:.0f}{t('analysis.discourse.conversation.chars_unit')}")

                                with st.expander(t('analysis.discourse.conversation.details')):
                                    st.json(result)

                            except Exception as e:
                                st.error(f"{t('analysis.discourse.conversation.failed')}: {str(e)}")

    # Tab3: 叙事分析
    with tab3:
        st.subheader(f"📖 {t('analysis.narrative.subtitle')}")

        st.info(f"💡 {t('analysis.narrative.info')}")

        if not st.session_state.get('raw_text'):
            st.warning(t('analysis.narrative.no_text_warning'))
        else:
            if st.button(f"📚 {t('analysis.narrative.start')}", type="primary"):
                with st.spinner(t('analysis.narrative.spinner')):
                    try:
                        from src.llm.discourse_analyzer import get_narrative_analyzer
                        
                        analyzer = get_narrative_analyzer()
                        result = analyzer.analyze_narrative(st.session_state.raw_text)

                        st.session_state.narrative_analysis = result

                        st.success(f"✅ {t('analysis.narrative.complete')}")

                        # 显示叙事结构
                        st.write(f"**{t('analysis.narrative.structure')}** ({t('analysis.narrative.labov')}):")

                        if 'orientation' in result:
                            with st.expander(f"1️⃣ {t('analysis.narrative.orientation.title')} - {t('analysis.narrative.orientation.desc')}"):
                                st.write(result['orientation'])

                        if 'complicating_action' in result:
                            with st.expander(f"2️⃣ {t('analysis.narrative.complicating_action.title')} - {t('analysis.narrative.complicating_action.desc')}"):
                                st.write(result['complicating_action'])

                        if 'evaluation' in result:
                            with st.expander(f"3️⃣ {t('analysis.narrative.evaluation.title')} - {t('analysis.narrative.evaluation.desc')}"):
                                st.write(result['evaluation'])

                        if 'resolution' in result:
                            with st.expander(f"4️⃣ {t('analysis.narrative.resolution.title')} - {t('analysis.narrative.resolution.desc')}"):
                                st.write(result['resolution'])

                        if 'coda' in result:
                            with st.expander(f"5️⃣ {t('analysis.narrative.coda.title')} - {t('analysis.narrative.coda.desc')}"):
                                st.write(result['coda'])

                        if 'narrative_type' in result:
                            st.metric(t('analysis.narrative.type'), result['narrative_type'])

                        if 'plot_points' in result:
                            st.write(f"**{t('analysis.narrative.plot_points')}**:")
                            for pp in result['plot_points']:
                                st.caption(f"- {pp}")

                    except Exception as e:
                        st.error(f"{t('analysis.narrative.failed')}: {str(e)}")
            
            # 时间线提取
            st.divider()
            st.subheader(f"⏱️ {t('analysis.narrative.timeline.title')}")

            if st.button(t('analysis.narrative.timeline.extract')):
                with st.spinner(t('analysis.narrative.timeline.extracting')):
                    try:
                        from src.llm.discourse_analyzer import get_narrative_analyzer

                        analyzer = get_narrative_analyzer()

                        # 将文本按段落分割
                        paragraphs = [p.strip() for p in st.session_state.raw_text.split('\n\n') if p.strip()]

                        result = analyzer.extract_timeline(paragraphs[:10])  # 限制段落数

                        if 'timeline' in result:
                            st.session_state.narrative_analysis = result

                            st.success(f"✅ {t('analysis.narrative.timeline.extracted')}: {len(result['timeline'])}")

                            # 显示时间线
                            for event in result['timeline']:
                                st.caption(f"**{event['time']}**: {event['event']}")

                    except Exception as e:
                        st.error(f"{t('analysis.narrative.timeline.failed')}: {str(e)}")

    # Tab4: 编码可靠性
    with tab4:
        st.subheader(f"🎯 {t('analysis.reliability.subtitle')}")

        st.info(f"💡 {t('analysis.reliability.info')}")

        # 多编码者数据输入
        st.write(f"**{t('analysis.reliability.step1')}**")

        with st.expander(t('analysis.reliability.add_coder')):
            coder_name = st.text_input(t('analysis.reliability.coder_name'), key="new_coder_name")

            st.write(t('analysis.reliability.coding_format'))
            coding_text = st.text_area(
                t('analysis.reliability.coding_list'),
                placeholder=t('analysis.reliability.coding_placeholder'),
                height=150,
                key="new_coder_codes"
            )

            if st.button(t('analysis.reliability.add_button')) and coder_name and coding_text:
                codes = [line.strip() for line in coding_text.split('\n') if line.strip()]
                st.session_state.multiple_coders[coder_name] = codes
                st.success(f"✅ {t('analysis.reliability.coder_added')}: {coder_name}, {len(codes)} {t('analysis.reliability.codes_count')}")

        # 显示现有编码者
        if st.session_state.multiple_coders:
            st.write(f"**{t('analysis.reliability.added_coders')}**:")
            for coder, codes in st.session_state.multiple_coders.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"- {coder}: {len(codes)} {t('analysis.reliability.codes_count')}")
                with col2:
                    if st.button(t('analysis.reliability.delete'), key=f"del_coder_{coder}"):
                        del st.session_state.multiple_coders[coder]
                        st.rerun()

            # 计算信度
            if len(st.session_state.multiple_coders) >= 2:
                st.divider()
                st.write(f"**{t('analysis.reliability.step2')}**")

                if st.button(f"🧮 {t('analysis.reliability.calculate')}", type="primary"):
                    with st.spinner(t('analysis.reliability.calculating')):
                        try:
                            from src.utils.reliability import (
                                compare_multiple_coders,
                                identify_disagreements
                            )
                            
                            result = compare_multiple_coders(st.session_state.multiple_coders)

                            st.success(f"✅ {t('analysis.reliability.calculation_complete')}")

                            # 显示整体信度
                            if 'overall_reliability' in result and result['overall_reliability']:
                                st.write(f"**{t('analysis.reliability.overall')}** (Krippendorff's Alpha):")
                                alpha_info = result['overall_reliability']

                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric(t('analysis.reliability.alpha'), f"{alpha_info['alpha']:.3f}")
                                with col2:
                                    st.metric(t('analysis.reliability.evaluation'), alpha_info['interpretation'])

                                st.caption(f"{t('analysis.reliability.items')}: {alpha_info['n_items']}, {t('analysis.reliability.coders')}: {alpha_info['n_coders']}")

                            # 显示两两比较
                            st.divider()
                            st.write(f"**{t('analysis.reliability.pairwise')}**:")

                            for pair_name, pair_result in result['pairwise_comparisons'].items():
                                with st.expander(f"📊 {pair_name.replace('_vs_', ' vs ')}"):
                                    col1, col2 = st.columns(2)

                                    with col1:
                                        st.metric(t('analysis.reliability.percent_agreement'),
                                                f"{pair_result['percent_agreement']:.1%}")

                                    with col2:
                                        kappa = pair_result['cohens_kappa']
                                        st.metric("Cohen's Kappa", f"{kappa['kappa']:.3f}")

                                    st.caption(f"{t('analysis.reliability.interpretation')}: {kappa['interpretation']}")

                                    # 显示不一致的位置
                                    coder1_name, coder2_name = pair_name.split('_vs_')
                                    disagreements = identify_disagreements(
                                        st.session_state.multiple_coders[coder1_name],
                                        st.session_state.multiple_coders[coder2_name]
                                    )

                                    if disagreements:
                                        st.write(f"**{t('analysis.reliability.disagreements')}** ({len(disagreements)}{t('analysis.reliability.count_unit')}):")
                                        for dis in disagreements[:5]:  # 只显示前5个
                                            st.caption(f"{t('analysis.reliability.position')}{dis['index']}: "
                                                     f"{dis['coder1_code']} vs {dis['coder2_code']}")

                                        if len(disagreements) > 5:
                                            st.caption(f"...{t('analysis.reliability.more_disagreements')} {len(disagreements)-5} {t('analysis.reliability.disagreement_unit')}")

                        except Exception as e:
                            st.error(f"{t('analysis.reliability.calculation_failed')}: {str(e)}")
            else:
                st.info(t('analysis.reliability.min_coders'))
        else:
            st.info(t('analysis.reliability.add_data_first'))
        
        # 编码演进追踪
        st.divider()
        st.subheader(f"📈 {t('analysis.reliability.evolution.title')}")

        if st.button(f"💾 {t('analysis.reliability.evolution.save')}"):
            if st.session_state.codes:
                import datetime

                version = {
                    'version': f"v{len(st.session_state.coding_evolution) + 1}",
                    'timestamp': datetime.datetime.now().isoformat(),
                    'codes': [{'name': c['name'], 'description': c.get('description', '')}
                             for c in st.session_state.codes]
                }

                st.session_state.coding_evolution.append(version)
                st.success(f"✅ {t('analysis.reliability.evolution.saved_as')} {version['version']}")
            else:
                st.warning(t('analysis.reliability.evolution.no_codes'))

        if st.session_state.coding_evolution:
            st.write(f"**{t('analysis.reliability.evolution.history')}** ({len(st.session_state.coding_evolution)}{t('analysis.reliability.evolution.versions_unit')})")

            for ver in st.session_state.coding_evolution:
                with st.expander(f"{ver['version']} - {ver['timestamp'][:10]}"):
                    st.write(f"{t('analysis.reliability.evolution.code_count')}: {len(ver['codes'])}")
                    st.caption(f"{t('analysis.reliability.evolution.code_list')}: " + ", ".join([c['name'] for c in ver['codes'][:10]]))
                    if len(ver['codes']) > 10:
                        st.caption(f"...{t('analysis.reliability.evolution.more_codes')} {len(ver['codes'])-10} {t('analysis.reliability.evolution.codes_unit')}")


# ==================== 页面7: 导出下载 ====================
def page_export():
    """导出下载页面"""
    st.title(f"💾 {t('export.title')}")

    st.info(f"💡 {t('export.info')}")

    tab1, tab2, tab3, tab4 = st.tabs([t("export.tabs.codebook"), t("export.tabs.themes"), t("export.tabs.reports"), t("export.tabs.project")])

    # Tab1: 编码本导出
    with tab1:
        st.subheader(f"📋 {t('export.codebook.subtitle')}")

        if not st.session_state.codes:
            st.warning(t('export.codebook.no_codes_warning'))
        else:
            export_format = st.selectbox(
                t('export.codebook.select_format'),
                [t('export.codebook.formats.csv'), t('export.codebook.formats.json'), t('export.codebook.formats.md'), t('export.codebook.formats.excel')],
                key="codebook_format"
            )

            if st.button(t('export.codebook.generate_button')):
                try:
                    if export_format == "CSV":
                        import pandas as pd
                        
                        df = pd.DataFrame([{
                            '编码名称': c['name'],
                            '描述': c.get('description', ''),
                            '引用数': len(c.get('quotes', [])),
                            '创建方式': c.get('created_by', 'unknown'),
                            '置信度': c.get('confidence', '')
                        } for c in st.session_state.codes])
                        
                        csv = df.to_csv(index=False, encoding='utf-8-sig')

                        st.download_button(
                            label=f"📥 {t('export.codebook.download_csv')}",
                            data=csv,
                            file_name="codebook.csv",
                            mime="text/csv"
                        )

                    elif export_format == t('export.codebook.formats.json'):
                        import json

                        json_str = json.dumps(st.session_state.codes, ensure_ascii=False, indent=2)

                        st.download_button(
                            label=f"📥 {t('export.codebook.download_json')}",
                            data=json_str,
                            file_name="codebook.json",
                            mime="application/json"
                        )

                    elif export_format == t('export.codebook.formats.md'):
                        import pandas as pd
                        md_content = f"# {t('export.codebook.codebook_title')}\n\n"
                        md_content += f"{t('export.codebook.generated')}: {pd.Timestamp.now()}\n\n"
                        md_content += f"{t('export.codebook.total_codes')}: {len(st.session_state.codes)}\n\n"
                        md_content += "---\n\n"

                        for i, code in enumerate(st.session_state.codes, 1):
                            md_content += f"## {i}. {code['name']}\n\n"
                            md_content += f"**{t('export.codebook.description')}**: {code.get('description', t('export.codebook.none'))}\n\n"
                            md_content += f"**{t('export.codebook.quote_count')}**: {len(code.get('quotes', []))}\n\n"

                            if code.get('quotes'):
                                md_content += f"**{t('export.codebook.typical_quotes')}**:\n\n"
                                for quote in code['quotes'][:3]:
                                    md_content += f"> {quote[:100]}...\n\n"

                            md_content += "---\n\n"

                        st.download_button(
                            label=f"📥 {t('export.codebook.download_md')}",
                            data=md_content,
                            file_name="codebook.md",
                            mime="text/markdown"
                        )

                    elif export_format == t('export.codebook.formats.excel'):
                        import pandas as pd
                        from io import BytesIO
                        
                        # 创建Excel文件
                        output = BytesIO()
                        
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            # 编码概览
                            df_overview = pd.DataFrame([{
                                '编码名称': c['name'],
                                '描述': c.get('description', ''),
                                '引用数': len(c.get('quotes', [])),
                                '创建方式': c.get('created_by', 'unknown')
                            } for c in st.session_state.codes])
                            df_overview.to_excel(writer, sheet_name='编码概览', index=False)
                            
                            # 编码-引用详情
                            quote_data = []
                            for code in st.session_state.codes:
                                for quote in code.get('quotes', []):
                                    quote_data.append({
                                        '编码名称': code['name'],
                                        '引用内容': quote[:200] if isinstance(quote, str) else str(quote)[:200]
                                    })
                            
                            if quote_data:
                                df_quotes = pd.DataFrame(quote_data)
                                df_quotes.to_excel(writer, sheet_name='编码引用', index=False)
                        
                        excel_data = output.getvalue()

                        st.download_button(
                            label=f"📥 {t('export.codebook.download_excel')}",
                            data=excel_data,
                            file_name="codebook.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                except Exception as e:
                    st.error(f"{t('export.codebook.failed')}: {str(e)}")

    # Tab2: 主题导出
    with tab2:
        st.subheader(f"🎯 {t('export.themes.subtitle')}")

        if not st.session_state.themes:
            st.warning(t('export.themes.no_themes_warning'))
        else:
            export_format = st.selectbox(
                t('export.themes.select_format'),
                [t('export.themes.formats.md'), t('export.themes.formats.json'), t('export.themes.formats.word'), t('export.themes.formats.pdf')],
                key="theme_format"
            )

            if st.button(t('export.themes.generate_button')):
                try:
                    if export_format == t('export.themes.formats.md'):
                        import pandas as pd
                        md_content = f"# {t('export.themes.title')}\n\n"
                        md_content += f"{t('export.themes.generated')}: {pd.Timestamp.now()}\n\n"
                        md_content += f"{t('export.themes.total')}: {len(st.session_state.themes)}\n\n"
                        md_content += "---\n\n"

                        for i, theme in enumerate(st.session_state.themes, 1):
                            md_content += f"## {t('export.themes.theme_label')} {i}: {theme['name']}\n\n"
                            md_content += f"**{t('export.themes.description')}**: {theme.get('description', t('export.themes.none'))}\n\n"
                            md_content += f"**{t('export.themes.definition')}**: {theme.get('definition', t('export.themes.none'))}\n\n"

                            if theme.get('codes'):
                                md_content += f"**{t('export.themes.related_codes')}** ({len(theme['codes'])}{t('export.themes.count_unit')}):\n\n"
                                for code in theme['codes']:
                                    md_content += f"- {code}\n"
                                md_content += "\n"

                            if theme.get('quotes'):
                                md_content += f"**{t('export.themes.typical_quotes')}**:\n\n"
                                for quote in theme['quotes'][:3]:
                                    quote_text = quote if isinstance(quote, str) else str(quote)
                                    md_content += f"> {quote_text[:200]}...\n\n"

                            md_content += "---\n\n"

                        st.download_button(
                            label=f"📥 {t('export.themes.download_md')}",
                            data=md_content,
                            file_name="themes.md",
                            mime="text/markdown"
                        )

                    elif export_format == t('export.themes.formats.json'):
                        import json
                        
                        json_str = json.dumps(st.session_state.themes, ensure_ascii=False, indent=2)

                        st.download_button(
                            label=f"📥 {t('export.themes.download_json')}",
                            data=json_str,
                            file_name="themes.json",
                            mime="application/json"
                        )

                    else:
                        st.info(f"{export_format} {t('export.themes.coming_soon')}")

                except Exception as e:
                    st.error(f"{t('export.themes.failed')}: {str(e)}")

    # Tab3: 报告导出
    with tab3:
        st.subheader(f"📑 {t('export.reports.subtitle')}")

        if not st.session_state.get('report'):
            st.warning(t('export.reports.no_report_warning'))
        else:
            export_format = st.selectbox(
                t('export.reports.select_format'),
                [t('export.reports.formats.md'), t('export.reports.formats.word'), t('export.reports.formats.pdf'), t('export.reports.formats.html')],
                key="report_format"
            )

            if st.button(t('export.reports.generate_button')):
                try:
                    report = st.session_state.report

                    if export_format == t('export.reports.formats.md'):
                        md_content = f"# {t('export.reports.report_title')}\n\n"

                        if report.get('abstract'):
                            md_content += f"## {t('export.reports.abstract')}\n\n"
                            md_content += report['abstract'] + "\n\n"

                        if report.get('introduction'):
                            md_content += f"## {t('export.reports.introduction')}\n\n"
                            md_content += report['introduction'] + "\n\n"

                        if report.get('methods'):
                            md_content += f"## {t('export.reports.methods')}\n\n"
                            md_content += report['methods'] + "\n\n"

                        if report.get('results'):
                            md_content += f"## {t('export.reports.results')}\n\n"
                            md_content += report['results'] + "\n\n"

                        if report.get('discussion'):
                            md_content += f"## {t('export.reports.discussion')}\n\n"
                            md_content += report['discussion'] + "\n\n"

                        if report.get('conclusion'):
                            md_content += f"## {t('export.reports.conclusion')}\n\n"
                            md_content += report['conclusion'] + "\n\n"

                        # 高级分析部分
                        if report.get('literature_review'):
                            md_content += f"## {t('export.reports.literature')}\n\n"
                            md_content += report['literature_review'] + "\n\n"

                        if report.get('theoretical_framework'):
                            md_content += f"## {t('export.reports.theory')}\n\n"
                            md_content += report['theoretical_framework'] + "\n\n"

                        st.download_button(
                            label=f"📥 {t('export.reports.download_md')}",
                            data=md_content,
                            file_name="research_report.md",
                            mime="text/markdown"
                        )

                    else:
                        st.info(f"{export_format} {t('export.reports.coming_soon')}")

                except Exception as e:
                    st.error(f"{t('export.reports.failed')}: {str(e)}")

    # Tab4: 完整项目
    with tab4:
        st.subheader(f"📦 {t('export.project.subtitle')}")

        st.info(f"💡 {t('export.project.info')}")

        if st.button(t('export.project.pack_button')):
            try:
                import json
                import datetime
                
                project_data = {
                    'export_time': datetime.datetime.now().isoformat(),
                    'version': '2.0',
                    'research_question': st.session_state.get('research_question', ''),
                    'methodology': st.session_state.get('methodology', ''),
                    'raw_text': st.session_state.get('raw_text', ''),
                    'codes': st.session_state.get('codes', []),
                    'themes': st.session_state.get('themes', []),
                    'report': st.session_state.get('report'),
                    'sentiment_analysis': st.session_state.get('sentiment_analysis'),
                    'discourse_analysis': st.session_state.get('discourse_analysis'),
                    'narrative_analysis': st.session_state.get('narrative_analysis'),
                    'coding_evolution': st.session_state.get('coding_evolution', []),
                    'theme_relationships': st.session_state.get('theme_relationships')
                }
                
                json_str = json.dumps(project_data, ensure_ascii=False, indent=2)

                st.download_button(
                    label=f"📥 {t('export.project.download_button')}",
                    data=json_str,
                    file_name=f"project_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

                st.success(f"✅ {t('export.project.packed_success')}")

            except Exception as e:
                st.error(f"{t('export.project.pack_failed')}: {str(e)}")

        st.divider()
        st.subheader(f"📂 {t('export.project.import_title')}")

        uploaded_file = st.file_uploader(t('export.project.select_file'), type=['json'])

        if uploaded_file is not None:
            if st.button(t('export.project.import_button'), type="primary"):
                try:
                    import json

                    project_data = json.load(uploaded_file)

                    # 恢复数据
                    st.session_state.research_question = project_data.get('research_question', '')
                    st.session_state.methodology = project_data.get('methodology', '')
                    st.session_state.raw_text = project_data.get('raw_text', '')
                    st.session_state.codes = project_data.get('codes', [])
                    st.session_state.themes = project_data.get('themes', [])
                    st.session_state.report = project_data.get('report')
                    st.session_state.sentiment_analysis = project_data.get('sentiment_analysis')
                    st.session_state.discourse_analysis = project_data.get('discourse_analysis')
                    st.session_state.narrative_analysis = project_data.get('narrative_analysis')
                    st.session_state.coding_evolution = project_data.get('coding_evolution', [])
                    st.session_state.theme_relationships = project_data.get('theme_relationships')

                    st.success(f"✅ {t('export.project.import_success')}")
                    st.rerun()

                except Exception as e:
                    st.error(f"{t('export.project.import_failed')}: {str(e)}")


# ==================== 页面8: 关于 ====================
def page_settings():
    """关于页面"""
    st.title(f"ℹ️ {t('settings.title')}")

    st.write(f"**{t('settings.app_title')}**")

    st.markdown(f"""
    {t('settings.description')}

    - 📝 {t('settings.feature1')}
    - 🏷️ {t('settings.feature2')}
    - 🎯 {t('settings.feature3')}
    - 📑 {t('settings.feature4')}

    **{t('settings.features_label')}**:
    - {t('settings.feature_item1')}
    - {t('settings.feature_item2')}
    - {t('settings.feature_item3')}
    - {t('settings.feature_item4')}
    - {t('settings.feature_item5')}
    - {t('settings.feature_item6')}
    - {t('settings.feature_item7')}

    **{t('settings.version_label')}**: v3.0 ({t('settings.version_desc')})

    **{t('settings.new_in')} v3.0:
    - ✨ {t('settings.new1')}
    - 🗣️ {t('settings.new2')}
    - 📖 {t('settings.new3')}
    - 🎯 {t('settings.new4')}
    - 📊 {t('settings.new5')}
    - 📈 {t('settings.new6')}
    - 💾 {t('settings.new7')}
    """)

    st.divider()
    st.write(f"**{t('settings.workflow_title')}**:")
    st.caption(f"1. 📝 {t('settings.workflow_step1')}")
    st.caption(f"2. 📝 {t('settings.workflow_step2')}")
    st.caption(f"3. 🏷️ {t('settings.workflow_step3')}")
    st.caption(f"4. 🎯 {t('settings.workflow_step4')}")
    st.caption(f"5. 📊 {t('settings.workflow_step5')}")
    st.caption(f"6. 🔬 {t('settings.workflow_step6')}")
    st.caption(f"7. 📑 {t('settings.workflow_step7')}")
    st.caption(f"8. 💾 {t('settings.workflow_step8')}")

    st.divider()
    st.write(f"**{t('settings.advanced_tools_title')}**:")
    st.caption(f"• {t('settings.tool1')}")
    st.caption(f"• {t('settings.tool2')}")
    st.caption(f"• {t('settings.tool3')}")
    st.caption(f"• {t('settings.tool4')}")
    st.caption(f"• {t('settings.tool5')}")
    st.caption(f"• {t('settings.tool6')}")

    st.divider()
    st.write(f"**{t('settings.supported_llm_title')}:**")
    st.caption(f"• {t('settings.llm1')}")
    st.caption(f"• {t('settings.llm2')}")
    st.caption(f"• {t('settings.llm3')}")


# ==================== 主函数 ====================
# ==================== 主函数（新布局）====================
def main():
    """主函数 - 基于工作流程的布局"""
    # 初始化Session State
    init_session_state()

    # 注入学术风格CSS
    inject_academic_css()

    # 渲染增强型水平导航栏（替代顶部导航和工作流程进度）
    render_horizontal_nav()

    # 根据工作流程步骤渲染对应内容
    workflow_step = st.session_state.get('workflow_step', 0)

    # 页面映射
    page_map = {
        0: page_dashboard,       # 主页（介绍+配置）
        1: page_text_input,      # 数据准备
        2: page_coding,          # AI编码
        3: page_themes,          # 主题分析
        4: page_advanced_viz,    # 可视化
        5: page_advanced_analysis,  # 深度分析
        6: page_reports,         # 报告生成
        7: page_export,          # 导出下载
    }

    # 渲染对应页面
    if workflow_step in page_map:
        page_map[workflow_step]()
    else:
        # 默认显示主页
        page_dashboard()


if __name__ == "__main__":
    main()
