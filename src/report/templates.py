"""
IMRAD报告模板
支持中英文双语报告生成
"""

from typing import Dict, List
from datetime import datetime


class IMRADTemplate:
    """IMRAD结构报告模板"""

    # 中文模板
    TEMPLATE_ZH = {
        'title_page': {
            'title': '研究标题',
            'author': '作者',
            'date': '日期',
            'abstract_label': '摘要'
        },
        'sections': [
            {'id': 'introduction', 'title': '1. 引言', 'level': 1},
            {'id': 'methods', 'title': '2. 方法', 'level': 1},
            {'id': 'results', 'title': '3. 结果', 'level': 1},
            {'id': 'discussion', 'title': '4. 讨论', 'level': 1},
            {'id': 'conclusion', 'title': '5. 结论', 'level': 1},
            {'id': 'references', 'title': '参考文献', 'level': 1},
        ]
    }

    # 英文模板
    TEMPLATE_EN = {
        'title_page': {
            'title': 'Research Title',
            'author': 'Author',
            'date': 'Date',
            'abstract_label': 'Abstract'
        },
        'sections': [
            {'id': 'introduction', 'title': '1. Introduction', 'level': 1},
            {'id': 'methods', 'title': '2. Methods', 'level': 1},
            {'id': 'results', 'title': '3. Results', 'level': 1},
            {'id': 'discussion', 'title': '4. Discussion', 'level': 1},
            {'id': 'conclusion', 'title': '5. Conclusion', 'level': 1},
            {'id': 'references', 'title': 'References', 'level': 1},
        ]
    }

    def __init__(self):
        """初始化模板"""
        pass

    def get_template(self, language: str = 'zh') -> Dict:
        """
        获取指定语言的模板

        Args:
            language: 语言代码 ('zh' 或 'en')

        Returns:
            模板字典
        """
        if language == 'en':
            return self.TEMPLATE_EN.copy()
        return self.TEMPLATE_ZH.copy()

    def get_sections(self, language: str = 'zh') -> List[Dict]:
        """
        获取报告章节列表

        Args:
            language: 语言代码

        Returns:
            章节列表
        """
        template = self.get_template(language)
        return template['sections']

    def get_section_title(self, section_id: str, language: str = 'zh') -> str:
        """
        获取章节标题

        Args:
            section_id: 章节ID (如 'introduction', 'methods')
            language: 语言代码

        Returns:
            章节标题
        """
        sections = self.get_sections(language)
        for section in sections:
            if section['id'] == section_id:
                return section['title']
        return section_id

    def create_empty_report(self, project_data: Dict, language: str = 'zh') -> Dict:
        """
        创建空的报告结构

        Args:
            project_data: 项目数据
            language: 语言代码

        Returns:
            空报告结构
        """
        template = self.get_template(language)

        # 生成标题
        title = project_data.get('research_question', '研究报告')
        if language == 'en':
            title = f"A Study on {title}" if project_data.get('research_question') else "Research Report"

        report = {
            'title': title,
            'author': '研究者',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'abstract': '',
            'introduction': '',
            'methods': '',
            'results': [],
            'discussion': '',
            'conclusion': '',
            'references': [],
            'language': language
        }

        # 添加章节占位符
        sections = self.get_sections(language)
        for section in sections:
            section_id = section['id']
            if section_id not in ['results', 'references']:
                report[section_id] = f"[{section['title']}]\n\n待生成内容..."

        return report

    def format_results_section(self, themes: List[Dict], language: str = 'zh') -> List[Dict]:
        """
        格式化结果部分的主题结构

        Args:
            themes: 主题列表
            language: 语言代码

        Returns:
            格式化的结果部分
        """
        results = []

        for theme in themes:
            theme_data = {
                'theme_id': theme.get('id'),
                'theme_name': theme.get('name'),
                'description': theme.get('description', ''),
                'definition': theme.get('definition', ''),
                'codes': [],
                'quotes': []
            }

            # 添加关联编码
            if theme.get('codes'):
                for code in theme['codes']:
                    theme_data['codes'].append({
                        'code_name': code.get('name'),
                        'color': code.get('color'),
                        'relevance': code.get('relevance_score', 1.0)
                    })

            # 添加典型引用
            if theme.get('quotes'):
                for quote in theme['quotes']:
                    theme_data['quotes'].append({
                        'text': quote.get('text_content'),
                        'source': quote.get('document_filename'),
                        'type': quote.get('quote_type', 'supporting')
                    })

            results.append(theme_data)

        return results

    def get_word_count_target(self, section: str, language: str = 'zh') -> int:
        """
        获取各部分的建议字数

        Args:
            section: 章节ID
            language: 语言代码

        Returns:
            建议字数
        """
        # 中文字数目标
        targets_zh = {
            'abstract': 300,
            'introduction': 800,
            'methods': 1000,
            'results': 2000,
            'discussion': 1200,
            'conclusion': 400
        }

        # 英文字数目标（约1.5倍）
        targets_en = {
            'abstract': 250,
            'introduction': 600,
            'methods': 800,
            'results': 1500,
            'discussion': 900,
            'conclusion': 300
        }

        if language == 'en':
            return targets_en.get(section, 500)
        return targets_zh.get(section, 500)

    def get_section_prompt(self, section: str, language: str = 'zh') -> str:
        """
        获取各部分的AI生成提示

        Args:
            section: 章节ID
            language: 语言代码

        Returns:
            提示信息
        """
        if language == 'en':
            prompts = {
                'abstract': 'Generate a concise abstract summarizing the research background, methods, key findings, and conclusions.',
                'introduction': 'Write an introduction that provides research background, states the research question, explains the significance, and outlines the paper structure.',
                'methods': 'Describe the research design, data collection procedures, data analysis methods, and quality control measures.',
                'results': 'Present findings organized by themes. Each theme should include description, supporting quotes, and data evidence.',
                'discussion': 'Summarize key findings, discuss relationships between themes, address limitations, and suggest future research directions.',
                'conclusion': 'Summarize the research contributions and theoretical/practical implications.'
            }
        else:
            prompts = {
                'abstract': '生成简洁的摘要，包括研究背景、研究方法、主要发现和结论。',
                'introduction': '撰写引言，包括研究背景、研究问题、研究意义和论文结构。',
                'methods': '描述研究设计、数据收集过程、分析方法和质量控制措施。',
                'results': '按主题呈现发现。每个主题应包含描述、支持性引用和数据证据。',
                'discussion': '总结主要发现，讨论主题间关系，指出研究局限性和未来研究方向。',
                'conclusion': '总结研究贡献和理论/实践意义。'
            }

        return prompts.get(section, '')

    def validate_report_structure(self, report: Dict) -> tuple[bool, List[str]]:
        """
        验证报告结构是否完整

        Args:
            report: 报告数据

        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        required_sections = ['title', 'introduction', 'methods', 'results', 'discussion', 'conclusion']

        for section in required_sections:
            if section not in report:
                errors.append(f"缺少必需章节: {section}")
            elif not report[section]:
                errors.append(f"章节内容为空: {section}")

        return len(errors) == 0, errors
