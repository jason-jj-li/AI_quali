"""
主题关系分析AI助手
提供主题间关系分析、冲突分析、层次结构分析等功能
"""
from typing import Dict, List
from .base import LLMProvider, LLMConfig
import re
import json


class ThemeAnalyzer:
    """主题关系分析助手

    提供以下功能：
    - 主题关联分析
    - 主题冲突分析
    - 主题层次结构分析
    - 主题网络可视化
    """

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def analyze_theme_relationships(
        self,
        themes: List,
        codes: List,
        analysis_type: str = "主题关联分析",
        research_question: str = ""
    ) -> Dict:
        """分析主题间关系

        Args:
            themes: 主题列表
            codes: 编码列表
            analysis_type: 分析类型（主题关联分析/主题冲突分析/主题层次结构）
            research_question: 研究问题

        Returns:
            包含关系分析结果的字典
        """
        # 准备主题摘要
        theme_summary = "\n".join([
            f"- {t.get('name', '')}: {t.get('description', '')[:100]}..."
            for t in themes
        ])

        # 准备编码列表
        code_list = [c.get('name', '') for c in codes]

        # 根据分析类型调整提示词
        if "冲突" in analysis_type:
            focus = """
请特别关注：
1. 主题之间的矛盾或对立
2. 不同视角或观点的冲突
3. 价值观或信念的冲突
4. 行为或态度的矛盾

关系类型包括：
- contrast: 对立/矛盾关系
- tension: 紧张关系
- paradox: 悖论关系
"""
        elif "层次" in analysis_type:
            focus = """
请特别关注：
1. 主题之间的层次关系（上位-下位）
2. 主题的包含关系
3. 抽象程度差异
4. 因果或逻辑关系

关系类型包括：
- hierarchy: 层次关系
- cause: 因果关系
- part_whole: 部分-整体关系
"""
        else:  # 关联分析
            focus = """
请特别关注：
1. 主题之间的支持或强化关系
2. 主题的共同出现
3. 主题的互补性
4. 主题的因果联系

关系类型包括：
- support: 支持/强化关系
- complement: 互补关系
- correlation: 相关关系
- cause: 因果关系
"""

        prompt = f"""你是质性研究方法学专家。请分析主题间的关系。

研究问题：{research_question}
分析类型：{analysis_type}

主题列表：
{theme_summary}

相关编码：{', '.join(code_list)}

{focus}

请识别主题间的关系，并为每种关系提供：
1. 涉及的主题
2. 关系类型
3. 关系的解释（为什么存在这种关系？）
4. 支持这种关系的证据（来自编码或文本）

返回JSON格式：
{{
    "network": [
        {{
            "theme1": "主题A",
            "theme2": "主题B",
            "type": "support|contrast|hierarchy|complement|correlation|cause",
            "strength": 0.8,  // 0-1的关系强度
            "explanation": "关系的详细解释",
            "evidence": ["证据1", "证据2"]
        }}
    ],
    "matrix": {{
        "主题A": {{"主题B": 0.8, "主题C": 0.3}},
        "主题B": {{"主题A": 0.8, "主题C": 0.5}}
    }},
    "insights": [
        "洞察1：关于主题网络的重要发现",
        "洞察2：关于核心主题的观察"
    ],
    "central_themes": ["最核心的主题1", "最核心的主题2"],
    "peripheral_themes": ["边缘主题1", "边缘主题2"]
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.4,
            max_tokens=3000
        )

        default_result = {
            "network": [],
            "matrix": {},
            "insights": ["无法完成详细的关系分析"],
            "central_themes": [],
            "peripheral_themes": []
        }

        return self._parse_json_response(response.content, default_result)

    def identify_theme_patterns(
        self,
        themes: List,
        codes: List,
        text: str
    ) -> Dict:
        """识别主题模式

        识别主题在文本中的出现模式、分布规律等。

        Args:
            themes: 主题列表
            codes: 编码列表
            text: 原始文本

        Returns:
            包含模式识别结果的字典
        """
        theme_names = [t.get('name', '') for t in themes]

        prompt = f"""你是质性研究方法学专家。请识别主题在文本中的模式。

主题：{', '.join(theme_names)}

文本摘要：{text[:2000]}

请分析：

1. **共现模式**：哪些主题经常一起出现？

2. **序列模式**：主题是否以特定的顺序出现？

3. **条件模式**：某些主题是否在特定条件下出现？

4. **互斥模式**：哪些主题很少一起出现？

5. **核心-边缘结构**：哪些是核心主题，哪些是边缘主题？

返回JSON格式：
{{
    "co_occurrence_patterns": [
        {{
            "themes": ["主题A", "主题B"],
            "pattern": "共现模式描述",
            "interpretation": "解释"
        }}
    ],
    "sequence_patterns": [
        {{
            "sequence": ["主题A", "主题B", "主题C"],
            "description": "序列描述"
        }}
    ],
    "conditional_patterns": [
        {{
            "condition": "条件描述",
            "themes": ["主题A", "主题B"],
            "explanation": "解释"
        }}
    ],
    "mutual_exclusions": [
        {{
            "themes": ["主题A", "主题B"],
            "reason": "互斥原因"
        }}
    ],
    "core_peripheral_structure": {{
        "core": ["核心主题1", "核心主题2"],
        "peripheral": ["边缘主题1", "边缘主题2"],
        "bridge": ["桥梁主题1"]  // 连接核心和边缘的主题
    }}
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.4,
            max_tokens=2500
        )

        default_result = {
            "co_occurrence_patterns": [],
            "sequence_patterns": [],
            "conditional_patterns": [],
            "mutual_exclusions": [],
            "core_peripheral_structure": {
                "core": [],
                "peripheral": [],
                "bridge": []
            }
        }

        return self._parse_json_response(response.content, default_result)

    def generate_theme_narrative(
        self,
        themes: List,
        relationships: Dict,
        research_question: str = ""
    ) -> str:
        """生成主题叙事

        将主题及其关系整合成连贯的学术叙述。

        Args:
            themes: 主题列表
            relationships: 关系分析结果
            research_question: 研究问题

        Returns:
            主题叙事文本
        """
        # 准备主题摘要
        theme_summary = "\n".join([
            f"- {t.get('name', '')}: {t.get('description', '')[:100]}..."
            for t in themes
        ])

        prompt = f"""你是学术写作专家。请将以下主题和分析结果整合成连贯的学术叙述。

研究问题：{research_question}

主题：
{theme_summary}

主题关系：
{json.dumps(relationships.get('network', []), ensure_ascii=False, indent=2)}

请生成一段连贯的学术叙述，包括：

1. **主题概览**：简要介绍识别出的主要主题

2. **主题关系**：描述主题之间的关键关系（支持、对立、层次等）

3. **理论意义**：这些主题和关系对理解研究问题有何意义？

4. **整体图景**：这些主题如何共同构成一个整体的理解？

请使用学术但清晰的语言，避免过度技术化。长度约500-800字。

直接返回叙述文本，不需要JSON格式。"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.5,
            max_tokens=2000
        )

        return response.content

    def compare_themes_across_groups(
        self,
        themes_group1: List,
        themes_group2: List,
        group1_name: str = "组1",
        group2_name: str = "组2"
    ) -> Dict:
        """跨组主题比较

        比较不同组的主题差异。

        Args:
            themes_group1: 组1的主题列表
            themes_group2: 组2的主题列表
            group1_name: 组1名称
            group2_name: 组2名称

        Returns:
            包含比较结果的字典
        """
        group1_themes = [t.get('name', '') for t in themes_group1]
        group2_themes = [t.get('name', '') for t in themes_group2]

        prompt = f"""你是质性研究方法学专家。请比较两组的主题差异。

{group1_name}的主题：{', '.join(group1_themes)}
{group2_name}的主题：{', '.join(group2_themes)}

请分析：

1. **共同主题**：两组共有的主题

2. **独特主题**：每组独有的主题

3. **主题差异**：主题在两组间有何不同？

4. **可能的解释**：如何解释这些差异？

返回JSON格式：
{{
    "common_themes": ["共同主题1", "共同主题2"],
    "unique_to_group1": ["{group1_name}独有主题"],
    "unique_to_group2": ["{group2_name}独有主题"],
    "differences": [
        {{
            "theme": "主题名称",
            "difference": "差异描述",
            "possible_explanation": "可能的解释"
        }}
    ],
    "overall_comparison": "整体比较结论"
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.4,
            max_tokens=2000
        )

        default_result = {
            "common_themes": [],
            "unique_to_group1": [],
            "unique_to_group2": [],
            "differences": [],
            "overall_comparison": "无法完成详细比较"
        }

        return self._parse_json_response(response.content, default_result)

    def _parse_json_response(self, content: str, default: Dict) -> Dict:
        """解析JSON响应

        Args:
            content: LLM响应内容
            default: 解析失败时返回的默认值

        Returns:
            解析后的字典或默认值
        """
        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return default


def get_ai_theme_analyzer(
    provider_name: str = None,
    api_key: str = None,
    model: str = None,
    base_url: str = None
) -> ThemeAnalyzer:
    """获取主题分析助手实例

    Args:
        provider_name: 提供商名称 ("lm_studio", "openai", "deepseek")，None时从session state获取
        api_key: API密钥（LM Studio不需要）
        model: 模型名称
        base_url: API地址（LM Studio/Deepseek需要）

    Returns:
        ThemeAnalyzer实例
    """
    import streamlit as st
    from .base import LLMConfig
    from .openai import OpenAIProvider
    from .lm_studio import LMStudioProvider
    from .deepseek import DeepseekProvider

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

    return ThemeAnalyzer(provider)
