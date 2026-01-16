"""
Anthropic Claude LLM接口实现
支持Claude 3.5 Sonnet, Claude 3 Haiku等模型
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


class ClaudeProvider(LLMProvider):
    """
    Anthropic Claude LLM提供商

    支持模型：
    - claude-3-5-sonnet-20241022: Claude 3.5 Sonnet（最新旗舰模型）
    - claude-3-haiku-20240307: Claude 3 Haiku（快速轻量模型）

    定价 (美元/1K tokens，2024年)：
    - claude-3-5-sonnet: $3.00 (input), $15.00 (output)
    - claude-3-haiku: $0.25 (input), $1.25 (output)
    """

    PROVIDER_NAME = "Anthropic"
    REQUIRED_PACKAGES = ["anthropic>=0.18.0"]
    SUPPORTED_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-haiku-20240307",
    ]

    # 定价表 (美元/1K tokens)
    PRICING = {
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
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
        """初始化Anthropic客户端"""
        try:
            from anthropic import Anthropic
            self._client = Anthropic(api_key=self.config.api_key)
        except ImportError:
            raise DependencyError(self.PROVIDER_NAME, self.REQUIRED_PACKAGES)

    def validate_api_key(self) -> bool:
        """
        验证API密钥
        通过调用一个简单的API请求来验证
        """
        try:
            self._client.messages.create(
                model=self.config.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "unauthorized" in error_str or "authentication" in error_str:
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
        调用Anthropic API生成文本

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数 (top_p等)

        Returns:
            LLMResponse对象

        Raises:
            APIKeyError: API密钥无效
            RateLimitError: 速率限制
            TokenLimitError: Token超限
        """
        # 使用配置或覆盖参数
        temp = temperature if temperature is not None else self.config.temperature
        max_tok = max_tokens if max_tokens is not None else self.config.max_tokens

        try:
            # 构建API参数
            api_params = {
                "model": self.config.model,
                "max_tokens": max_tok,
                "temperature": temp,
                "messages": [{"role": "user", "content": prompt}],
            }

            # 添加系统提示词（如果有）
            if system_prompt:
                api_params["system"] = system_prompt

            # 添加top_p参数（如果提供）
            if "top_p" in kwargs:
                api_params["top_p"] = kwargs["top_p"]

            # 调用Anthropic API
            response = self._client.messages.create(**api_params)

            # 解析响应
            content = response.content[0].text

            # 获取token使用情况
            usage = response.usage
            tokens_used = {
                "prompt": usage.input_tokens,
                "completion": usage.output_tokens,
                "total": usage.input_tokens + usage.output_tokens,
            }

            # 计算成本
            cost = self.estimate_cost(usage.input_tokens, usage.output_tokens)

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
                raise APIKeyError(f"Anthropic API密钥无效: {e}")
            elif "rate limit" in error_str or "quota" in error_str:
                raise RateLimitError(f"Anthropic API速率限制: {e}")
            elif "maximum context length" in error_str or "too many tokens" in error_str or "prompt" in error_str and "too long" in error_str:
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
        使用anthropic的token计算方法
        Claude使用与GPT类似的tokenizer，粗略估算

        Args:
            text: 输入文本

        Returns:
            token数估算
        """
        # Anthropic的token计算与OpenAI类似
        # 粗略估算：英文约4字符=1token，中文约2字符=1token
        # 取中间值3字符=1token
        return len(text) // 3

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        流式生成文本（支持实时显示）

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Yields:
            文本片段
        """
        # 使用配置或覆盖参数
        temp = temperature if temperature is not None else self.config.temperature
        max_tok = max_tokens if max_tokens is not None else self.config.max_tokens

        try:
            # 构建API参数
            api_params = {
                "model": self.config.model,
                "max_tokens": max_tok,
                "temperature": temp,
                "messages": [{"role": "user", "content": prompt}],
            }

            # 添加系统提示词（如果有）
            if system_prompt:
                api_params["system"] = system_prompt

            # 添加top_p参数（如果提供）
            if "top_p" in kwargs:
                api_params["top_p"] = kwargs["top_p"]

            # 流式调用Anthropic API
            with self._client.messages.stream(**api_params) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "unauthorized" in error_str or "authentication" in error_str:
                raise APIKeyError(f"Anthropic API密钥无效: {e}")
            elif "rate limit" in error_str or "quota" in error_str:
                raise RateLimitError(f"Anthropic API速率限制: {e}")
            elif "maximum context length" in error_str or "too many tokens" in error_str:
                raise TokenLimitError(f"Token超限: {e}")
            else:
                raise
