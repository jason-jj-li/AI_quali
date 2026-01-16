"""
LM Studio本地LLM接口实现
使用OpenAI兼容API，支持本地运行的开源模型
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
from .openai import OpenAIProvider


class LMStudioProvider(LLMProvider):
    """
    LM Studio本地LLM提供商

    LM Studio是一个本地LLM运行环境，支持多种开源模型：
    - Llama 3.x
    - Mistral
    - Phi-3
    - Qwen
    - 其他兼容GGUF格式的模型

    特点：
    - 完全本地运行，保护隐私
    - 无需API费用
    - 支持离线使用
    - 使用OpenAI兼容API

    默认地址: http://localhost:1234/v1
    """

    PROVIDER_NAME = "LM Studio"
    REQUIRED_PACKAGES = ["openai>=1.0.0"]
    SUPPORTED_MODELS = [
        "local-model",      # 默认通用名称
        "custom-model",     # 用户自定义模型
    ]

    # 本地模型无API费用
    PRICING = {
        "local-model": {"input": 0, "output": 0},
        "custom-model": {"input": 0, "output": 0},
    }

    def __init__(self, config: LLMConfig):
        # 检查依赖
        statuses, all_installed = self.check_dependencies()
        if not all_installed:
            missing_pkgs = [s.package_name for s in statuses if not s.installed]
            raise DependencyError(self.PROVIDER_NAME, missing_pkgs)

        # 设置默认base_url（如果未提供）
        if not config.base_url:
            from config import SUPPORTED_LLM_PROVIDERS
            config.base_url = SUPPORTED_LLM_PROVIDERS["lm_studio"]["default_base_url"]

        super().__init__(config)
        self._initialize_client()

    def _initialize_client(self):
        """初始化LM Studio客户端（使用OpenAI兼容API）"""
        try:
            from openai import OpenAI
            # LM Studio使用OpenAI兼容API
            self._client = OpenAI(
                base_url=self.config.base_url,
                api_key=self.config.api_key or "not-needed"  # 本地服务不需要真实API密钥
            )
        except ImportError:
            raise DependencyError(self.PROVIDER_NAME, self.REQUIRED_PACKAGES)

    def validate_api_key(self) -> bool:
        """
        验证LM Studio连接
        本地服务无需验证API密钥，只需检查连接是否可用
        """
        try:
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception:
            # 本地服务可能未启动，返回False
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        调用LM Studio API生成文本

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            LLMResponse对象
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
            # 调用LM Studio API（OpenAI兼容）
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
                top_p=kwargs.get("top_p", self.config.top_p),
            )

            # 解析响应
            choice = response.choices[0]
            content = choice.message.content

            # 获取token使用情况
            usage = response.usage
            tokens_used = {
                "prompt": usage.prompt_tokens if usage else 0,
                "completion": usage.completion_tokens if usage else 0,
                "total": usage.total_tokens if usage else 0,
            }

            # 本地模型无成本
            return LLMResponse(
                content=content,
                model=self.config.model,
                provider=self.PROVIDER_NAME,
                tokens_used=tokens_used,
                cost=0.0,  # 本地模型无费用
                raw_response=response,
            )

        except ImportError as e:
            raise DependencyError(self.PROVIDER_NAME, self.REQUIRED_PACKAGES)
        except Exception as e:
            error_str = str(e).lower()
            if "connection" in error_str or "refused" in error_str:
                raise APIKeyError(f"无法连接到LM Studio服务 ({self.config.base_url})，请确保LM Studio正在运行")
            elif "maximum context length" in error_str or "too many tokens" in error_str:
                raise TokenLimitError(f"Token超限: {e}")
            else:
                raise

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        估算成本（本地模型为0）

        Args:
            prompt_tokens: 输入token数
            completion_tokens: 输出token数

        Returns:
            成本（始终为0）
        """
        return 0.0

    def count_tokens(self, text: str) -> int:
        """
        计算token数（粗略估算）

        Args:
            text: 输入文本

        Returns:
            token数估算
        """
        # 本地模型token数可能不同，使用基类估算
        return super().count_tokens(text)


def get_lm_studio_provider(base_url: str = None, model: str = "local-model") -> LMStudioProvider:
    """
    获取LM Studio提供商实例

    Args:
        base_url: LM Studio API地址，默认为 http://localhost:1234/v1
        model: 模型名称

    Returns:
        LMStudioProvider实例
    """
    if not base_url:
        from config import SUPPORTED_LLM_PROVIDERS
        base_url = SUPPORTED_LLM_PROVIDERS["lm_studio"]["default_base_url"]

    config = LLMConfig(
        provider="lm_studio",
        model=model,
        api_key="not-needed",  # 本地服务不需要API密钥
        base_url=base_url,
    )

    return LMStudioProvider(config)
