# -*- coding: utf-8 -*-
"""
QualInsight Pages Module
所有页面模块的统一入口
"""

from .dashboard import render_dashboard
from .data_preparation import render_data_preparation
from .coding import render_coding
from .theme_analysis import render_theme_analysis
from .visualization import render_visualization
from .deep_analysis import render_deep_analysis
from .report import render_report
from .export import render_export
from .settings import render_settings

__all__ = [
    "render_dashboard",
    "render_data_preparation",
    "render_coding",
    "render_theme_analysis",
    "render_visualization",
    "render_deep_analysis",
    "render_report",
    "render_export",
    "render_settings",
]
