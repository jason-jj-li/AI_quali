"""
AI辅助质性研究平台 - 报告生成模块

该模块负责生成学术研究报告，支持IMRAD结构。
"""

from .generator import ReportGenerator
from .templates import IMRADTemplate
from .formatter import CitationFormatter
from .exporter import WordExporter

__all__ = [
    'ReportGenerator',
    'IMRADTemplate',
    'CitationFormatter',
    'WordExporter',
]


def get_report_generator():
    """获取报告生成器实例"""
    from src.utils.database import get_db
    return ReportGenerator(get_db())


def get_imrad_template():
    """获取IMRAD模板实例"""
    return IMRADTemplate()


def get_citation_formatter():
    """获取引用格式化器实例"""
    return CitationFormatter()


def get_word_exporter():
    """获取Word导出器实例"""
    return WordExporter()
