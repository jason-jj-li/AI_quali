"""
AI主题分析助手模块
实现AI辅助主题识别功能
"""
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from src.llm.base import LLMConfig, LLMProvider, LLMResponse


@dataclass
class ThemeSuggestionResult:
    """主题建议结果数据类"""
    name: str
    description: str
    definition: str
    suggested_codes: List[Dict[str, Any]]
    representative_quotes: List[Dict[str, Any]]
    confidence: float


@dataclass
class QuoteSelectionResult:
    """引用选择结果数据类"""
    quotes: List[Dict[str, Any]]
    summary: str


class AIThemeAssistant:
    """
    AI主题分析助手

    支持功能：
    1. 批量主题识别（基于项目所有编码）
    2. 主题定义生成
    3. 典型引用选择
    4. 主题关系分析
    """

    def __init__(self, provider: LLMProvider):
        """
        初始化AI主题分析助手

        Args:
            provider: LLM提供商实例
        """
        self.provider = provider
        self._load_prompts()

    def _load_prompts(self):
        """加载提示词模板"""
        import os
        from config import PROMPTS_DIR

        # 加载主题分析提示词
        theme_prompts_path = PROMPTS_DIR / "theme.txt"
        if theme_prompts_path.exists():
            with open(theme_prompts_path, 'r', encoding='utf-8') as f:
                theme_content = f.read()
                # 执行提示词文件以获取模板
                exec_globals = {}
                exec(theme_content, exec_globals)
                self.system_prompt = exec_globals.get('SYSTEM_PROMPT', '')
                self.identification_prompt = exec_globals.get('BATCH_THEME_IDENTIFICATION_PROMPT',
                                                              exec_globals.get('THEME_IDENTIFICATION_PROMPT', ''))
                self.quote_selection_prompt = exec_globals.get('QUOTE_SELECTION_PROMPT', '')
                self.definition_prompt = exec_globals.get('THEME_DEFINITION_PROMPT', '')
                self.relationship_prompt = exec_globals.get('THEME_RELATIONSHIP_PROMPT', '')
        else:
            # 使用默认提示词
            self.system_prompt = "你是一位资深的质性研究专家，擅长主题分析。"
            self.identification_prompt = "请分析以下编码并识别主题：{codes_data}"
            self.quote_selection_prompt = "请为主题选择典型引用：{coding_instances}"

    def identify_themes(
        self,
        codes: List[Dict[str, Any]],
        coding_instances: List[Dict[str, Any]],
        research_question: str = "",
        methodology: str = "",
        max_themes: int = 10
    ) -> List[ThemeSuggestionResult]:
        """
        基于编码识别主题

        Args:
            codes: 编码列表
            coding_instances: 编码实例列表（包含文本片段）
            research_question: 研究问题
            methodology: 研究方法
            max_themes: 最大主题数

        Returns:
            主题建议列表
        """
        # 准备编码数据
        codes_data = self._prepare_codes_data(codes, coding_instances)

        # 构建提示词
        prompt = self.identification_prompt.format(
            research_question=research_question,
            methodology=methodology,
            max_themes=max_themes,
            codes_data=codes_data
        )

        try:
            # 调用LLM
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.4,  # 中等温度以平衡创造性和一致性
                max_tokens=3000
            )

            # 解析响应
            suggestions = self._parse_theme_response(response.content)

            # 限制主题数量
            return suggestions[:max_themes]

        except Exception as e:
            # 返回错误信息
            return [ThemeSuggestionResult(
                name="错误",
                description=f"主题识别失败: {str(e)}",
                definition="",
                suggested_codes=[],
                representative_quotes=[],
                confidence=0.0
            )]

    def generate_theme_definition(
        self,
        theme_name: str,
        related_codes: List[Dict[str, Any]],
        excerpts: List[str],
        research_question: str = ""
    ) -> Dict[str, str]:
        """
        生成主题的学术性定义

        Args:
            theme_name: 主题名称
            related_codes: 相关编码列表
            excerpts: 文本片段列表
            research_question: 研究问题

        Returns:
            包含定义、描述等信息的字典
        """
        # 准备数据
        codes_str = self._format_codes_for_definition(related_codes)
        excerpts_str = "\n\n".join([f"- {exc[:200]}..." if len(exc) > 200 else f"- {exc}"
                                     for exc in excerpts[:5]])  # 限制片段数量

        # 构建提示词
        prompt = self.definition_prompt.format(
            theme_name=theme_name,
            related_codes=codes_str,
            excerpts=excerpts_str,
            research_question=research_question
        )

        try:
            # 调用LLM
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=1500
            )

            # 解析响应
            return self._parse_definition_response(response.content, theme_name)

        except Exception as e:
            return {
                "theme_name": theme_name,
                "definition": f"定义生成失败: {str(e)}",
                "description": "",
                "inclusion_criteria": "",
                "exclusion_criteria": "",
                "theoretical_interpretation": ""
            }

    def select_quotes(
        self,
        theme_name: str,
        theme_definition: str,
        coding_instances: List[Dict[str, Any]],
        max_quotes: int = 5
    ) -> QuoteSelectionResult:
        """
        为主题选择典型引用

        Args:
            theme_name: 主题名称
            theme_definition: 主题定义
            coding_instances: 编码实例列表
            max_quotes: 最大引用数量

        Returns:
            引用选择结果
        """
        # 准备编码实例数据
        instances_str = self._format_coding_instances_for_quotes(coding_instances)

        # 构建提示词
        prompt = self.quote_selection_prompt.format(
            theme_name=theme_name,
            definition=theme_definition,
            coding_instances=instances_str
        )

        try:
            # 调用LLM
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=2000
            )

            # 解析响应
            result = self._parse_quote_response(response.content)

            # 限制引用数量
            if result and result.quotes:
                result.quotes = result.quotes[:max_quotes]

            return result or QuoteSelectionResult(quotes=[], summary="")

        except Exception as e:
            return QuoteSelectionResult(
                quotes=[],
                summary=f"引用选择失败: {str(e)}"
            )

    def analyze_theme_relationships(
        self,
        themes: List[Dict[str, Any]],
        co_occurrence_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分析主题之间的关系

        Args:
            themes: 主题列表
            co_occurrence_data: 共现数据

        Returns:
            关系分析结果
        """
        # 准备数据
        themes_str = self._format_themes_for_relationship(themes)
        co_occurrence_str = json.dumps(co_occurrence_data, ensure_ascii=False, indent=2)

        # 构建提示词
        prompt = self.relationship_prompt.format(
            themes=themes_str,
            co_occurrence_data=co_occurrence_str
        )

        try:
            # 调用LLM
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=2000
            )

            # 解析响应
            return self._parse_relationship_response(response.content)

        except Exception as e:
            return {
                "theme_relationships": [],
                "relationship_matrix": {},
                "analysis": f"关系分析失败: {str(e)}",
                "visualization_suggestions": []
            }

    def _prepare_codes_data(self, codes: List[Dict], coding_instances: List[Dict]) -> str:
        """准备编码数据用于主题识别"""
        lines = []

        # 添加编码列表
        lines.append("## 编码列表")
        for code in codes:
            desc = code.get('description', '')
            usage = code.get('usage_count', 0)
            lines.append(f"- [{code['name']}] {desc} (使用{usage}次)")

        lines.append("")

        # 添加编码实例
        lines.append("## 编码实例（文本片段）")
        for i, instance in enumerate(coding_instances[:50], 1):  # 限制实例数量
            text = instance.get('text_content', '')
            code_name = instance.get('code_name', '未知编码')
            # 截断过长的文本
            if len(text) > 300:
                text = text[:300] + "..."
            lines.append(f"{i}. [{code_name}] {text}")

        return "\n".join(lines)

    def _format_codes_for_definition(self, codes: List[Dict]) -> str:
        """格式化编码列表用于定义生成"""
        lines = []
        for code in codes:
            name = code.get('name', '')
            desc = code.get('description', '')
            if desc:
                lines.append(f"- {name}: {desc}")
            else:
                lines.append(f"- {name}")
        return "\n".join(lines)

    def _format_coding_instances_for_quotes(self, instances: List[Dict]) -> str:
        """格式化编码实例用于引用选择"""
        lines = []
        for i, instance in enumerate(instances[:30], 1):  # 限制实例数量
            text = instance.get('text_content', '')
            doc_name = instance.get('document_filename', f'文档{i}')
            lines.append(f"{i}. [{doc_name}] {text}")
        return "\n".join(lines)

    def _format_themes_for_relationship(self, themes: List[Dict]) -> str:
        """格式化主题列表用于关系分析"""
        lines = []
        for theme in themes:
            name = theme.get('name', '')
            desc = theme.get('description', '')
            codes = theme.get('codes', [])
            code_names = [c.get('name', '') for c in codes]
            lines.append(f"- {name}: {desc}")
            lines.append(f"  包含编码: {', '.join(code_names)}")
        return "\n".join(lines)

    def _parse_theme_response(self, response: str) -> List[ThemeSuggestionResult]:
        """解析主题识别响应"""
        suggestions = []

        try:
            # 尝试解析JSON响应
            data = json.loads(response)

            if "themes" in data:
                for item in data["themes"]:
                    suggested_codes = []
                    for code_item in item.get("suggested_codes", []):
                        suggested_codes.append({
                            "code_id": code_item.get("code_id", ""),
                            "code_name": code_item.get("code_name", ""),
                            "relevance_score": code_item.get("relevance_score", 0.8),
                            "reason": code_item.get("reason", "")
                        })

                    suggestions.append(ThemeSuggestionResult(
                        name=item.get("name", ""),
                        description=item.get("description", ""),
                        definition=item.get("definition", ""),
                        suggested_codes=suggested_codes,
                        representative_quotes=item.get("representative_quotes", []),
                        confidence=item.get("confidence", 0.8)
                    ))

        except json.JSONDecodeError:
            # 如果不是JSON格式，尝试其他解析方式
            pass

        return suggestions

    def _parse_definition_response(self, response: str, theme_name: str) -> Dict[str, str]:
        """解析定义生成响应"""
        # 简单解析：将响应作为定义
        # 实际应用中可能需要更复杂的解析
        lines = response.split('\n')

        result = {
            "theme_name": theme_name,
            "definition": "",
            "description": "",
            "inclusion_criteria": "",
            "exclusion_criteria": "",
            "theoretical_interpretation": ""
        }

        # 简单的段落提取逻辑
        current_section = "definition"
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if "详细描述" in line or "description" in line.lower():
                current_section = "description"
            elif "包含标准" in line or "inclusion" in line.lower():
                current_section = "inclusion_criteria"
            elif "排除标准" in line or "exclusion" in line.lower():
                current_section = "exclusion_criteria"
            elif "理论阐释" in line or "theoretical" in line.lower():
                current_section = "theoretical_interpretation"
            else:
                if result[current_section]:
                    result[current_section] += " " + line
                else:
                    result[current_section] = line

        # 如果没有找到定义，使用整个响应
        if not result["definition"]:
            result["definition"] = response[:500]

        return result

    def _parse_quote_response(self, response: str) -> Optional[QuoteSelectionResult]:
        """解析引用选择响应"""
        try:
            data = json.loads(response)

            quotes = []
            for item in data.get("quotes", []):
                quotes.append({
                    "text": item.get("text", ""),
                    "coding_id": item.get("coding_id", ""),
                    "document_id": item.get("document_id", ""),
                    "quote_type": item.get("quote_type", "supporting"),
                    "reason": item.get("reason", ""),
                    "relevance_score": item.get("relevance_score", 0.8)
                })

            return QuoteSelectionResult(
                quotes=quotes,
                summary=data.get("summary", "")
            )

        except json.JSONDecodeError:
            return None

    def _parse_relationship_response(self, response: str) -> Dict[str, Any]:
        """解析主题关系响应"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "theme_relationships": [],
                "relationship_matrix": {},
                "analysis": response[:500],  # 使用响应的前500字符作为分析
                "visualization_suggestions": []
            }


    # Convenience wrapper methods for backward compatibility with new app.py
    def identify_themes_from_codes(self, codes: list, research_question: str = "", max_themes: int = 8, approach: str = "主题分析法") -> list:
        """从编码识别主题的包装方法"""
        from dataclasses import dataclass
        from typing import List

        @dataclass
        class ThemeResult:
            name: str
            description: str
            definition: str
            related_codes: List[str]
            quotes: List[str]
            confidence: float

        # 准备编码数据（将Session State的编码格式转换为现有格式）
        codebook_data = []
        for c in codes:
            codebook_data.append({
                "name": c.get("name", ""),
                "description": c.get("description", ""),
                "usage_count": len(c.get("quotes", []))
            })

        # 使用现有的identify_themes方法
        suggestions = self.identify_themes(
            codes=codebook_data,
            coding_instances=[],
            research_question=research_question,
            methodology=approach,
            max_themes=max_themes
        )

        # 转换为app.py期望的格式
        results = []
        for s in suggestions:
            related_code_names = [sc.get("code_name", "") for sc in s.suggested_codes]
            results.append(ThemeResult(
                name=s.name,
                description=s.description,
                definition=s.definition,
                related_codes=related_code_names,
                quotes=[rq.get("text", "")[:100] for rq in s.representative_quotes[:2]],
                confidence=s.confidence
            ))

        return results


def get_ai_theme_assistant(provider_name: str = None, api_key: str = None, model: str = None, base_url: str = None):
    """
    获取AI主题分析助手实例

    Args:
        provider_name: 提供商名称 ("lm_studio", "openai", "deepseek")，None时从session state获取
        api_key: API密钥（LM Studio不需要）
        model: 模型名称
        base_url: API地址（LM Studio/Deepseek需要）

    Returns:
        AIThemeAssistant实例
    """
    import streamlit as st
    from src.llm.base import LLMConfig
    from src.llm.openai import OpenAIProvider
    from src.llm.lm_studio import LMStudioProvider
    from src.llm.deepseek import DeepseekProvider

    # 使用session state中的配置（如果参数未提供）
    if provider_name is None:
        provider_name = st.session_state.get('llm_provider', 'lm_studio')
    if api_key is None:
        api_key = st.session_state.get('llm_api_key')
    if model is None:
        model = st.session_state.get('llm_model')
    if base_url is None:
        base_url = st.session_state.get('llm_base_url')

    # 创建LLM配置
    if provider_name == "lm_studio":
        llm_config = LLMConfig(
            provider="lm_studio",
            model=model or "qwen/qwen3-next-80b",
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

    return AIThemeAssistant(provider)
