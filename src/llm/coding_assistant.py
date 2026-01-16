"""
AI编码助手模块
实现AI辅助编码功能，参考literature-review技能的两阶段模式
"""
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from src.llm.base import LLMConfig, LLMProvider, LLMResponse


@dataclass
class CodingSuggestion:
    """编码建议数据类"""
    code_name: str
    reasoning: str
    confidence: float
    text_evidence: str
    is_new_code: bool
    suggested_description: Optional[str] = None


@dataclass
class CodingBatchResult:
    """批量编码结果"""
    fragment_id: str
    text: str
    suggestions: List[CodingSuggestion]
    error: Optional[str] = None


class AICodingAssistant:
    """
    AI编码助手

    支持功能：
    1. 演绎式编码（基于现有编码本）
    2. 归纳式编码（建议新编码）
    3. 编码理由解释
    4. 批量AI编码
    """

    def __init__(self, provider: LLMProvider):
        """
        初始化AI编码助手

        Args:
            provider: LLM提供商实例
        """
        self.provider = provider
        self._load_prompts()

    def _load_prompts(self):
        """加载提示词模板"""
        import os
        from config import PROMPTS_DIR

        # 加载编码提示词
        coding_prompts_path = PROMPTS_DIR / "coding.txt"
        if coding_prompts_path.exists():
            with open(coding_prompts_path, 'r', encoding='utf-8') as f:
                coding_content = f.read()
                # 执行提示词文件以获取模板
                exec_globals = {}
                exec(coding_content, exec_globals)
                self.system_prompt = exec_globals.get('SYSTEM_PROMPT', '')
                self.deductive_prompt = exec_globals.get('DEDUCTIVE_CODING_PROMPT', '')
                self.inductive_prompt = exec_globals.get('INDUCTIVE_CODING_PROMPT', '')
                self.explain_prompt = exec_globals.get('EXPLAIN_CODING_PROMPT', '')
        else:
            # 使用默认提示词
            self.system_prompt = "你是一位资深的质性研究方法学专家，擅长对质性数据进行编码。"
            self.deductive_prompt = "请对以下文本进行编码：{text}\n\n现有编码本：{codebook}"
            self.inductive_prompt = "请对以下文本进行开放式编码：{text}"
            self.explain_prompt = "请解释编码决策：编码={code}, 文本={text}"

    def suggest_codes_deductive(
        self,
        text: str,
        codebook: List[Dict[str, Any]],
        research_question: str = "",
        methodology: str = "",
        max_suggestions: int = 3
    ) -> List[CodingSuggestion]:
        """
        演绎式编码：基于现有编码本建议编码

        Args:
            text: 待编码文本
            codebook: 现有编码本 [{"name": "...", "description": "..."}, ...]
            research_question: 研究问题
            methodology: 研究方法
            max_suggestions: 最大建议数量

        Returns:
            编码建议列表
        """
        # 格式化编码本
        codebook_str = self._format_codebook(codebook)

        # 构建提示词
        prompt = self.deductive_prompt.format(
            research_question=research_question,
            methodology=methodology,
            codebook=codebook_str,
            text=text
        )

        try:
            # 调用LLM
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,  # 编码任务使用较低温度
                max_tokens=1500
            )

            # 解析响应
            suggestions = self._parse_coding_response(response.content)

            # 限制建议数量
            return suggestions[:max_suggestions]

        except Exception as e:
            # 返回错误建议
            return [CodingSuggestion(
                code_name="错误",
                reasoning=f"AI编码失败: {str(e)}",
                confidence=0.0,
                text_evidence="",
                is_new_code=False
            )]

    def suggest_codes_inductive(
        self,
        text: str,
        research_question: str = "",
        methodology: str = "",
        max_suggestions: int = 3
    ) -> List[CodingSuggestion]:
        """
        归纳式编码：开放式编码，建议新编码

        Args:
            text: 待编码文本
            research_question: 研究问题
            methodology: 研究方法
            max_suggestions: 最大建议数量

        Returns:
            编码建议列表（包含新编码建议）
        """
        # 构建提示词
        prompt = self.inductive_prompt.format(
            research_question=research_question,
            methodology=methodology,
            text=text
        )

        try:
            # 调用LLM
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.4,  # 稍高的温度以鼓励创造性
                max_tokens=1500
            )

            # 解析响应
            suggestions = self._parse_coding_response(response.content)

            # 限制建议数量
            return suggestions[:max_suggestions]

        except Exception as e:
            # 返回错误建议
            return [CodingSuggestion(
                code_name="错误",
                reasoning=f"AI编码失败: {str(e)}",
                confidence=0.0,
                text_evidence="",
                is_new_code=True
            )]

    def explain_coding(
        self,
        code_name: str,
        code_description: str,
        text: str,
        confidence: float = 0.0
    ) -> str:
        """
        解释编码决策的理由

        Args:
            code_name: 编码名称
            code_description: 编码描述
            text: 文本片段
            confidence: 置信度

        Returns:
            解释文本
        """
        # 构建提示词
        prompt = self.explain_prompt.format(
            code_name=code_name,
            code_description=code_description,
            text=text,
            confidence=confidence
        )

        try:
            # 调用LLM
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=500
            )

            return response.content

        except Exception as e:
            return f"解释生成失败: {str(e)}"

    def batch_suggest_codes(
        self,
        fragments: List[Dict[str, str]],
        codebook: List[Dict[str, Any]],
        research_question: str = "",
        methodology: str = "",
        mode: str = "deductive",
        progress_callback=None
    ) -> List[CodingBatchResult]:
        """
        批量AI编码

        Args:
            fragments: 文本片段列表 [{"id": "1", "text": "..."}, ...]
            codebook: 现有编码本
            research_question: 研究问题
            methodology: 研究方法
            mode: 编码模式 ("deductive" 或 "inductive")
            progress_callback: 进度回调函数

        Returns:
            批量编码结果列表
        """
        results = []

        for i, fragment in enumerate(fragments):
            fragment_id = fragment.get("id", str(i))
            text = fragment.get("text", "")

            try:
                if mode == "deductive":
                    suggestions = self.suggest_codes_deductive(
                        text=text,
                        codebook=codebook,
                        research_question=research_question,
                        methodology=methodology
                    )
                else:  # inductive
                    suggestions = self.suggest_codes_inductive(
                        text=text,
                        research_question=research_question,
                        methodology=methodology
                    )

                results.append(CodingBatchResult(
                    fragment_id=fragment_id,
                    text=text,
                    suggestions=suggestions,
                    error=None
                ))

            except Exception as e:
                results.append(CodingBatchResult(
                    fragment_id=fragment_id,
                    text=text,
                    suggestions=[],
                    error=str(e)
                ))

            # 调用进度回调
            if progress_callback:
                progress_callback(i + 1, len(fragments))

        return results

    def _format_codebook(self, codebook: List[Dict[str, Any]]) -> str:
        """格式化编码本为字符串"""
        if not codebook:
            return "（暂无编码）"

        formatted = []
        for code in codebook:
            name = code.get("name", "")
            desc = code.get("description", "")
            if desc:
                formatted.append(f"- {name}: {desc}")
            else:
                formatted.append(f"- {name}")

        return "\n".join(formatted)

    def _parse_coding_response(self, response: str) -> List[CodingSuggestion]:
        """
        解析LLM的编码响应

        Args:
            response: LLM响应文本

        Returns:
            编码建议列表
        """
        suggestions = []

        # 调试输出：打印原始响应
        print(f"[DEBUG] LLM Response: {response[:500]}...")

        # 预处理：移除markdown代码块标记
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]  # 移除 ```json
        elif response.startswith("```"):
            response = response[3:]   # 移除 ```
        if response.endswith("```"):
            response = response[:-3]  # 移除末尾的 ```
        response = response.strip()

        try:
            # 尝试解析JSON响应
            data = json.loads(response)

            if "suggested_codes" in data:
                for item in data["suggested_codes"]:
                    suggestions.append(CodingSuggestion(
                        code_name=item.get("code_name", ""),
                        reasoning=item.get("reasoning", ""),
                        confidence=item.get("confidence", 0.5),
                        text_evidence=item.get("text_evidence", ""),
                        is_new_code=item.get("is_new_code", False),
                        suggested_description=item.get("suggested_description")
                    ))
                print(f"[DEBUG] Parsed {len(suggestions)} codes from JSON")
            else:
                # 备用解析：如果响应格式不同
                print(f"[DEBUG] No 'suggested_codes' found in JSON")

        except json.JSONDecodeError as e:
            # 如果不是JSON格式，尝试简单解析
            print(f"[DEBUG] JSON decode error: {e}")
            print(f"[DEBUG] Response was: {response[:500]}")

            # 尝试提取类似JSON的内容
            import re
            json_match = re.search(r'\{[^{}]*"suggested_codes"[^{}]*\}', response, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    if "suggested_codes" in data:
                        for item in data["suggested_codes"]:
                            suggestions.append(CodingSuggestion(
                                code_name=item.get("code_name", ""),
                                reasoning=item.get("reasoning", ""),
                                confidence=item.get("confidence", 0.5),
                                text_evidence=item.get("text_evidence", ""),
                                is_new_code=item.get("is_new_code", False),
                                suggested_description=item.get("suggested_description")
                            ))
                        print(f"[DEBUG] Parsed {len(suggestions)} codes from extracted JSON")
                except:
                    pass

        return suggestions

    def check_consistency(
        self,
        code_name: str,
        code_description: str,
        coding_examples: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        检查编码应用的一致性

        Args:
            code_name: 编码名称
            code_description: 编码描述
            coding_examples: 编码应用实例 [{"text": "...", "source": "..."}, ...]

        Returns:
            一致性分析结果
        """
        # 格式化编码实例
        examples_str = self._format_coding_examples(coding_examples)

        prompt = f"""
请检查以下编码应用的一致性。

## 编码信息
- 编码名称：{code_name}
- 编码描述：{code_description}

## 编码应用实例
{examples_str}

## 任务要求
请分析这些编码应用是否一致，并输出JSON格式：
{{
    "consistency_score": 0.8,
    "analysis": "详细分析...",
    "inconsistent_cases": ["案例1", "案例2"],
    "improvement_suggestions": ["建议1", "建议2"]
}}
"""

        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=1000
            )

            return json.loads(response.content)

        except Exception as e:
            return {
                "consistency_score": 0.0,
                "analysis": f"一致性检查失败: {str(e)}",
                "inconsistent_cases": [],
                "improvement_suggestions": []
            }

    def _format_coding_examples(self, examples: List[Dict[str, str]]) -> str:
        """格式化编码实例为字符串"""
        formatted = []
        for i, example in enumerate(examples, 1):
            text = example.get("text", "")
            source = example.get("source", f"来源{i}")
            formatted.append(f"{i}. [{source}] {text}")

        return "\n".join(formatted)


    # Convenience wrapper methods for backward compatibility with new app.py
    def deductive_coding(self, text: str, codebook: list, research_question: str = "") -> list:
        """演绎式编码包装方法"""
        from dataclasses import dataclass
        from typing import List

        @dataclass
        class CodingResult:
            name: str
            description: str
            quotes: List[str]
            confidence: float

        results = []
        suggestions = self.suggest_codes_deductive(
            text=text,
            codebook=codebook,
            research_question=research_question
        )

        for s in suggestions:
            results.append(CodingResult(
                name=s.code_name,
                description=s.suggested_description or s.reasoning,
                quotes=[s.text_evidence],
                confidence=s.confidence
            ))

        return results

    def inductive_coding(self, text: str, research_question: str = "") -> list:
        """归纳式编码包装方法"""
        from dataclasses import dataclass
        from typing import List

        @dataclass
        class CodingResult:
            name: str
            description: str
            quotes: List[str]
            confidence: float

        results = []
        suggestions = self.suggest_codes_inductive(
            text=text,
            research_question=research_question
        )

        for s in suggestions:
            results.append(CodingResult(
                name=s.code_name,
                description=s.suggested_description or s.reasoning,
                quotes=[s.text_evidence],
                confidence=s.confidence
            ))

        return results


def get_ai_coding_assistant(provider_name: str = None, api_key: str = None, model: str = None, base_url: str = None):
    """
    获取AI编码助手实例

    Args:
        provider_name: 提供商名称 ("lm_studio", "openai", "deepseek")，None时从session state获取
        api_key: API密钥（LM Studio不需要）
        model: 模型名称
        base_url: API地址（LM Studio/Deepseek需要）

    Returns:
        AICodingAssistant实例
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

    return AICodingAssistant(provider)
