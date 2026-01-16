"""
深度分析AI助手
提供主题交叉分析、理论饱和度评估、解释性框架构建等高级分析功能
"""
from typing import Dict, List
from .base import LLMProvider, LLMConfig
import re
import json


class DeepAnalyzer:
    """深度分析助手

    提供以下功能：
    - 主题交叉分析
    - 编码-主题映射
    - 理论饱和度评估
    - 解释性框架构建
    - 命题生成
    - 模式识别
    """

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def analyze(
        self,
        analysis_type: str,
        report: Dict,
        session_state
    ) -> Dict:
        """执行深度分析

        Args:
            analysis_type: 分析类型
            report: 已生成的报告
            session_state: Streamlit session state

        Returns:
            分析结果字典
        """
        if analysis_type == "主题交叉分析":
            return self.cross_theme_analysis(
                session_state.get('themes', []),
                session_state.get('codes', []),
                session_state.get('research_question', '')
            )
        elif analysis_type == "编码-主题映射":
            return self.code_theme_mapping(
                session_state.get('codes', []),
                session_state.get('themes', [])
            )
        elif analysis_type == "理论饱和度评估":
            return self.theoretical_saturation(
                session_state.get('themes', []),
                session_state.get('codes', []),
                session_state.get('raw_text', '')
            )
        elif analysis_type == "解释性框架构建":
            return self.interpretive_framework(
                session_state.get('themes', []),
                session_state.get('research_question', '')
            )
        else:
            return {"error": f"未知分析类型: {analysis_type}"}

    def cross_theme_analysis(
        self,
        themes: List,
        codes: List,
        research_question: str
    ) -> Dict:
        """主题交叉分析

        分析主题之间的相互作用、相互强化或制约关系。

        Args:
            themes: 主题列表
            codes: 编码列表
            research_question: 研究问题

        Returns:
            交叉分析结果
        """
        # 准备主题摘要
        theme_summary = "\n".join([
            f"- {t.get('name', '')}: {t.get('description', '')[:100]}..."
            for t in themes
        ])

        prompt = f"""你是质性研究方法学专家。请对主题进行交叉分析。

研究问题：{research_question}

主题：
{theme_summary}

请分析主题之间的相互作用：

1. **相互强化**：哪些主题相互支持、强化？

2. **相互制约**：哪些主题之间存在限制、抑制关系？

3. **共同作用**：哪些主题组合起来产生新的理解？

4. **中介效应**：哪些主题在另外两个主题之间起中介作用？

5. **调节效应**：哪些主题调节其他主题之间的关系？

返回JSON格式：
{{
    "reinforcing_pairs": [
        {{
            "theme1": "主题A",
            "theme2": "主题B",
            "mechanism": "强化机制解释",
            "quote": "支持引文"
        }}
    ],
    "constraining_pairs": [
        {{
            "theme1": "主题A",
            "theme2": "主题B",
            "mechanism": "制约机制解释"
        }}
    ],
    "synergistic_combinations": [
        {{
            "themes": ["主题A", "主题B", "主题C"],
            "emergent_understanding": "共同作用产生的新理解"
        }}
    ],
    "mediation_effects": [
        {{
            "mediator": "中介主题",
            "relationship": "主题A → 中介主题 → 主题B",
            "explanation": "中介机制"
        }}
    ],
    "findings": ["核心发现1", "核心发现2"],
    "recommendations": ["建议1", "建议2"]
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.4,
            max_tokens=3000
        )

        default_result = {
            "reinforcing_pairs": [],
            "constraining_pairs": [],
            "synergistic_combinations": [],
            "mediation_effects": [],
            "findings": ["无法完成详细交叉分析"],
            "recommendations": []
        }

        return self._parse_json_response(response.content, default_result)

    def code_theme_mapping(
        self,
        codes: List,
        themes: List
    ) -> Dict:
        """编码-主题映射分析

        分析编码与主题的映射关系，识别：
        - 哪些编码对哪些主题贡献最大
        - 哪些编码跨越多个主题
        - 编码在主题间的分布

        Args:
            codes: 编码列表
            themes: 主题列表

        Returns:
            映射分析结果
        """
        # 准备编码信息
        code_info = []
        for code in codes:
            related_themes = [
                t['name'] for t in themes
                if code.get('name') in t.get('codes', [])
            ]
            code_info.append({
                'name': code.get('name', ''),
                'description': code.get('description', ''),
                'related_themes': related_themes
            })

        prompt = f"""你是质性研究方法学专家。请分析编码与主题的映射关系。

编码信息：
{json.dumps(code_info, ensure_ascii=False, indent=2)}

主题信息：
{json.dumps([{'name': t.get('name', ''), 'description': t.get('description', '')} for t in themes], ensure_ascii=False, indent=2)}

请分析：

1. **编码分布**：编码如何在不同主题间分布？

2. **核心编码**：哪些编码对主题贡献最大？

3. **跨主题编码**：哪些编码跨越多个主题？（这些可能是"桥梁编码"）

4. **主题特异性编码**：哪些编码是某个主题独有的？

5. **编码层次**：编码间是否存在层次关系？

返回JSON格式：
{{
    "distribution_analysis": "分布分析总结",
    "core_codes": [
        {{
            "code": "编码名称",
            "contributes_to": ["主题1", "主题2"],
            "importance": "重要性说明"
        }}
    ],
    "bridge_codes": [
        {{
            "code": "编码名称",
            "connects": ["主题1", "主题2", "主题3"],
            "role": "桥梁角色说明"
        }}
    ],
    "theme_specific_codes": [
        {{
            "theme": "主题名称",
            "unique_codes": ["编码1", "编码2"]
        }}
    ],
    "coding_hierarchy": [
        {{
            "parent_code": "父编码",
            "child_codes": ["子编码1", "子编码2"],
            "rationale": "层次关系说明"
        }}
    ],
    "recommendations": ["建议1", "建议2"]
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2500
        )

        default_result = {
            "distribution_analysis": "编码分布在各主题中",
            "core_codes": [],
            "bridge_codes": [],
            "theme_specific_codes": [],
            "coding_hierarchy": [],
            "recommendations": []
        }

        return self._parse_json_response(response.content, default_result)

    def theoretical_saturation(
        self,
        themes: List,
        codes: List,
        text: str
    ) -> Dict:
        """理论饱和度评估

        评估是否达到理论饱和，即新数据不再产生新的理论见解。

        Args:
            themes: 主题列表
            codes: 编码列表
            text: 原始文本

        Returns:
            饱和度评估结果
        """
        theme_names = [t.get('name', '') for t in themes]
        code_names = [c.get('name', '') for c in codes]

        prompt = f"""你是质性研究方法学专家（扎根理论取向）。请评估理论饱和度。

当前状态：
- 主题数：{len(themes)}
- 编码数：{len(codes)}
- 文本长度：{len(text)} 字符

主题：{', '.join(theme_names)}
编码：{', '.join(code_names)}

理论饱和度的标志：
1. 新数据不再产生新的主题或编码
2. 现有主题和编码之间的关系已经充分阐明
3. 理论命题已经达到稳定
4. 边缘条件已经被识别

请评估：

1. **理论饱和度评分**（0-1）：当前达到的饱和程度

2. **饱和维度评估**：
   - 主题饱和：新主题是否还会出现？
   - 关系饱和：主题间关系是否充分阐明？
   - 命题饱和：理论命题是否稳定？
   - 边界饱和：是否识别了边界条件？

3. **未饱和领域**：哪些方面还需要更多探索？

4. **下一步建议**：如何达到理论饱和？

返回JSON格式：
{{
    "overall_saturation": 0.75,
    "dimensions": {{
        "themes": {{"score": 0.8, "status": "接近饱和", "gaps": []}},
        "relationships": {{"score": 0.7, "status": "中等饱和", "gaps": ["主题X与Y的关系"]}},
        "propositions": {{"score": 0.6, "status": "部分饱和", "gaps": ["需要更多证据"]}},
        "boundaries": {{"score": 0.5, "status": "未饱和", "gaps": ["边界条件未明确"]}}
    }},
    "is_saturated": false,
    "analysis": "整体分析...",
    "unsaturated_areas": ["未饱和领域1", "未饱和领域2"],
    "next_steps": [
        "建议1：收集更多X类型的数据",
        "建议2：深入探索Y关系",
        "建议3：识别边界条件"
    ],
    "estimated_additional_data": "估计需要约X%的额外数据"
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2000
        )

        default_result = {
            "overall_saturation": 0.5,
            "dimensions": {
                "themes": {"score": 0.5, "status": "未饱和", "gaps": []},
                "relationships": {"score": 0.5, "status": "未饱和", "gaps": []},
                "propositions": {"score": 0.5, "status": "未饱和", "gaps": []},
                "boundaries": {"score": 0.5, "status": "未饱和", "gaps": []}
            },
            "is_saturated": False,
            "analysis": "需要更多数据才能评估理论饱和度",
            "unsaturated_areas": [],
            "next_steps": ["继续收集数据", "深化编码和主题分析"],
            "estimated_additional_data": "需要约50%的额外数据"
        }

        return self._parse_json_response(response.content, default_result)

    def interpretive_framework(
        self,
        themes: List,
        research_question: str
    ) -> Dict:
        """构建解释性框架

        将主题整合成一个连贯的解释性框架。

        Args:
            themes: 主题列表
            research_question: 研究问题

        Returns:
            解释性框架
        """
        # 准备主题详情
        theme_details = "\n".join([
            f"\n主题：{t.get('name', '')}\n描述：{t.get('description', '')}\n定义：{t.get('definition', '未提供')}"
            for t in themes
        ])

        prompt = f"""你是质性研究理论构建专家。请基于主题构建解释性框架。

研究问题：{research_question}

主题详情：{theme_details}

请构建一个解释性框架，回答研究问题。

解释性框架应包括：

1. **核心理论命题**：
   - 主要发现是什么？
   - 这些发现如何解释研究问题？

2. **概念关系图**：
   - 关键概念有哪些？
   - 这些概念之间如何关联？

3. **解释逻辑**：
   - 为什么这些主题以这种方式关联？
   - 底层的机制或过程是什么？

4. **条件分析**：
   - 这个框架在什么条件下成立？
   - 什么情况下可能不适用？

返回JSON格式：
{{
    "core_propositions": [
        {{
            "proposition": "理论命题陈述",
            "evidence": ["支持证据1", "支持证据2"],
            "confidence": 0.8
        }}
    ],
    "key_concepts": [
        {{
            "concept": "概念名称",
            "definition": "概念定义",
            "role": "在框架中的角色"
        }}
    ],
    "conceptual_relationships": [
        {{
            "concept1": "概念A",
            "concept2": "概念B",
            "relationship": "关系描述",
            "mechanism": "作用机制"
        }}
    ],
    "explanatory_logic": "整体解释逻辑的描述",
    "boundary_conditions": [
        {{
            "condition": "条件描述",
            "effect": "对框架的影响"
        }}
    ],
    "theoretical_contributions": [
        "理论贡献1",
        "理论贡献2"
    ],
    "framework_summary": "框架的简洁总结（2-3句话）"
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.4,
            max_tokens=3000
        )

        default_result = {
            "core_propositions": [],
            "key_concepts": [],
            "conceptual_relationships": [],
            "explanatory_logic": "无法构建详细的解释性框架",
            "boundary_conditions": [],
            "theoretical_contributions": [],
            "framework_summary": "需要更多主题和分析才能构建框架"
        }

        return self._parse_json_response(response.content, default_result)

    def generate_propositions(
        self,
        themes: List,
        codes: List,
        research_question: str
    ) -> Dict:
        """生成理论命题

        从主题和编码中抽象出可检验的理论命题。

        Args:
            themes: 主题列表
            codes: 编码列表
            research_question: 研究问题

        Returns:
            理论命题列表
        """
        prompt = f"""你是质性研究理论构建专家。请从主题和编码中生成理论命题。

研究问题：{research_question}

主题数：{len(themes)}
编码数：{len(codes)}

请生成理论命题。

理论命题的特点：
1. **抽象性**：超越具体案例，具有普遍性
2. **可检验性**：可以被后续研究验证或挑战
3. **清晰性**：概念明确，关系清晰
4. **简洁性**：用最少的语言表达核心观点

请提供：

1. **主要命题**（3-5个）：核心的理论陈述

2. **次要命题**（若干）：补充和细化

3. **命题的证据基础**：每个命题基于哪些主题/编码

4. **命题间关系**：命题之间如何关联？

返回JSON格式：
{{
    "main_propositions": [
        {{
            "statement": "命题陈述",
            "type": "因果|相关|条件|描述",
            "based_on": ["主题1", "编码1"],
            "rationale": "命题的理由",
            "confidence": 0.8
        }}
    ],
    "secondary_propositions": [
        {{
            "statement": "次要命题",
            "clarifies": "主命题1",
            "rationale": "理由"
        }}
    ],
    "proposition_network": [
        {{
            "prop1": "命题A",
            "prop2": "命题B",
            "relationship": "支持|细化|条件|矛盾"
        }}
    ],
    "theoretical_implications": [
        "理论意义1",
        "理论意义2"
    ]
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.4,
            max_tokens=2500
        )

        default_result = {
            "main_propositions": [],
            "secondary_propositions": [],
            "proposition_network": [],
            "theoretical_implications": []
        }

        return self._parse_json_response(response.content, default_result)

    def identify_patterns(
        self,
        codes: List,
        text: str
    ) -> Dict:
        """识别模式

        识别文本中的重复模式、序列模式、条件模式等。

        Args:
            codes: 编码列表
            text: 原始文本

        Returns:
            模式识别结果
        """
        prompt = f"""你是质性研究模式识别专家。请从文本中识别模式。

编码数：{len(codes)}
文本长度：{len(text)} 字符
文本摘要：{text[:1500]}

请识别以下类型的模式：

1. **重复模式**：哪些元素或结构反复出现？

2. **序列模式**：是否存在时间或逻辑序列？

3. **条件模式**：什么条件下出现什么结果？

4. **对比模式**：是否存在并行的对比模式？

5. **循环模式**：是否存在循环或迭代？

返回JSON格式：
{{
    "repetitive_patterns": [
        {{
            "pattern": "模式描述",
            "frequency": "频率",
            "examples": ["例子1", "例子2"],
            "significance": "意义"
        }}
    ],
    "sequential_patterns": [
        {{
            "sequence": ["步骤1", "步骤2", "步骤3"],
            "description": "序列描述"
        }}
    ],
    "conditional_patterns": [
        {{
            "condition": "条件",
            "outcome": "结果",
            "mechanism": "机制"
        }}
    ],
    "contrast_patterns": [
        {{
            "contrasting_elements": ["元素A", "元素B"],
            "dimension": "对比维度",
            "significance": "对比的意义"
        }}
    ],
    "overall_pattern": "整体模式总结",
    "theoretical_relevance": "模式的理论意义"
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.4,
            max_tokens=2500
        )

        default_result = {
            "repetitive_patterns": [],
            "sequential_patterns": [],
            "conditional_patterns": [],
            "contrast_patterns": [],
            "overall_pattern": "无法识别详细模式",
            "theoretical_relevance": ""
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


def get_ai_deep_analyzer(
    provider_name: str = None,
    api_key: str = None,
    model: str = None,
    base_url: str = None
) -> DeepAnalyzer:
    """获取深度分析助手实例

    Args:
        provider_name: 提供商名称 ("lm_studio", "openai", "deepseek")，None时从session state获取
        api_key: API密钥（LM Studio不需要）
        model: 模型名称
        base_url: API地址（LM Studio/Deepseek需要）

    Returns:
        DeepAnalyzer实例
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

    return DeepAnalyzer(provider)
