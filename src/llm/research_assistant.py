"""
研究设计AI助手
提供研究问题优化、访谈提纲生成等功能
"""
from typing import Dict, List
from .base import LLMProvider, LLMConfig
from dataclasses import dataclass
import re
import json


@dataclass
class ResearchQuestionResult:
    """研究问题优化结果"""
    original_question: str
    improved_question: str
    suggestions: List[str]
    clarity_score: float  # 清晰度评分
    feasibility_score: float  # 可行性评分


@dataclass
class InterviewGuideSection:
    """访谈提纲章节"""
    title: str
    purpose: str
    questions: List[str]


@dataclass
class InterviewGuideResult:
    """访谈提纲生成结果"""
    research_question: str
    participant_type: str
    duration: str
    sections: List[InterviewGuideSection]
    total_questions: int


class ResearchAssistant:
    """研究设计AI助手

    提供以下功能：
    - 研究问题优化
    - 访谈提纲生成
    - 研究设计建议
    """

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def optimize_research_question(self, question: str) -> Dict:
        """优化研究问题

        Args:
            question: 原始研究问题

        Returns:
            包含优化后的问题和建议的字典
        """
        prompt = f"""你是质性研究方法学专家。请评估并优化以下研究问题：

研究问题：{question}

请从以下维度分析：
1. 清晰度：问题是否明确、具体、不含糊？
2. 可操作性：是否可以转化为可执行的研究活动？
3. 质性适用性：是否适合质性研究方法？
4. 焦点性：是否聚焦于单一核心问题？

请提供：
1. 优化后的研究问题（保持原意，使其更清晰、更可操作）
2. 优化建议（3-5条具体建议）
3. 清晰度评分（0-1）
4. 可行性评分（0-1）

返回JSON格式：
{{
    "improved_question": "优化后的研究问题",
    "suggestions": ["建议1", "建议2", "建议3"],
    "clarity_score": 0.8,
    "feasibility_score": 0.9
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.4,
            max_tokens=1500
        )

        # 解析JSON响应
        try:
            # 提取JSON部分
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # 如果没有找到JSON，构造基本响应
                result = {
                    "improved_question": question,
                    "suggestions": ["请重新审视研究问题的清晰度"],
                    "clarity_score": 0.5,
                    "feasibility_score": 0.5
                }
        except json.JSONDecodeError:
            # JSON解析失败，返回基本结构
            result = {
                "improved_question": question,
                "suggestions": ["AI建议：请使研究问题更加具体和可操作"],
                "clarity_score": 0.6,
                "feasibility_score": 0.6
            }

        return result

    def generate_interview_guide(
        self,
        research_question: str,
        participant_type: str = "研究对象",
        duration: str = "1小时",
        question_count: int = 10
    ) -> Dict:
        """生成访谈提纲

        Args:
            research_question: 研究问题
            participant_type: 访谈对象类型
            duration: 预计访谈时长
            question_count: 问题数量

        Returns:
            包含访谈提纲的字典
        """
        prompt = f"""你是质性研究方法学专家。请根据以下信息生成结构化的访谈提纲：

研究问题：{research_question}
访谈对象：{participant_type}
预计时长：{duration}
问题数量：约{question_count}个

访谈提纲应包括以下部分：
1. **开场与破冰**（1-2个问题）- 建立 rapport，让参与者感到舒适
2. **背景信息收集**（2-3个问题）- 了解参与者基本情况
3. **核心探索问题**（4-6个问题）- 直接围绕研究问题展开
4. **深入追问**（2-3个问题）- 挖掘深层理解和体验
5. **结束问题**（1-2个问题）- 给参与者补充和总结的机会

每个问题应该：
- 开放式（避免"是/否"问题）
- 避免引导性语言
- 清晰具体，避免专业术语
- 符合逻辑顺序（从一般到具体）
- 尊重参与者的经验和视角

返回JSON格式：
{{
    "sections": [
        {{
            "title": "章节标题",
            "purpose": "本章节目的",
            "questions": ["问题1", "问题2", "问题3"]
        }}
    ],
    "total_questions": 问题总数,
    "estimated_duration": "预计时长",
    "notes": "访谈注意事项"
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.5,
            max_tokens=2500
        )

        # 解析JSON响应
        try:
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # 构造基本响应
                result = {
                    "sections": [
                        {
                            "title": "开场问题",
                            "purpose": "建立良好的访谈氛围",
                            "questions": ["请介绍一下您自己", "您是如何参与到这个活动中的？"]
                        },
                        {
                            "title": "核心问题",
                            "purpose": "探索研究问题的核心",
                            "questions": [f"关于{research_question}，您能谈谈您的看法吗？"]
                        }
                    ],
                    "total_questions": 3,
                    "estimated_duration": duration,
                    "notes": "请注意倾听，避免打断"
                }
        except json.JSONDecodeError:
            result = {
                "sections": [
                    {
                        "title": "开场",
                        "purpose": "破冰",
                        "questions": ["请简单介绍一下自己"]
                    }
                ],
                "total_questions": 1,
                "estimated_duration": duration,
                "notes": "访谈提纲生成遇到问题，请手动调整"
            }

        return result

    def evaluate_research_design(
        self,
        research_question: str,
        methodology: str = None
    ) -> Dict:
        """评估研究设计

        Args:
            research_question: 研究问题
            methodology: 研究方法（如：现象学、扎根理论、个案研究等）

        Returns:
            研究设计评估结果
        """
        method_text = f"研究方法：{methodology}" if methodology else "未指定研究方法"

        prompt = f"""你是质性研究方法学专家。请评估以下研究设计：

研究问题：{research_question}
{method_text}

请评估：
1. 研究问题的质量（清晰、聚焦、可研究）
2. 方法的适用性（如已指定）
3. 可能的挑战和局限性
4. 改进建议

返回JSON格式：
{{
    "overall_assessment": "整体评价",
    "strengths": ["优势1", "优势2"],
    "challenges": ["挑战1", "挑战2"],
    "recommendations": ["建议1", "建议2"],
    "suggested_methodology": "建议的研究方法"
}}"""

        response = self.provider.generate(
            prompt=prompt,
            temperature=0.4,
            max_tokens=2000
        )

        try:
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        # 返回基本结构
        return {
            "overall_assessment": "研究设计需要进一步明确",
            "strengths": ["提出了明确的研究问题"],
            "challenges": ["需要更详细的研究设计"],
            "recommendations": ["请明确研究方法", "请考虑数据收集策略"],
            "suggested_methodology": "根据研究问题选择合适的质性研究方法"
        }


def get_ai_research_assistant(
    provider_name: str = None,
    api_key: str = None,
    model: str = None,
    base_url: str = None
) -> ResearchAssistant:
    """获取研究设计助手实例

    Args:
        provider_name: 提供商名称 ("lm_studio", "openai", "deepseek")，None时从session state获取
        api_key: API密钥（LM Studio不需要）
        model: 模型名称
        base_url: API地址（LM Studio/Deepseek需要）

    Returns:
        ResearchAssistant实例
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
            max_tokens=2000
        )
        provider = LMStudioProvider(llm_config)
    elif provider_name == "deepseek":
        llm_config = LLMConfig(
            provider="deepseek",
            model=model or "deepseek-chat",
            api_key=api_key,
            base_url=base_url or "https://api.deepseek.com/v1",
            temperature=0.4,
            max_tokens=2000
        )
        provider = DeepseekProvider(llm_config)
    elif provider_name == "openai":
        llm_config = LLMConfig(
            provider="openai",
            model=model or "gpt-4o-mini",
            api_key=api_key,
            temperature=0.4,
            max_tokens=2000
        )
        provider = OpenAIProvider(llm_config)
    else:
        raise ValueError(f"不支持的提供商: {provider_name}")

    return ResearchAssistant(provider)
