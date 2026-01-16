# -*- coding: utf-8 -*-
"""
QualInsight Report Service
报告生成业务逻辑层
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class ReportSection:
    """报告章节"""
    title: str
    content: str
    order: int = 0


@dataclass
class Report:
    """报告数据类"""
    id: str
    title: str
    sections: List[ReportSection]
    language: str = "zh"
    created_at: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "sections": [asdict(s) for s in self.sections],
            "language": self.language,
            "created_at": self.created_at,
            "metadata": self.metadata
        }


class ReportService:
    """
    报告服务

    职责：
    - 报告生成
    - 报告导出
    - 报告模板管理
    """

    def __init__(self):
        self._reports: List[Report] = []

    def create_report(
        self,
        title: str,
        sections: List[ReportSection],
        language: str = "zh",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Report:
        """
        创建报告

        Args:
            title: 报告标题
            sections: 报告章节
            language: 语言
            metadata: 元数据

        Returns:
            创建的报告
        """
        import uuid

        report = Report(
            id=str(uuid.uuid4()),
            title=title,
            sections=sections,
            language=language,
            metadata=metadata or {}
        )

        self._reports.append(report)
        return report

    def get_report(self, report_id: str) -> Optional[Report]:
        """获取报告"""
        for report in self._reports:
            if report.id == report_id:
                return report
        return None

    def export_report(self, report: Report, format: str = "md") -> str:
        """
        导出报告

        Args:
            report: 报告对象
            format: 格式 (md, json)

        Returns:
            导出内容
        """
        if format == "md":
            return self._export_markdown(report)
        elif format == "json":
            return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

        raise ValueError(f"Unsupported format: {format}")

    def _export_markdown(self, report: Report) -> str:
        """导出为 Markdown"""
        lines = [
            f"# {report.title}",
            f"\nGenerated on: {report.created_at}",
            "\n---\n"
        ]

        # 按顺序排序章节
        sorted_sections = sorted(report.sections, key=lambda s: s.order)

        for section in sorted_sections:
            lines.append(f"## {section.title}")
            lines.append(section.content)
            lines.append("\n")

        return "\n".join(lines)

    def generate_imrad_report(
        self,
        research_question: str,
        codes: List[Dict[str, Any]],
        themes: List[Dict[str, Any]],
        language: str = "zh"
    ) -> Report:
        """
        生成 IMRAD 结构报告

        Args:
            research_question: 研究问题
            codes: 编码列表
            themes: 主题列表
            language: 语言

        Returns:
            生成的报告
        """
        sections = [
            ReportSection(
                title="Introduction",
                content=self._generate_introduction(research_question, language),
                order=1
            ),
            ReportSection(
                title="Methods",
                content=self._generate_methods(language),
                order=2
            ),
            ReportSection(
                title="Results",
                content=self._generate_results(codes, themes, language),
                order=3
            ),
            ReportSection(
                title="Discussion",
                content=self._generate_discussion(codes, themes, language),
                order=4
            )
        ]

        return self.create_report(
            title=f"Qualitative Research Report - {datetime.now().strftime('%Y-%m-%d')}",
            sections=sections,
            language=language
        )

    def _generate_introduction(self, research_question: str, language: str) -> str:
        """生成引言"""
        if language == "zh":
            return f"""## 研究背景

本研究旨在探讨以下研究问题：

**{research_question}**

通过质性研究方法，我们收集并分析了相关数据，以期获得深入洞察。

## 研究目的

本研究的目的是通过系统性的数据分析，揭示研究现象背后的深层含义和模式。"""
        else:
            return f"""## Research Background

This study aims to explore the following research question:

**{research_question}**

Through qualitative research methods, we collected and analyzed relevant data to gain deep insights.

## Research Purpose

The purpose of this study is to reveal the deep meanings and patterns behind the research phenomenon through systematic data analysis."""

    def _generate_methods(self, language: str) -> str:
        """生成方法部分"""
        if language == "zh":
            return """## 研究方法

本研究采用质性研究方法，具体包括：

1. **数据收集**：通过访谈方式收集原始数据
2. **数据分析**：采用编码分析方法对数据进行系统性分析
3. **主题识别**：从编码中提炼出核心主题
4. **结果验证**：通过回溯原始数据验证分析结果的可靠性

## 分析工具

本研究使用 AI 辅助质性分析平台 QualInsight 进行数据分析。"""
        else:
            return """## Research Methods

This study adopts qualitative research methods, including:

1. **Data Collection**: Collecting original data through interviews
2. **Data Analysis**: Systematic analysis of data using coding analysis methods
3. **Theme Identification**: Extracting core themes from codes
4. **Result Validation**: Verifying the reliability of analysis results by returning to original data

## Analysis Tools

This study uses the AI-assisted qualitative analysis platform QualInsight for data analysis."""

    def _generate_results(
        self,
        codes: List[Dict[str, Any]],
        themes: List[Dict[str, Any]],
        language: str
    ) -> str:
        """生成结果部分"""
        # 确保 codes 和 themes 是字典列表
        valid_codes = []
        for code in codes:
            if isinstance(code, dict):
                valid_codes.append(code)
            elif isinstance(code, str):
                valid_codes.append({"name": code, "description": ""})

        valid_themes = []
        for theme in themes:
            if isinstance(theme, dict):
                valid_themes.append(theme)
            elif isinstance(theme, str):
                valid_themes.append({"name": theme, "definition": ""})

        if language == "zh":
            content = "## 编码分析结果\n\n"
            content += f"本研究共识别出 {len(valid_codes)} 个编码。主要编码包括：\n\n"
            for code in valid_codes[:10]:  # 只显示前10个
                content += f"- **{code.get('name', 'N/A')}**: {code.get('description', '')}\n"

            content += "\n## 主题分析结果\n\n"
            if valid_themes:
                content += f"基于编码分析，本研究识别出 {len(valid_themes)} 个核心主题：\n\n"
                for theme in valid_themes[:5]:  # 只显示前5个
                    content += f"- **{theme.get('name', 'N/A')}**: {theme.get('definition', '')}\n"
            else:
                content += "主题分析正在进行中。\n"

            return content
        else:
            content = "## Coding Analysis Results\n\n"
            content += f"This study identified {len(valid_codes)} codes. Major codes include:\n\n"
            for code in valid_codes[:10]:
                content += f"- **{code.get('name', 'N/A')}**: {code.get('description', '')}\n"

            content += "\n## Theme Analysis Results\n\n"
            if valid_themes:
                content += f"Based on coding analysis, this study identified {len(valid_themes)} core themes:\n\n"
                for theme in valid_themes[:5]:
                    content += f"- **{theme.get('name', 'N/A')}**: {theme.get('definition', '')}\n"
            else:
                content += "Theme analysis is in progress.\n"

            return content

    def _generate_discussion(
        self,
        codes: List[Dict[str, Any]],
        themes: List[Dict[str, Any]],
        language: str
    ) -> str:
        """生成讨论部分"""
        if language == "zh":
            return """## 研究发现

基于上述分析结果，本研究得出以下主要发现：

1. **模式识别**：通过系统编码，我们识别出数据中的关键模式
2. **主题关联**：主题之间存在明显的关联关系
3. **理论意义**：研究发现对相关理论具有启示意义

## 研究局限

本研究存在以下局限：

1. **样本范围**：样本的代表性可能有限
2. **分析偏差**：分析过程可能存在主观偏差
3. **进一步研究**：建议未来研究扩大样本范围

## 结论

本研究通过质性分析方法，对研究问题进行了深入探讨。研究结果为理解相关现象提供了新的视角和洞察。"""
        else:
            return """## Research Findings

Based on the above analysis results, this study draws the following main findings:

1. **Pattern Recognition**: Through systematic coding, we identified key patterns in the data
2. **Theme Relationships**: There are clear associations between themes
3. **Theoretical Significance**: The research findings have implications for relevant theories

## Research Limitations

This study has the following limitations:

1. **Sample Scope**: The representativeness of the sample may be limited
2. **Analysis Bias**: The analysis process may have subjective bias
3. **Further Research**: Future research is recommended to expand the sample scope

## Conclusion

Through qualitative analysis methods, this study conducted an in-depth exploration of the research question. The research results provide new perspectives and insights for understanding relevant phenomena."""
