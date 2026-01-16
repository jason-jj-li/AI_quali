"""
报告生成器
负责整合报告生成的完整流程
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器"""

    def __init__(self, db):
        """
        初始化报告生成器

        Args:
            db: 数据库实例
        """
        self.db = db

    def generate_report(self, project_id: str, options: Optional[Dict] = None) -> Dict:
        """
        生成报告

        Args:
            project_id: 项目ID
            options: 报告选项
                - report_type: 报告类型 ('paper', 'thesis', 'report')
                - language: 语言 ('zh', 'en')
                - citation_style: 引用格式 ('APA', 'MLA', 'Chicago')
                - include_figures: 是否包含图表

        Returns:
            报告数据
        """
        if options is None:
            options = {}

        # 默认选项
        report_type = options.get('report_type', 'paper')
        language = options.get('language', 'zh')
        citation_style = options.get('citation_style', 'APA')

        # 获取项目数据
        project = self.db.get_project(project_id)
        if not project:
            raise ValueError(f"项目不存在: {project_id}")

        # 获取主题数据
        themes = self.db.list_themes(project_id)
        if not themes:
            raise ValueError("项目没有主题数据，请先完成主题分析")

        # 为每个主题获取详细数据
        themes_with_data = []
        for theme in themes:
            theme_data = self._get_theme_with_details(theme['id'])
            if theme_data:
                themes_with_data.append(theme_data)

        # 构建报告结构
        report = {
            'project_id': project_id,
            'title': self._generate_title(project, language),
            'author': '研究者',  # 可以从项目配置获取
            'date': datetime.now().strftime('%Y-%m-%d'),
            'abstract': '',
            'introduction': '',
            'methods': '',
            'results': themes_with_data,
            'discussion': '',
            'conclusion': '',
            'references': [],
            'language': language,
            'citation_style': citation_style,
            'report_type': report_type,
            'metadata': {
                'research_question': project.get('research_question'),
                'methodology': project.get('methodology'),
                'themes_count': len(themes_with_data)
            }
        }

        return report

    def _get_theme_with_details(self, theme_id: str) -> Optional[Dict]:
        """
        获取主题的详细信息

        Args:
            theme_id: 主题ID

        Returns:
            主题详细数据
        """
        theme = self.db.get_theme(theme_id)
        if not theme:
            return None

        # 获取关联编码
        codes = self.db.get_theme_codes_with_stats(theme_id)

        # 获取典型引用
        quotes = self.db.get_theme_quotes(theme_id)

        return {
            'id': theme['id'],
            'name': theme['name'],
            'description': theme.get('description', ''),
            'definition': theme.get('definition', ''),
            'codes': codes,
            'quotes': quotes
        }

    def _generate_title(self, project: Dict, language: str) -> str:
        """
        生成报告标题

        Args:
            project: 项目数据
            language: 语言

        Returns:
            报告标题
        """
        research_question = project.get('research_question', '')

        if language == 'en':
            if research_question:
                return f"A Study on {research_question}"
            return "Qualitative Research Report"
        else:
            if research_question:
                return research_question
            return project.get('name', '研究报告')

    def save_report(self, report: Dict) -> str:
        """
        保存报告到数据库

        Args:
            report: 报告数据

        Returns:
            报告ID
        """
        project_id = report.get('project_id')
        title = report.get('title')

        # 构建内容JSON（只保存文本部分）
        content = {
            'abstract': report.get('abstract', ''),
            'introduction': report.get('introduction', ''),
            'methods': report.get('methods', ''),
            'discussion': report.get('discussion', ''),
            'conclusion': report.get('conclusion', ''),
            'references': report.get('references', [])
        }

        report_id = self.db.create_report(
            project_id=project_id,
            title=title,
            report_type=report.get('report_type', 'paper'),
            language=report.get('language', 'zh'),
            citation_style=report.get('citation_style', 'APA'),
            content=content
        )

        return report_id

    def update_report_content(self, report_id: str, section: str, content: str):
        """
        更新报告的特定部分

        Args:
            report_id: 报告ID
            section: 章节ID (introduction, methods, etc.)
            content: 新内容
        """
        self.db.update_report_content(report_id, section, content)

    def get_report(self, report_id: str) -> Optional[Dict]:
        """
        获取报告

        Args:
            report_id: 报告ID

        Returns:
            报告数据
        """
        return self.db.get_report(report_id)

    def list_reports(self, project_id: str) -> List[Dict]:
        """
        列出项目的所有报告

        Args:
            project_id: 项目ID

        Returns:
            报告列表
        """
        return self.db.list_reports(project_id)

    def delete_report(self, report_id: str):
        """
        删除报告

        Args:
            report_id: 报告ID
        """
        self.db.delete_report(report_id)

    def validate_project_for_report(self, project_id: str) -> tuple[bool, List[str]]:
        """
        验证项目是否可以生成报告

        Args:
            project_id: 项目ID

        Returns:
            (是否可以生成, 错误列表)
        """
        errors = []

        # 检查项目是否存在
        project = self.db.get_project(project_id)
        if not project:
            errors.append("项目不存在")
            return False, errors

        # 检查是否有主题
        themes = self.db.list_themes(project_id)
        if not themes:
            errors.append("项目没有主题数据，请先完成主题分析")

        # 检查主题是否有编码
        for theme in themes:
            codes = self.db.get_theme_codes(theme['id'])
            if not codes:
                errors.append(f"主题 '{theme['name']}' 没有关联编码")

        # 检查主题是否有引用
        for theme in themes:
            quotes = self.db.get_theme_quotes(theme['id'])
            if not quotes:
                # 这是一个警告，不是错误
                logger.warning(f"主题 '{theme['name']}' 没有典型引用")

        return len(errors) == 0, errors

    def get_report_summary(self, report_id: str) -> Dict:
        """
        获取报告摘要信息

        Args:
            report_id: 报告ID

        Returns:
            报告摘要
        """
        report = self.db.get_report(report_id)
        if not report:
            return {}

        content = report.get('content', {})

        return {
            'id': report['id'],
            'title': report['title'],
            'report_type': report.get('report_type'),
            'language': report.get('language'),
            'status': report.get('status', 'draft'),
            'created_at': report.get('created_at'),
            'updated_at': report.get('updated_at'),
            'has_abstract': bool(content.get('abstract')),
            'has_introduction': bool(content.get('introduction')),
            'has_methods': bool(content.get('methods')),
            'has_discussion': bool(content.get('discussion')),
            'has_conclusion': bool(content.get('conclusion')),
            'completion_rate': self._calculate_completion_rate(content)
        }

    def _calculate_completion_rate(self, content: Dict) -> float:
        """
        计算报告完成度

        Args:
            content: 报告内容

        Returns:
            完成度 (0-1)
        """
        required_sections = ['abstract', 'introduction', 'methods', 'discussion', 'conclusion']
        completed = sum(1 for section in required_sections if content.get(section))
        return completed / len(required_sections)
