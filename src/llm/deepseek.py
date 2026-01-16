"""
Deepseek LLM Provider
使用OpenAI兼容接口
"""
from typing import Optional
from .openai import OpenAIProvider
from .base import LLMConfig, LLMResponse


class DeepseekProvider(OpenAIProvider):
    """
    Deepseek Provider - 使用OpenAI兼容API

    支持模型：
    - deepseek-chat: Deepseek对话模型
    - deepseek-coder: Deepseek代码模型

    定价 (人民币/1K tokens)：
    - deepseek-chat: ¥0.001 (input), ¥0.002 (output)
    - deepseek-coder: ¥0.001 (input), ¥0.002 (output)
    """

    PROVIDER_NAME = "Deepseek"
    REQUIRED_PACKAGES = ["openai>=1.0.0"]
    SUPPORTED_MODELS = ["deepseek-chat", "deepseek-coder"]

    # 定价表 (人民币/1K tokens)
    PRICING = {
        "deepseek-chat": {"input": 0.001, "output": 0.002},
        "deepseek-coder": {"input": 0.001, "output": 0.002},
    }

    def __init__(self, config: LLMConfig):
        # 设置Deepseek的base_url
        if not config.base_url:
            config.base_url = "https://api.deepseek.com/v1"
        super().__init__(config)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        调用Deepseek API生成文本

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            LLMResponse对象
        """
        response = super().generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        # 修改provider名称
        response.provider = self.PROVIDER_NAME
        return response

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        估算API调用成本（人民币）

        Args:
            prompt_tokens: 输入token数
            completion_tokens: 输出token数

        Returns:
            估算成本（人民币）
        """
        pricing = self.PRICING.get(self.config.model, {"input": 0, "output": 0})
        input_cost = (prompt_tokens / 1000) * pricing["input"]
        output_cost = (completion_tokens / 1000) * pricing["output"]
        return input_cost + output_cost
