"""
AI报告生成助手模块
实现AI辅助学术报告生成功能
支持IMRAD结构：引言、方法、结果、讨论、结论
支持中英文双语
"""
import json
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from src.llm.base import LLMConfig, LLMProvider


@dataclass
class ReportSectionResult:
    """报告章节生成结果"""
    section: str  # 章节ID (introduction, methods, etc.)
    content: str  # 生成的内容
    word_count: int  # 字数
    language: str  # 语言
    tokens_used: Dict[str, int]  # token使用情况


@dataclass
class FullReportResult:
    """完整报告生成结果"""
    abstract: str
    introduction: str
    methods: str
    results: str  # 结果部分内容（主题描述）
    discussion: str
    conclusion: str

    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {
            'abstract': self.abstract,
            'introduction': self.introduction,
            'methods': self.methods,
            'results': self.results,
            'discussion': self.discussion,
            'conclusion': self.conclusion
        }


class AIReportAssistant:
    """
    AI报告生成助手

    支持功能：
    1. 生成完整IMRAD结构报告
    2. 分章节生成（引言、方法、结果、讨论、结论）
    3. 生成摘要
    4. 支持中英文双语
    """

    def __init__(self, provider: LLMProvider):
        """
        初始化AI报告生成助手

        Args:
            provider: LLM提供商实例
        """
        self.provider = provider
        self._load_prompts()

    def _load_prompts(self):
        """加载提示词模板"""
        import os
        from pathlib import Path
        import sys
        sys.path.append(str(Path(__file__).parent.parent.parent))
        from config import PROMPTS_DIR

        # 加载报告生成提示词
        report_prompts_path = PROMPTS_DIR / "report.txt"
        if report_prompts_path.exists():
            with open(report_prompts_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
                # 执行提示词文件以获取模板
                exec_globals = {}
                exec(report_content, exec_globals)

                # 系统提示词
                self.system_prompt_zh = exec_globals.get('SYSTEM_PROMPT_ZH', '')
                self.system_prompt_en = exec_globals.get('SYSTEM_PROMPT_EN', '')

                # 双语提示词模板
                self.prompts_bilingual = {
                    'introduction': exec_globals.get('INTRODUCTION_BILINGUAL', {}),
                    'methods': exec_globals.get('METHODS_BILINGUAL', {}),
                    'results': exec_globals.get('RESULTS_BILINGUAL', {}),
                    'discussion': exec_globals.get('DISCUSSION_BILINGUAL', {}),
                    'conclusion': exec_globals.get('CONCLUSION_BILINGUAL', {}),
                    'abstract': exec_globals.get('ABSTRACT_BILINGUAL', {})
                }

                # 辅助函数
                self.format_themes_simple = exec_globals.get('format_themes_for_prompt', self._default_format_themes)
                self.format_themes_detailed = exec_globals.get('format_themes_detailed', self._default_format_themes_detailed)
        else:
            # 使用默认提示词
            self.system_prompt_zh = "你是一位资深的质性研究方法学专家和学术写作专家。"
            self.system_prompt_en = "You are a senior qualitative research methodologist and academic writing expert."
            self.prompts_bilingual = {}
            self.format_themes_simple = self._default_format_themes
            self.format_themes_detailed = self._default_format_themes_detailed

    def generate_full_report(
        self,
        project_data: Dict[str, Any],
        themes: List[Dict[str, Any]],
        language: str = 'zh',
        sections: Optional[List[str]] = None
    ) -> FullReportResult:
        """
        生成完整报告

        Args:
            project_data: 项目数据
                - research_question: 研究问题
                - methodology: 研究方法
                - doc_count: 文档数量
                - code_count: 编码数量
                - theme_count: 主题数量
            themes: 主题列表（包含详细信息）
            language: 语言 ('zh' 或 'en')
            sections: 要生成的章节列表，None表示全部

        Returns:
            完整报告结果
        """
        if sections is None:
            sections = ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion']

        result = FullReportResult(
            abstract='',
            introduction='',
            methods='',
            results='',
            discussion='',
            conclusion=''
        )

        # 按顺序生成各部分
        for section in sections:
            if section == 'abstract':
                result.abstract = self.generate_abstract(project_data, themes, language)
            elif section == 'introduction':
                result.introduction = self.generate_introduction(project_data, themes, language)
            elif section == 'methods':
                result.methods = self.generate_methods(project_data, themes, language)
            elif section == 'results':
                result.results = self.generate_results(project_data, themes, language)
            elif section == 'discussion':
                result.discussion = self.generate_discussion(project_data, themes, language)
            elif section == 'conclusion':
                result.conclusion = self.generate_conclusion(project_data, themes, language)

        return result

    def generate_abstract(
        self,
        project_data: Dict[str, Any],
        themes: List[Dict[str, Any]],
        language: str = 'zh'
    ) -> str:
        """生成摘要"""
        # 准备数据
        research_question = project_data.get('research_question', '')
        methodology = project_data.get('methodology', '')
        themes_summary = self._get_themes_summary(themes, language)

        # 获取提示词模板
        prompt_template = self._get_prompt_template('abstract', language)
        if not prompt_template:
            # 使用默认提示词
            if language == 'zh':
                prompt = f"""请基于以下信息撰写摘要（250-350字）：

研究问题：{research_question}
研究方法：{methodology}
主要发现：{themes_summary}

请直接输出摘要内容。"""
            else:
                prompt = f"""Please write an abstract (200-300 words) based on:

Research Question: {research_question}
Methodology: {methodology}
Key Findings: {themes_summary}

Please output the abstract directly."""
        else:
            prompt = prompt_template.format(
                research_question=research_question,
                methodology=methodology,
                themes_summary=themes_summary
            )

        # 获取系统提示词
        system_prompt = self.system_prompt_zh if language == 'zh' else self.system_prompt_en

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=1000
            )
            return response.content.strip()
        except Exception as e:
            if language == 'zh':
                return f"[摘要生成失败: {str(e)}]"
            return f"[Abstract generation failed: {str(e)}]"

    def generate_introduction(
        self,
        project_data: Dict[str, Any],
        themes: List[Dict[str, Any]],
        language: str = 'zh'
    ) -> str:
        """生成引言"""
        # 准备数据
        research_question = project_data.get('research_question', '')
        methodology = project_data.get('methodology', '')
        themes_list = self.format_themes_simple(themes, language)

        # 获取提示词模板
        prompt_template = self._get_prompt_template('introduction', language)
        if not prompt_template:
            if language == 'zh':
                prompt = f"""请撰写引言部分（800-1000字）：

研究问题：{research_question}
研究方法：{methodology}
识别出的主题：
{themes_list}

请直接输出引言内容。"""
            else:
                prompt = f"""Please write the introduction (600-800 words):

Research Question: {research_question}
Methodology: {methodology}
Identified Themes:
{themes_list}

Please output the introduction directly."""
        else:
            prompt = prompt_template.format(
                research_question=research_question,
                methodology=methodology,
                themes_list=themes_list
            )

        # 获取系统提示词
        system_prompt = self.system_prompt_zh if language == 'zh' else self.system_prompt_en

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=2000
            )
            return response.content.strip()
        except Exception as e:
            if language == 'zh':
                return f"[引言生成失败: {str(e)}]"
            return f"[Introduction generation failed: {str(e)}]"

    def generate_methods(
        self,
        project_data: Dict[str, Any],
        themes: List[Dict[str, Any]],
        language: str = 'zh'
    ) -> str:
        """生成方法部分"""
        # 准备数据
        methodology = project_data.get('methodology', '')
        doc_count = project_data.get('doc_count', len(project_data.get('documents', [])))
        code_count = project_data.get('code_count', 0)
        theme_count = len(themes)
        participants = project_data.get('participants', 'N/A')

        # 获取提示词模板
        prompt_template = self._get_prompt_template('methods', language)
        if not prompt_template:
            if language == 'zh':
                prompt = f"""请撰写方法部分（1000-1200字）：

研究方法：{methodology}
文档数量：{doc_count} 个
参与者：{participants}
编码数量：{code_count} 个
主题数量：{theme_count} 个

请直接输出方法内容。"""
            else:
                prompt = f"""Please write the methods section (800-1000 words):

Methodology: {methodology}
Documents: {doc_count}
Participants: {participants}
Codes: {code_count}
Themes: {theme_count}

Please output the methods directly."""
        else:
            prompt = prompt_template.format(
                methodology=methodology,
                doc_count=doc_count,
                participants=participants,
                code_count=code_count,
                theme_count=theme_count
            )

        # 获取系统提示词
        system_prompt = self.system_prompt_zh if language == 'zh' else self.system_prompt_en

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=2500
            )
            return response.content.strip()
        except Exception as e:
            if language == 'zh':
                return f"[方法生成失败: {str(e)}]"
            return f"[Methods generation failed: {str(e)}]"

    def generate_results(
        self,
        project_data: Dict[str, Any],
        themes: List[Dict[str, Any]],
        language: str = 'zh'
    ) -> str:
        """生成结果部分"""
        # 准备数据
        research_question = project_data.get('research_question', '')
        methodology = project_data.get('methodology', '')
        themes_data = self.format_themes_detailed(themes, language)

        # 获取提示词模板
        prompt_template = self._get_prompt_template('results', language)
        if not prompt_template:
            if language == 'zh':
                prompt = f"""请撰写结果部分（2000-3000字）：

研究问题：{research_question}
研究方法：{methodology}

主题数据：
{themes_data}

请按主题组织，每个主题包含定义、描述和典型引用。"""
            else:
                prompt = f"""Please write the results section (1500-2500 words):

Research Question: {research_question}
Methodology: {methodology}

Theme Data:
{themes_data}

Please organize by themes, each including definition, description, and representative quotes."""
        else:
            prompt = prompt_template.format(
                research_question=research_question,
                methodology=methodology,
                themes_data=themes_data
            )

        # 获取系统提示词
        system_prompt = self.system_prompt_zh if language == 'zh' else self.system_prompt_en

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=4000
            )
            return response.content.strip()
        except Exception as e:
            if language == 'zh':
                return f"[结果生成失败: {str(e)}]"
            return f"[Results generation failed: {str(e)}]"

    def generate_discussion(
        self,
        project_data: Dict[str, Any],
        themes: List[Dict[str, Any]],
        language: str = 'zh'
    ) -> str:
        """生成讨论部分"""
        # 准备数据
        research_question = project_data.get('research_question', '')
        themes_summary = self._get_themes_summary(themes, language)

        # 获取提示词模板
        prompt_template = self._get_prompt_template('discussion', language)
        if not prompt_template:
            if language == 'zh':
                prompt = f"""请撰写讨论部分（1200-1500字）：

研究问题：{research_question}

研究发现：
{themes_summary}

请包含发现总结、主题关系、理论意义、实践意义、局限性和未来方向。"""
            else:
                prompt = f"""Please write the discussion section (900-1200 words):

Research Question: {research_question}

Research Findings:
{themes_summary}

Please include summary of findings, theme relationships, theoretical implications, practical implications, limitations, and future directions."""
        else:
            prompt = prompt_template.format(
                research_question=research_question,
                themes_summary=themes_summary
            )

        # 获取系统提示词
        system_prompt = self.system_prompt_zh if language == 'zh' else self.system_prompt_en

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=3000
            )
            return response.content.strip()
        except Exception as e:
            if language == 'zh':
                return f"[讨论生成失败: {str(e)}]"
            return f"[Discussion generation failed: {str(e)}]"

    def generate_conclusion(
        self,
        project_data: Dict[str, Any],
        themes: List[Dict[str, Any]],
        language: str = 'zh'
    ) -> str:
        """生成结论部分"""
        # 准备数据
        research_question = project_data.get('research_question', '')
        themes_summary = self._get_themes_summary(themes, language)

        # 获取提示词模板
        prompt_template = self._get_prompt_template('conclusion', language)
        if not prompt_template:
            if language == 'zh':
                prompt = f"""请撰写结论部分（400-500字）：

研究问题：{research_question}

研究发现：
{themes_summary}

请包含研究总结、研究贡献和最终结语。"""
            else:
                prompt = f"""Please write the conclusion section (300-400 words):

Research Question: {research_question}

Research Findings:
{themes_summary}

Please include research summary, contributions, and final concluding remark."""
        else:
            prompt = prompt_template.format(
                research_question=research_question,
                themes_summary=themes_summary
            )

        # 获取系统提示词
        system_prompt = self.system_prompt_zh if language == 'zh' else self.system_prompt_en

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=1500
            )
            return response.content.strip()
        except Exception as e:
            if language == 'zh':
                return f"[结论生成失败: {str(e)}]"
            return f"[Conclusion generation failed: {str(e)}]"

    def _get_prompt_template(self, section: str, language: str) -> Optional[str]:
        """获取指定章节和语言的提示词模板"""
        if section in self.prompts_bilingual:
            return self.prompts_bilingual[section].get(language)
        return None

    def _get_themes_summary(self, themes: List[Dict], language: str) -> str:
        """获取主题摘要"""
        if language == 'zh':
            prefix = f"本研究识别出 {len(themes)} 个主题："
        else:
            prefix = f"This study identified {len(themes)} themes:"

        theme_list = []
        for i, theme in enumerate(themes, 1):
            name = theme.get('name', '')
            desc = theme.get('description', '')[:150]
            theme_list.append(f"{i}. {name}: {desc}...")

        return prefix + "\n" + "\n".join(theme_list)

    def _default_format_themes(self, themes: List[Dict], language: str) -> str:
        """默认主题格式化"""
        lines = []
        for i, theme in enumerate(themes, 1):
            name = theme.get('name', '')
            desc = theme.get('description', '')[:100]
            lines.append(f"{i}. {name}: {desc}...")
        return "\n".join(lines)

    def _default_format_themes_detailed(self, themes: List[Dict], language: str) -> str:
        """默认详细主题格式化"""
        lines = []
        for i, theme in enumerate(themes, 1):
            name = theme.get('name', '')
            definition = theme.get('definition', '')
            description = theme.get('description', '')

            if language == 'zh':
                lines.append(f"### 主题 {i}: {name}")
                lines.append(f"**定义**: {definition}")
                lines.append(f"**描述**: {description}")

                # 添加典型引用
                quotes = theme.get('quotes', [])[:3]
                if quotes:
                    lines.append("**典型引用**:")
                    for q in quotes:
                        text = q.get('text_content', '')[:150]
                        source = q.get('document_filename', '')
                        lines.append(f"- {text}... [{source}]")
            else:
                lines.append(f"### Theme {i}: {name}")
                lines.append(f"**Definition**: {definition}")
                lines.append(f"**Description**: {description}")

                quotes = theme.get('quotes', [])[:3]
                if quotes:
                    lines.append("**Representative Quotes**:")
                    for q in quotes:
                        text = q.get('text_content', '')[:150]
                        source = q.get('document_filename', '')
                        lines.append(f"- {text}... [{source}]")

            lines.append("---")

        return "\n".join(lines)

    def count_words(self, text: str, language: str = 'zh') -> int:
        """统计字数"""
        if not text:
            return 0

        # 移除 markdown 标记
        text = re.sub(r'\*\*', '', text)
        text = re.sub(r'\[.*?\]', '', text)

        if language == 'zh':
            # 中文按字符数统计
            return len(text.strip())
        else:
            # 英文按单词数统计
            words = text.split()
            return len(words)

    # ==================== 高级分析方法 ====================

    def literature_dialogue(self, findings: List, research_question: str, language: str = 'zh') -> str:
        """文献对话：将发现与现有文献对比

        Args:
            findings: 研究发现列表
            research_question: 研究问题
            language: 语言

        Returns:
            文献对话文本
        """
        findings_text = "\n".join([f"- {f}" for f in findings])

        if language == 'zh':
            prompt = f"""你是学术写作专家。请将以下研究发现与现有文献进行对话。

研究问题：{research_question}

研究发现：
{findings_text}

请撰写文献对话部分（600-800字），包括：

1. **与现有文献的关系**：
   - 哪些发现支持了现有文献？
   - 哪些发现扩展了现有文献？
   - 哪些发现挑战了现有文献？

2. **相关研究引用**：
   - 建议可以引用的相关研究方向
   - （注意：请使用通用的文献引用格式，如[作者, 年份]，而非真实文献）

3. **本研究的独特贡献**：
   - 本研究在文献中的定位
   - 本研究填补了哪些空白

请使用学术但清晰的语言，直接输出文献对话内容。"""
        else:
            prompt = f"""You are an academic writing expert. Please dialogue the following findings with existing literature.

Research Question: {research_question}

Findings:
{findings_text}

Please write a literature dialogue section (500-700 words), including:

1. **Relationship with existing literature**:
   - Which findings support existing literature?
   - Which findings extend existing literature?
   - Which findings challenge existing literature?

2. **Related research citations**:
   - Suggest relevant research directions
   - (Use generic citation format like [Author, Year])

3. **Unique contributions**:
   - Positioning of this study in the literature
   - Gaps this study fills

Please use academic but clear language. Output the literature dialogue directly."""

        system_prompt = self.system_prompt_zh if language == 'zh' else self.system_prompt_en

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=2500
            )
            return response.content.strip()
        except Exception as e:
            if language == 'zh':
                return f"[文献对话生成失败: {str(e)}]"
            return f"[Literature dialogue generation failed: {str(e)}]"

    def theoretical_alignment(self, themes: List[Dict], research_question: str, language: str = 'zh') -> str:
        """理论框架对接

        Args:
            themes: 主题列表
            research_question: 研究问题
            language: 语言

        Returns:
            理论框架文本
        """
        themes_summary = self._get_themes_summary(themes, language)

        if language == 'zh':
            prompt = f"""你是理论构建专家。请将以下发现对接到合适的理论框架。

研究问题：{research_question}

主题发现：
{themes_summary}

请撰写理论框架部分（600-800字），包括：

1. **适用的理论**：
   - 哪些现有理论可以解释这些发现？
   - （请使用通用的理论名称，如"社会认同理论"、"认知失调理论"等）

2. **理论-发现对接**：
   - 主题如何与理论概念对应？
   - 发现如何支持或丰富理论？

3. **理论贡献**：
   - 这些发现对现有理论有何贡献？
   - 是否需要提出新的理论视角？

请使用学术但清晰的语言，直接输出理论框架内容。"""
        else:
            prompt = f"""You are a theory construction expert. Please align the following findings with appropriate theoretical frameworks.

Research Question: {research_question}

Theme Findings:
{themes_summary}

Please write a theoretical framework section (500-700 words), including:

1. **Applicable theories**:
   - Which existing theories can explain these findings?
   - (Use generic theory names like "Social Identity Theory", "Cognitive Dissonance Theory", etc.)

2. **Theory-finding alignment**:
   - How do themes correspond to theoretical concepts?
   - How do findings support or enrich the theory?

3. **Theoretical contributions**:
   - What contributions do these findings make to existing theory?
   - Is a new theoretical perspective needed?

Please use academic but clear language. Output the theoretical framework directly."""

        system_prompt = self.system_prompt_zh if language == 'zh' else self.system_prompt_en

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=2500
            )
            return response.content.strip()
        except Exception as e:
            if language == 'zh':
                return f"[理论框架生成失败: {str(e)}]"
            return f"[Theoretical framework generation failed: {str(e)}]"

    def extract_novelty(self, findings: List, literature: str, language: str = 'zh') -> str:
        """提取创新点

        Args:
            findings: 研究发现列表
            literature: 文献背景
            language: 语言

        Returns:
            创新点分析文本
        """
        findings_text = "\n".join([f"- {f}" for f in findings])

        if language == 'zh':
            prompt = f"""你是学术评估专家。请识别以下研究的创新点。

研究发现：
{findings_text}

文献背景：
{literature[:1000] if literature else '未提供'}

请撰写创新点部分（400-600字），包括：

1. **方法创新**：
   - 研究方法有何独特之处？
   - 数据收集或分析有何创新？

2. **理论创新**：
   - 提出了哪些新概念或新视角？
   - 对现有理论有何补充或修正？

3. **实践创新**：
   - 对实践领域有何新的启示？
   - 有何新的应用价值？

4. **整体贡献**：
   - 研究的核心创新是什么？
   - 对领域有何推动作用？

请使用简洁、有力的语言，直接输出创新点内容。"""
        else:
            prompt = f"""You are an academic evaluation expert. Please identify the novelty of the following research.

Findings:
{findings_text}

Literature Background:
{literature[:1000] if literature else 'Not provided'}

Please write a novelty section (300-500 words), including:

1. **Methodological innovation**:
   - What is unique about the research method?
   - What innovations in data collection or analysis?

2. **Theoretical innovation**:
   - What new concepts or perspectives are proposed?
   - What supplements or revisions to existing theory?

3. **Practical innovation**:
   - What new insights for practice?
   - What new application value?

4. **Overall contribution**:
   - What is the core innovation?
   - How does it advance the field?

Please use concise, powerful language. Output the novelty content directly."""

        system_prompt = self.system_prompt_zh if language == 'zh' else self.system_prompt_en

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=2000
            )
            return response.content.strip()
        except Exception as e:
            if language == 'zh':
                return f"[创新点提取失败: {str(e)}]"
            return f"[Novelty extraction failed: {str(e)}]"

    def analyze_limitations(self, study_design: Dict, findings: List, language: str = 'zh') -> str:
        """分析局限性

        Args:
            study_design: 研究设计信息
            findings: 研究发现列表
            language: 语言

        Returns:
            局限性分析文本
        """
        findings_text = "\n".join([f"- {f}" for f in findings])

        if language == 'zh':
            prompt = f"""你是研究方法学专家。请诚实而专业地分析以下研究的局限性。

研究设计：
- 样本：{study_design.get('doc_count', 'N/A')} 个文档
- 方法：{study_design.get('methodology', 'N/A')}
- 数据来源：{study_design.get('data_source', 'N/A')}

研究发现：
{findings_text}

请撰写局限性部分（400-600字），包括：

1. **样本局限性**：
   - 样本量、代表性的限制
   - 可能存在的选择偏差

2. **方法局限性**：
   - 数据收集方法的限制
   - 分析方法的局限性

3. **结论可推广性**：
   - 结论的适用范围
   - 需要谨慎推广的情况

4. **未解决的问题**：
   - 哪些问题本研究未能回答
   - 需要进一步研究的方面

请诚实但专业，避免过度贬低研究价值。直接输出局限性内容。"""
        else:
            prompt = f"""You are a research methodology expert. Please analyze the limitations of the following study honestly and professionally.

Study Design:
- Sample: {study_design.get('doc_count', 'N/A')} documents
- Method: {study_design.get('methodology', 'N/A')}
- Data source: {study_design.get('data_source', 'N/A')}

Findings:
{findings_text}

Please write a limitations section (300-500 words), including:

1. **Sample limitations**:
   - Sample size, representativeness constraints
   - Potential selection bias

2. **Methodological limitations**:
   - Data collection method constraints
   - Analysis method limitations

3. **Generalizability**:
   - Scope of conclusions
   - Situations requiring cautious generalization

4. **Unresolved issues**:
   - Questions this study could not answer
   - Areas needing further research

Please be honest but professional, avoiding excessive devaluation of the study. Output the limitations directly."""

        system_prompt = self.system_prompt_zh if language == 'zh' else self.system_prompt_en

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=2000
            )
            return response.content.strip()
        except Exception as e:
            if language == 'zh':
                return f"[局限性分析失败: {str(e)}]"
            return f"[Limitations analysis failed: {str(e)}]"

    def assess_rigor(self, themes: List, codes: List, findings: List, language: str = 'zh') -> str:
        """评估可信性

        Args:
            themes: 主题列表
            codes: 编码列表
            findings: 研究发现列表
            language: 语言

        Returns:
            可信性评估文本
        """
        findings_text = "\n".join([f"- {f}" for f in findings])

        if language == 'zh':
            prompt = f"""你是质性研究方法学专家。请评估以下研究的可信性（Trustworthiness）。

数据概况：
- 主题数：{len(themes)}
- 编码数：{len(codes)}

研究发现：
{findings_text}

请撰写可信性评估部分（500-700字），包括：

1. **可信性（Credibility）**：
   - 结论是否有充分证据支持？
   - 是否有足够的典型引用？

2. **可转移性（Transferability）**：
   - 研究发现的描述是否充分？
   - 其他情境能否借鉴？

3. **可靠性（Dependability）**：
   - 编码是否一致？
   - 分析过程是否透明？

4. **可确认性（Confirmability）**：
   - 是否存在过度解读？
   - 研究者偏见是否得到控制？

5. **整体评估**：
   - 研究的可信性等级
   - 改进建议

请客观、专业，直接输出可信性评估内容。"""
        else:
            prompt = f"""You are a qualitative research methodology expert. Please assess the trustworthiness of the following study.

Data Overview:
- Themes: {len(themes)}
- Codes: {len(codes)}

Findings:
{findings_text}

Please write a rigor assessment section (400-600 words), including:

1. **Credibility**:
   - Are conclusions well-supported by evidence?
   - Are there sufficient representative quotes?

2. **Transferability**:
   - Are findings described sufficiently?
   - Can other contexts benefit?

3. **Dependability**:
   - Is coding consistent?
   - Is analysis process transparent?

4. **Confirmability**:
   - Is there over-interpretation?
   - Is researcher bias controlled?

5. **Overall assessment**:
   - Trustworthiness level
   - Improvement suggestions

Please be objective and professional. Output the rigor assessment directly."""

        system_prompt = self.system_prompt_zh if language == 'zh' else self.system_prompt_en

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=2500
            )
            return response.content.strip()
        except Exception as e:
            if language == 'zh':
                return f"[可信性评估失败: {str(e)}]"
            return f"[Rigor assessment failed: {str(e)}]"

    def find_counter_examples(self, findings: List, raw_text: str, language: str = 'zh') -> str:
        """寻找反例

        Args:
            findings: 研究发现列表
            raw_text: 原始文本
            language: 语言

        Returns:
            反例分析文本
        """
        findings_text = "\n".join([f"- {f}" for f in findings])
        text_excerpt = raw_text[:3000] if len(raw_text) > 3000 else raw_text

        if language == 'zh':
            prompt = f"""你是批判性思维专家。请从文本中主动寻找可能反驳主流发现的证据。

主流发现：
{findings_text}

文本（节选）：
{text_excerpt}

请撰写反例分析部分（400-600字），包括：

1. **识别反例**：
   - 哪些证据与主流发现不符？
   - 哪些案例是例外或偏离？

2. **替代解释**：
   - 是否存在对发现的其他解释？
   - 哪些解释尚未被排除？

3. **边界条件**：
   - 在什么条件下发现可能不成立？
   - 哪些变量调节了发现？

4. **反思性讨论**：
   - 这些反例如何影响结论？
   - 需要如何修正或限定结论？

请诚实面对反例，避免选择性忽视。直接输出反例分析内容。"""
        else:
            prompt = f"""You are a critical thinking expert. Please actively seek evidence from the text that may contradict mainstream findings.

Mainstream Findings:
{findings_text}

Text (excerpt):
{text_excerpt}

Please write a counter-example analysis section (300-500 words), including:

1. **Identify counter-examples**:
   - What evidence contradicts mainstream findings?
   - Which cases are exceptions or deviations?

2. **Alternative explanations**:
   - Are there other interpretations of the findings?
   - Which explanations haven't been ruled out?

3. **Boundary conditions**:
   - Under what conditions might findings not hold?
   - What variables moderate the findings?

4. **Reflective discussion**:
   - How do these counter-examples affect conclusions?
   - How should conclusions be modified or qualified?

Please face counter-examples honestly, avoiding selective ignorance. Output the counter-example analysis directly."""

        system_prompt = self.system_prompt_zh if language == 'zh' else self.system_prompt_en

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=2000
            )
            return response.content.strip()
        except Exception as e:
            if language == 'zh':
                return f"[反例分析失败: {str(e)}]"
            return f"[Counter-example analysis failed: {str(e)}]"


def get_ai_report_assistant(provider_name: str = None, api_key: str = None, model: str = None, base_url: str = None):
    """
    获取AI报告生成助手实例

    Args:
        provider_name: 提供商名称 ("lm_studio", "openai", "deepseek")，None时从session state获取
        api_key: API密钥（LM Studio不需要）
        model: 模型名称
        base_url: API地址（LM Studio/Deepseek需要）

    Returns:
        AIReportAssistant实例
    """
    import streamlit as st
    from src.llm.base import LLMConfig
    from src.llm.openai import OpenAIProvider
    from src.llm.lm_studio import LMStudioProvider
    from src.llm.deepseek import DeepseekProvider

    # 使用session state中的配置
    if provider_name is None:
        provider_name = st.session_state.get('llm_provider', 'lm_studio')
        model = st.session_state.get('llm_model')
        api_key = st.session_state.get('llm_api_key')
        base_url = st.session_state.get('llm_base_url')

    # 创建LLM配置
    if provider_name == "lm_studio":
        llm_config = LLMConfig(
            provider="lm_studio",
            model=model or "local-model",
            api_key="not-needed",
            base_url=base_url or "http://localhost:1234/v1",
            temperature=0.4,
            max_tokens=3000
        )
        provider = LMStudioProvider(llm_config)
    elif provider_name == "deepseek":
        llm_config = LLMConfig(
            provider="deepseek",
            model=model or "deepseek-chat",
            api_key=api_key,
            base_url=base_url or "https://api.deepseek.com/v1",
            temperature=0.4,
            max_tokens=3000
        )
        provider = DeepseekProvider(llm_config)
    elif provider_name == "openai":
        llm_config = LLMConfig(
            provider="openai",
            model=model or "gpt-4o-mini",
            api_key=api_key,
            temperature=0.4,
            max_tokens=3000
        )
        provider = OpenAIProvider(llm_config)
    else:
        raise ValueError(f"不支持的提供商: {provider_name}")

    return AIReportAssistant(provider)
