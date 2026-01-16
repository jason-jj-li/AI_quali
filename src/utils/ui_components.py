"""
UI组件库 - 统一的视觉设计系统
提供现代化的UI组件和样式
"""
import streamlit as st


# ==================== CSS样式系统 ====================
def inject_custom_css():
    """注入自定义CSS样式"""
    st.markdown("""
    <style>
    /* ========== 配色系统 ========== */
    :root {
        --primary: #2E86DE;
        --primary-light: #5FA3E8;
        --primary-dark: #1B5FA3;
        
        --accent: #26C281;
        --accent-light: #54D9A1;
        --accent-dark: #1E9B68;
        
        --gray-50: #F8F9FA;
        --gray-100: #E9ECEF;
        --gray-200: #DEE2E6;
        --gray-700: #495057;
        --gray-900: #212529;
        
        --success: #26C281;
        --warning: #F39C12;
        --danger: #E74C3C;
        --info: #3498DB;
        
        --gradient-primary: linear-gradient(135deg, #2E86DE 0%, #5FA3E8 100%);
        --gradient-accent: linear-gradient(135deg, #26C281 0%, #54D9A1 100%);
    }
    
    /* ========== 全局样式 ========== */
    .main {
        padding: 2rem 1rem;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ========== 侧边栏样式 ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8F9FA 0%, #FFFFFF 100%);
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    
    /* ========== 按钮样式 ========== */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    
    .stButton > button[kind="primary"] {
        background: var(--gradient-primary) !important;
        color: white !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(46,134,222,0.3) !important;
    }
    
    /* ========== 输入框样式 ========== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 2px solid var(--gray-200) !important;
        transition: border-color 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(46,134,222,0.1) !important;
    }
    
    /* ========== Tab样式 ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--gray-50);
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gradient-primary) !important;
        color: white !important;
    }
    
    /* ========== 指标卡片样式 ========== */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--primary) !important;
    }
    
    /* ========== 警告/信息框样式 ========== */
    .stAlert {
        border-radius: 10px !important;
        border: none !important;
        padding: 1rem 1.5rem !important;
    }
    
    /* ========== 进度条样式 ========== */
    .stProgress > div > div > div > div {
        background: var(--gradient-primary) !important;
    }
    
    /* ========== 选择框样式 ========== */
    .stSelectbox > div > div > div {
        border-radius: 8px !important;
    }
    
    /* ========== 复选框和单选框 ========== */
    .stCheckbox, .stRadio {
        padding: 0.5rem 0;
    }
    
    /* ========== 数据框样式 ========== */
    .dataframe {
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    
    /* ========== 代码块样式 ========== */
    .stCodeBlock {
        border-radius: 8px !important;
    }
    
    /* ========== 动画 ========== */
    @keyframes slideInFromLeft {
        0% {
            transform: translateX(-100%);
            opacity: 0;
        }
        100% {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeIn {
        0% {
            opacity: 0;
        }
        100% {
            opacity: 1;
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    .animate-slide-in {
        animation: slideInFromLeft 0.5s ease-out;
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)


# ==================== 卡片组件 ====================
def render_card(title, content, icon="📊", border_color="#2E86DE", bg_color="#FFFFFF"):
    """渲染卡片组件"""
    st.markdown(f"""
    <div style="
        border-left: 4px solid {border_color};
        padding: 1.5rem;
        border-radius: 10px;
        background: {bg_color};
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    ">
        <h3 style="margin: 0 0 0.5rem 0; color: {border_color}; display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <span>{title}</span>
        </h3>
        <div style="color: #495057; line-height: 1.6;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card(label, value, icon="📊", color="#2E86DE", delta=None):
    """渲染统计卡片"""
    delta_html = ""
    if delta:
        delta_color = "#26C281" if delta > 0 else "#E74C3C"
        delta_icon = "↑" if delta > 0 else "↓"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.9rem; margin-top: 0.5rem;">{delta_icon} {abs(delta)}%</div>'
    
    st.markdown(f"""
    <div style="
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, {color}15 0%, {color}05 100%);
        border: 2px solid {color}30;
        text-align: center;
        transition: transform 0.3s ease;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 2rem; font-weight: 700; color: {color}; margin-bottom: 0.3rem;">{value}</div>
        <div style="font-size: 0.9rem; color: #495057; text-transform: uppercase; letter-spacing: 0.5px;">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_highlight_card(title, content, icon="✨", gradient="linear-gradient(135deg, #2E86DE 0%, #5FA3E8 100%)"):
    """渲染高亮卡片（带渐变背景）"""
    st.markdown(f"""
    <div style="
        padding: 2rem;
        border-radius: 16px;
        background: {gradient};
        color: white;
        box-shadow: 0 8px 24px rgba(46,134,222,0.3);
        margin: 1rem 0;
    ">
        <h2 style="margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 2rem;">{icon}</span>
            <span>{title}</span>
        </h2>
        <div style="font-size: 1.1rem; line-height: 1.8; opacity: 0.95;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==================== 进度指示器 ====================
def render_workflow_progress(current_step, total_steps=3):
    """渲染工作流程进度条"""
    steps = ["📋 数据准备", "🔍 编码分析", "📊 可视报告"]
    
    progress_html = '<div style="display: flex; justify-content: space-between; align-items: center; margin: 2rem 0;">'
    
    for i, step in enumerate(steps[:total_steps], 1):
        is_current = i == current_step
        is_completed = i < current_step
        
        if is_completed:
            color = "#26C281"
            status = "✓"
            opacity = "1"
        elif is_current:
            color = "#2E86DE"
            status = "●"
            opacity = "1"
        else:
            color = "#DEE2E6"
            status = "○"
            opacity = "0.5"
        
        progress_html += f"""
        <div style="flex: 1; text-align: center; opacity: {opacity};">
            <div style="
                width: 60px;
                height: 60px;
                margin: 0 auto 0.5rem;
                border-radius: 50%;
                background: {color};
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                font-weight: 700;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            ">{status}</div>
            <div style="font-size: 0.9rem; font-weight: 600; color: {color};">{step}</div>
        </div>
        """
        
        if i < total_steps:
            line_color = "#26C281" if is_completed else "#DEE2E6"
            progress_html += f'<div style="flex: 0.5; height: 3px; background: {line_color}; margin-bottom: 2rem;"></div>'
    
    progress_html += '</div>'
    st.markdown(progress_html, unsafe_allow_html=True)


# ==================== 徽章组件 ====================
def render_badge(text, type="info"):
    """渲染状态徽章"""
    colors = {
        "success": ("#26C281", "✓"),
        "warning": ("#F39C12", "⚠"),
        "danger": ("#E74C3C", "✕"),
        "info": ("#3498DB", "ℹ"),
        "primary": ("#2E86DE", "●")
    }
    
    color, icon = colors.get(type, colors["info"])
    
    return f"""
    <span style="
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        background: {color}20;
        color: {color};
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    ">{icon} {text}</span>
    """


# ==================== 智能提示组件 ====================
def render_smart_tip(message, type="info", action_text=None, action_callback=None):
    """渲染智能提示"""
    icons = {
        "success": "✅",
        "info": "💡",
        "warning": "⚠️",
        "error": "❌",
        "tip": "💡"
    }
    
    colors = {
        "success": "#26C281",
        "info": "#3498DB",
        "warning": "#F39C12",
        "error": "#E74C3C",
        "tip": "#2E86DE"
    }
    
    icon = icons.get(type, "💡")
    color = colors.get(type, "#3498DB")
    
    st.markdown(f"""
    <div style="
        padding: 1rem 1.5rem;
        border-radius: 10px;
        background: {color}10;
        border-left: 4px solid {color};
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    ">
        <div style="font-size: 1.5rem;">{icon}</div>
        <div style="flex: 1; color: #495057;">{message}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if action_text and action_callback:
        if st.button(action_text, key=f"tip_action_{hash(message)}"):
            action_callback()


# ==================== 加载动画 ====================
def render_loading_message(message, progress=None, tip=None):
    """渲染增强的加载消息"""
    st.markdown(f"""
    <div style="
        padding: 2rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #F8F9FA 0%, #FFFFFF 100%);
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin: 2rem 0;
    ">
        <div style="font-size: 3rem; margin-bottom: 1rem; animation: pulse 2s infinite;">🤖</div>
        <h3 style="color: #2E86DE; margin-bottom: 0.5rem;">{message}</h3>
        {"<div style='color: #26C281; font-weight: 600; margin-top: 1rem;'>进度: " + str(progress) + "%</div>" if progress else ""}
        {"<div style='color: #495057; font-size: 0.9rem; margin-top: 1rem; font-style: italic;'>💡 " + tip + "</div>" if tip else ""}
    </div>
    """, unsafe_allow_html=True)


# ==================== 空状态组件 ====================
def render_empty_state(title, message, icon="📭", action_text=None, action_callback=None):
    """渲染空状态"""
    st.markdown(f"""
    <div style="
        padding: 3rem 2rem;
        text-align: center;
        background: #F8F9FA;
        border-radius: 12px;
        margin: 2rem 0;
    ">
        <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;">{icon}</div>
        <h3 style="color: #495057; margin-bottom: 0.5rem;">{title}</h3>
        <p style="color: #6c757d; margin-bottom: 2rem;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if action_text and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_text, type="primary", use_container_width=True):
                action_callback()


# ==================== 确认对话框 ====================
def render_confirm_dialog(message, confirm_text="确认", cancel_text="取消"):
    """渲染确认对话框（需要配合st.dialog使用）"""
    st.warning(f"⚠️ {message}")
    col1, col2 = st.columns(2)
    with col1:
        cancel = st.button(cancel_text, use_container_width=True)
    with col2:
        confirm = st.button(confirm_text, type="primary", use_container_width=True)
    return confirm, cancel
