"""
OpenAI LLM接口实现
支持GPT-4, GPT-4o, GPT-4o-mini等模型
"""
from typing import Optional, Dict, Any
from .base import (
    LLMProvider,
    LLMResponse,
    LLMConfig,
    DependencyError,
    APIKeyError,
    RateLimitError,
    TokenLimitError,
)


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM提供商

    支持模型：
    - gpt-4o: 最新的GPT-4 Omni模型
    - gpt-4o-mini: 轻量级版本
    - gpt-4-turbo: GPT-4 Turbo
    - gpt-3.5-turbo: GPT-3.5 Turbo

    定价 (美元/1K tokens，2024年)：
    - gpt-4o: $5.00 (input), $15.00 (output)
    - gpt-4o-mini: $0.15 (input), $0.60 (output)
    - gpt-4-turbo: $10.00 (input), $30.00 (output)
    - gpt-3.5-turbo: $0.50 (input), $1.50 (output)
    """

    PROVIDER_NAME = "OpenAI"
    REQUIRED_PACKAGES = ["openai>=1.0.0"]
    SUPPORTED_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ]

    # 定价表 (美元/1K tokens)
    PRICING = {
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }

    def __init__(self, config: LLMConfig):
        # 检查依赖
        statuses, all_installed = self.check_dependencies()
        if not all_installed:
            missing_pkgs = [s.package_name for s in statuses if not s.installed]
            raise DependencyError(self.PROVIDER_NAME, missing_pkgs)

        super().__init__(config)
        self._initialize_client()

    def _initialize_client(self):
        """初始化OpenAI客户端"""
        try:
            from openai import OpenAI
            # 支持LM Studio等本地LLM服务（通过自定义base_url）
            if self.config.base_url:
                self._client = OpenAI(
                    base_url=self.config.base_url,
                    api_key=self.config.api_key or "not-needed"  # 本地服务通常不需要API密钥
                )
            else:
                self._client = OpenAI(api_key=self.config.api_key)
        except ImportError:
            raise DependencyError(self.PROVIDER_NAME, self.REQUIRED_PACKAGES)

    def validate_api_key(self) -> bool:
        """
        验证API密钥
        通过调用一个简单的API请求来验证
        """
        try:
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "unauthorized" in error_str:
                return False
            # 其他错误可能是临时性的，暂时认为密钥有效
            return True

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        调用OpenAI API生成文本

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数 (top_p, frequency_penalty, presence_penalty等)

        Returns:
            LLMResponse对象

        Raises:
            APIKeyError: API密钥无效
            RateLimitError: 速率限制
            TokenLimitError: Token超限
        """
        # 构建消息列表
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # 使用配置或覆盖参数
        temp = temperature if temperature is not None else self.config.temperature
        max_tok = max_tokens if max_tokens is not None else self.config.max_tokens

        try:
            # 调用OpenAI API
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
                top_p=kwargs.get("top_p", self.config.top_p),
                frequency_penalty=kwargs.get("frequency_penalty", self.config.frequency_penalty),
                presence_penalty=kwargs.get("presence_penalty", self.config.presence_penalty),
            )

            # 解析响应
            choice = response.choices[0]
            content = choice.message.content

            # 获取token使用情况
            usage = response.usage
            tokens_used = {
                "prompt": usage.prompt_tokens,
                "completion": usage.completion_tokens,
                "total": usage.total_tokens,
            }

            # 计算成本
            cost = self.estimate_cost(usage.prompt_tokens, usage.completion_tokens)

            return LLMResponse(
                content=content,
                model=self.config.model,
                provider=self.PROVIDER_NAME,
                tokens_used=tokens_used,
                cost=cost,
                raw_response=response,
            )

        except ImportError as e:
            raise DependencyError(self.PROVIDER_NAME, self.REQUIRED_PACKAGES)
        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "unauthorized" in error_str or "authentication" in error_str:
                raise APIKeyError(f"OpenAI API密钥无效: {e}")
            elif "rate limit" in error_str or "quota" in error_str:
                raise RateLimitError(f"OpenAI API速率限制: {e}")
            elif "maximum context length" in error_str or "too many tokens" in error_str:
                raise TokenLimitError(f"Token超限: {e}")
            else:
                raise

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        估算API调用成本

        Args:
            prompt_tokens: 输入token数
            completion_tokens: 输出token数

        Returns:
            估算成本（美元）
        """
        pricing = self.PRICING.get(self.config.model, {"input": 0, "output": 0})
        input_cost = (prompt_tokens / 1000) * pricing["input"]
        output_cost = (completion_tokens / 1000) * pricing["output"]
        return input_cost + output_cost

    def count_tokens(self, text: str) -> int:
        """
        使用tiktoken计算精确的token数

        Args:
            text: 输入文本

        Returns:
            token数
        """
        try:
            import tiktoken
            # 获取对应模型的编码器
            encoding = tiktoken.encoding_for_model(self.config.model)
            return len(encoding.encode(text))
        except ImportError:
            # 如果没有tiktoken，使用基类的粗略估算
            return super().count_tokens(text)
