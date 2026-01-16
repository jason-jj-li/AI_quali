"""
引用格式化器
支持多种引用格式：APA, MLA, Chicago等
"""

from typing import Dict, List


class CitationFormatter:
    """引用格式化器"""

    # 引用格式配置
    FORMAT_CONFIGS = {
        'APA': {
            'in_text_template': '[{source}, {participant}]',
            'reference_template': '{source}. ({year}). {title}.',
            'name': 'APA'
        },
        'MLA': {
            'in_text_template': '({source} {participant})',
            'reference_template': '{source}. "{title}." {journal}, {year}.',
            'name': 'MLA'
        },
        'Chicago': {
            'in_text_template': '({source} {year})',
            'reference_template': '{source}. {title}. {publisher}, {year}.',
            'name': 'Chicago'
        }
    }

    def __init__(self):
        """初始化格式化器"""
        self.supported_styles = list(self.FORMAT_CONFIGS.keys())

    def format_citation(self, quote: Dict, style: str = 'APA',
                        language: str = 'zh') -> str:
        """
        格式化单个引用

        Args:
            quote: 引用数据，包含:
                - text_content: 引用文本
                - document_filename: 来源文档
                - start_pos, end_pos: 位置
                - participant_id: 参与者ID（如果有）
            style: 引用格式 (APA, MLA, Chicago)
            language: 语言 (zh, en)

        Returns:
            格式化后的引用
        """
        config = self.FORMAT_CONFIGS.get(style, self.FORMAT_CONFIGS['APA'])

        # 提取来源信息
        source = quote.get('document_filename', 'Unknown')
        # 移除文件扩展名
        if '.' in source:
            source = source.rsplit('.', 1)[0]

        # 参与者信息
        participant = quote.get('participant_id', 'P01')
        if not participant:
            participant = 'Unknown'

        # 格式化文中引用
        in_text = config['in_text_template'].format(
            source=source,
            participant=participant,
            year='2024'  # 可以从文档元数据获取
        )

        return in_text

    def format_quote_with_citation(self, quote: Dict, style: str = 'APA',
                                   language: str = 'zh') -> str:
        """
        格式化带引用标记的引用文本

        Args:
            quote: 引用数据
            style: 引用格式
            language: 语言

        Returns:
            格式化后的引用文本
        """
        citation = self.format_citation(quote, style, language)
        text = quote.get('text_content', '')

        if language == 'en':
            return f'"{text}" ({citation})'
        return f'"{text}" —— {citation}'

    def format_reference_list(self, quotes: List[Dict], style: str = 'APA',
                             language: str = 'zh') -> List[str]:
        """
        格式化参考文献列表

        Args:
            quotes: 引用列表
            style: 引用格式
            language: 语言

        Returns:
            格式化后的参考文献列表
        """
        references = []
        seen_sources = set()

        for quote in quotes:
            source = quote.get('document_filename', 'Unknown')
            if '.' in source:
                source = source.rsplit('.', 1)[0]

            # 去重
            if source in seen_sources:
                continue
            seen_sources.add(source)

            config = self.FORMAT_CONFIGS.get(style, self.FORMAT_CONFIGS['APA'])

            if language == 'en':
                reference = config['reference_template'].format(
                    source=source,
                    title='Interview Data',
                    journal='Journal',
                    year='2024',
                    publisher='Research Archive'
                )
            else:
                reference = f'{source}. (2024). 访谈数据.'

            references.append(reference)

        return references

    def select_quotes_for_theme(self, theme: Dict, max_quotes: int = 5) -> List[Dict]:
        """
        为主题选择最佳引用

        Args:
            theme: 主题数据，包含:
                - quotes: 引用列表
            max_quotes: 最大引用数量

        Returns:
            选择的引用列表
        """
        all_quotes = theme.get('quotes', [])
        if not all_quotes:
            return []

        # 按类型分组
        supporting = [q for q in all_quotes if q.get('quote_type') == 'supporting']
        deviant = [q for q in all_quotes if q.get('quote_type') == 'deviant']
        borderline = [q for q in all_quotes if q.get('quote_type') == 'borderline']

        selected = []

        # 优先选择支持性引用（约占70%）
        num_supporting = min(int(max_quotes * 0.7), len(supporting))
        selected.extend(supporting[:num_supporting])

        # 添加偏离性引用（约占20%）
        if len(selected) < max_quotes:
            num_deviant = min(int(max_quotes * 0.2), len(deviant))
            selected.extend(deviant[:num_deviant])

        # 添加边界案例（约占10%）
        if len(selected) < max_quotes:
            remaining = max_quotes - len(selected)
            selected.extend(borderline[:remaining])

        return selected[:max_quotes]

    def format_theme_results(self, theme: Dict, style: str = 'APA',
                            language: str = 'zh') -> Dict:
        """
        格式化主题结果（包含引用）

        Args:
            theme: 主题数据
            style: 引用格式
            language: 语言

        Returns:
            格式化后的主题结果
        """
        # 选择最佳引用
        selected_quotes = self.select_quotes_for_theme(theme)

        # 格式化引用
        formatted_quotes = []
        for quote in selected_quotes:
            formatted_quotes.append({
                'text': quote.get('text_content', ''),
                'citation': self.format_citation(quote, style, language),
                'type': quote.get('quote_type', 'supporting'),
                'source': quote.get('document_filename', '')
            })

        return {
            'theme_name': theme.get('name', ''),
            'description': theme.get('description', ''),
            'definition': theme.get('definition', ''),
            'quotes': formatted_quotes,
            'code_names': [c.get('name') for c in theme.get('codes', [])]
        }

    def get_supported_styles(self) -> List[str]:
        """
        获取支持的引用格式列表

        Returns:
            引用格式列表
        """
        return self.supported_styles.copy()

    def validate_style(self, style: str) -> bool:
        """
        验证引用格式是否支持

        Args:
            style: 引用格式

        Returns:
            是否支持
        """
        return style in self.supported_styles
