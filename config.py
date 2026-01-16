"""
AI辅助质性研究平台 - 配置文件
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = BASE_DIR / "prompts"

# 数据库配置
DATABASE_PATH = DATA_DIR / "qualitative_research.db"

# LLM提供商配置（简化版）
SUPPORTED_LLM_PROVIDERS = {
    "lm_studio": {
        "name": "本地模型 (LM Studio)",
        "type": "local",
        "models": ["local-model", "custom-model"],
        "default_model": "local-model",
        "default_base_url": "http://localhost:1234/v1",
        "api_key_required": False,
    },
    "openai": {
        "name": "OpenAI",
        "type": "online",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "default_model": "gpt-4o-mini",
        "api_key_required": True,
        "api_key_pattern": "^sk-",
    },
    "deepseek": {
        "name": "Deepseek",
        "type": "online",
        "models": ["deepseek-chat", "deepseek-coder"],
        "default_model": "deepseek-chat",
        "api_key_required": True,
        "api_key_pattern": "^sk-",
        "base_url": "https://api.deepseek.com/v1",
    },
}

# 默认LLM配置（默认使用本地模型）
DEFAULT_LLM_CONFIG = {
    "provider": "lm_studio",
    "model": "local-model",
    "temperature": 0.3,
    "max_tokens": 2000,
}

# 质性研究方法论选项
METHODOLOGY_OPTIONS = [
    "现象学分析",
    "扎根理论",
    "个案研究",
    "叙事研究",
    "民族志",
    "话语分析",
    "内容分析",
    "主题分析",
    "其他",
]

# 支持的文档格式
SUPPORTED_DOC_FORMATS = [".txt", ".pdf", ".docx"]
SUPPORTED_AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".mp4"]
SUPPORTED_VIDEO_FORMATS = [".mp4", ".mov", ".avi"]

# 编码颜色预设（用于区分不同编码）
CODE_COLORS = [
    "#FF5733",  # 红色
    "#33FF57",  # 绿色
    "#3357FF",  # 蓝色
    "#FF33A8",  # 粉色
    "#33FFF5",  # 青色
    "#F5FF33",  # 黄色
    "#FF8C33",  # 橙色
    "#8C33FF",  # 紫色
    "#FF3333",  # 深红
    "#33FF8C",  # 浅绿
]

# Streamlit配置
STREAMLIT_CONFIG = {
    "page_title": "AI辅助质性研究平台",
    "page_icon": "🔬",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# 导出格式
EXPORT_FORMATS = {
    "codebook": ["csv", "xlsx", "json"],
    "report": ["md", "pdf", "docx"],
    "codings": ["csv", "json"],
}
