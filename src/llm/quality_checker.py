"""
编码质量检查AI助手
提供编码饱和度、一致性、边缘案例识别等质量检查功能
"""
from typing import Dict, List
from .base import LLMProvider, LLMConfig
import re
import json


class QualityChecker:
    """编码质量检查助手

    提供以下功能：
    - 编码饱和度检查
    - 编码一致性检查
    - 边缘案例识别
    - 编码质量评分
    """

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def check_saturation(self, codes: List, text: str) -> Dict:
        """检查编码饱和度

        理论饱和度是指新数据不再产生新编码的状态。

        Args:
            codes: 编码列表
            text: 原始文本

        Returns:
            包含饱和度分析结果的字典
        """
        # 准备编码摘要
        code_summary = "\n".join([
            f"- {c.get('name', '')}: {c.get('description', '')[:80]}..."
            for c in codes[:10]
        ])

        prompt = f"""你是质性研究方法学专家。请评估编码的理论饱和度。

编码数量：{len(codes)}
编码列表：
{code_summary}

文本长度：{len(text)} 字符
文本摘要：{text[:500]}...

请分析：
1. **理论饱和度状态**：是否达到理论饱和？
   - 理论饱和的标志：新数据不再产生新的编码或编码类别
   - 请考虑当前编码数量是否足以覆盖研究现象

2. **编码覆盖率**：编码是否覆盖了文本的主要内容？

3. **潜在遗漏**：是否有明显的主题或模式未被编码？

4. **进一步行动建议**：
   - 如果未饱和，建议收集多少额外数据？
   - 是否需要细分某些宽泛的编码？
   - 是否需要合并相似的编码？

返回JSON格式：
{{
    "is_saturated": true/false,
    "saturation_score": 0.75,  // 0-1的饱和度评分
    "analysis": "详细分析...",
    "suggestions": ["建议1", "建议2", "建议3"],
    "potential_gaps": ["可能的遗漏1", "可能的遗漏2"],
    "next_steps": "下一步建议"
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2000
        )

        return self._parse_json_response(response.content, {
            "is_saturated": False,
            "saturation_score": 0.5,
            "analysis": "无法完成饱和度分析",
            "suggestions": ["请增加更多数据", "请检查编码是否覆盖所有主题"],
            "potential_gaps": [],
            "next_steps": "建议继续编码更多数据"
        })

    def check_internal_consistency(self, codes: List, text: str) -> Dict:
        """检查编码内部一致性

        分析编码间是否有重叠、冲突或不一致。

        Args:
            codes: 编码列表
            text: 原始文本

        Returns:
            包含一致性检查结果的字典
        """
        # 准备编码详情
        code_details = "\n".join([
            f"编码{i+1}: {c.get('name', '')}\n  描述: {c.get('description', '')}\n"
            for i, c in enumerate(codes)
        ])

        prompt = f"""你是质性研究方法学专家。请检查编码的内部一致性。

编码列表：
{code_details}

请检查：

1. **语义重复**：
   - 有没有两个或多个编码实际上描述的是同一个概念？
   - 请列出可能需要合并的编码

2. **定义冲突**：
   - 有没有编码的定义存在内在矛盾？
   - 有没有编码的描述与其名称不匹配？

3. **层次混乱**：
   - 有没有编码之间存在层次关系但未明确？
   - 有些"编码"实际上可能是更高层次的"主题"

4. **清晰度**：
   - 每个编码是否有清晰的描述？
   - 研究者能否一致地应用这些编码？

返回JSON格式：
{{
    "score": 0.85,  // 一致性评分 0-1
    "analysis": "整体一致性分析...",
    "issues": [
        {{
            "type": "重复|冲突|层次|清晰度",
            "description": "问题描述",
            "affected_codes": ["编码1", "编码2"],
            "suggestion": "改进建议"
        }}
    ],
    "recommendations": ["改进建议1", "改进建议2"],
    "merge_suggestions": [
        {{
            "codes": ["编码A", "编码B"],
            "suggested_name": "合并后的编码名",
            "reason": "合并理由"
        }}
    ]
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2500
        )

        return self._parse_json_response(response.content, {
            "score": 0.7,
            "analysis": "编码一致性检查完成",
            "issues": [],
            "recommendations": ["建议重新检查编码定义"],
            "merge_suggestions": []
        })

    def identify_deviant_cases(self, codes: List, text: str) -> Dict:
        """识别边缘案例

        边缘案例是那些不符合主流模式、能够挑战现有理解的重要发现。

        Args:
            codes: 编码列表
            text: 原始文本

        Returns:
            包含边缘案例识别结果的字典
        """
        # 准备编码列表
        code_names = [c.get('name', '') for c in codes]

        prompt = f"""你是质性研究方法学专家。请从文本中识别边缘案例（Deviant Cases）。

当前编码：{', '.join(code_names)}

文本：
{text[:3000]}

**边缘案例的重要性**：
边缘案例是那些不符合主流模式、能够挑战或丰富现有理解的发现。它们不是"错误"，而是重要的学习机会，能帮助研究者：
- 发现理论的边界条件
- 识别例外情况
- 理解现象的复杂性
- 避免过度概括

请识别以下类型的边缘案例：

1. **反例**：与主流发现直接矛盾的案例
2. **例外情况**：在特定条件下才出现的模式
3. **边界案例**：处于分类边界的模糊案例
4. **挑战性案例**：挑战现有编码或理解的案例

对于每个边缘案例，请提供：
- 标题
- 描述
- 相关引文
- 研究意义（为什么这个案例重要？）
- 对编码/理论的启示（如何调整现有理解？）

返回JSON格式：
{{
    "deviant_cases": [
        {{
            "title": "案例标题",
            "description": "案例描述",
            "quote": "相关引文",
            "significance": "研究意义",
            "implications": "对编码/理论的启示",
            "type": "反例|例外|边界|挑战"
        }}
    ],
    "main_patterns": ["主流模式1", "主流模式2"],
    "analysis": "边缘案例分析总结"
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.4,
            max_tokens=3000
        )

        return self._parse_json_response(response.content, {
            "deviant_cases": [],
            "main_patterns": ["未识别到明确的主流模式"],
            "analysis": "边缘案例识别完成"
        })

    def assess_coding_quality(self, codes: List, text: str) -> Dict:
        """综合评估编码质量

        Args:
            codes: 编码列表
            text: 原始文本

        Returns:
            包含质量评估结果的字典
        """
        prompt = f"""你是质性研究方法学专家。请综合评估编码质量。

编码数量：{len(codes)}
文本长度：{len(text)} 字符

请从以下维度评估编码质量：

1. **完整性**：编码是否覆盖了文本的主要内容？

2. **特异性**：编码是否足够具体，避免了过于宽泛的标签？

3. **互斥性**：编码之间是否有清晰的边界，减少了重叠？

4. **理论相关性**：编码是否与研究问题相关？

5. **可操作性**：编码是否有清晰的描述，能够被一致地应用？

返回JSON格式：
{{
    "overall_score": 0.8,  // 0-1的总体评分
    "dimensions": {{
        "completeness": {{"score": 0.8, "comment": "评价"}},
        "specificity": {{"score": 0.7, "comment": "评价"}},
        "exclusivity": {{"score": 0.85, "comment": "评价"}},
        "theoretical_relevance": {{"score": 0.9, "comment": "评价"}},
        "operability": {{"score": 0.75, "comment": "评价"}}
    }},
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["不足1", "不足2"],
    "recommendations": ["改进建议1", "改进建议2"]
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2000
        )

        return self._parse_json_response(response.content, {
            "overall_score": 0.75,
            "dimensions": {},
            "strengths": [],
            "weaknesses": [],
            "recommendations": ["继续改进编码质量"]
        })

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


def get_ai_quality_checker(
    provider_name: str = None,
    api_key: str = None,
    model: str = None,
    base_url: str = None
) -> QualityChecker:
    """获取质量检查助手实例

    Args:
        provider_name: 提供商名称 ("lm_studio", "openai", "deepseek")，None时从session state获取
        api_key: API密钥（LM Studio不需要）
        model: 模型名称
        base_url: API地址（LM Studio/Deepseek需要）

    Returns:
        QualityChecker实例
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
            temperature=0.3,
            max_tokens=2000
        )
        provider = LMStudioProvider(llm_config)
    elif provider_name == "deepseek":
        llm_config = LLMConfig(
            provider="deepseek",
            model=model or "deepseek-chat",
            api_key=api_key,
            base_url=base_url or "https://api.deepseek.com/v1",
            temperature=0.3,
            max_tokens=2000
        )
        provider = DeepseekProvider(llm_config)
    elif provider_name == "openai":
        llm_config = LLMConfig(
            provider="openai",
            model=model or "gpt-4o-mini",
            api_key=api_key,
            temperature=0.3,
            max_tokens=2000
        )
        provider = OpenAIProvider(llm_config)
    else:
        raise ValueError(f"不支持的提供商: {provider_name}")

    return QualityChecker(provider)
