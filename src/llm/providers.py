# -*- coding: utf-8 -*-
"""
LLM Provider Factory Module
提供统一的 LLM 提供商创建接口
"""
from typing import Optional, Dict, Any
from .base import LLMConfig, LLMProvider
from .openai import OpenAIProvider
from .claude import ClaudeProvider
from .deepseek import DeepseekProvider
from .lm_studio import LMStudioProvider


# ==================== Provider Registry ====================

PROVIDER_REGISTRY: Dict[str, type] = {
    "openai": OpenAIProvider,
    "anthropic": ClaudeProvider,
    "claude": ClaudeProvider,  # 别名
    "deepseek": DeepseekProvider,
    "lm_studio": LMStudioProvider,
    "lmstudio": LMStudioProvider,  # 别名
}


def get_provider_class(provider_name: str) -> type:
    """
    获取提供商类

    Args:
        provider_name: 提供商名称

    Returns:
        提供商类

    Raises:
        ValueError: 不支持的提供商
    """
    provider_name_lower = provider_name.lower().replace("-", "_").replace(" ", "_")

    if provider_name_lower not in PROVIDER_REGISTRY:
        supported = ", ".join(PROVIDER_REGISTRY.keys())
        raise ValueError(
            f"不支持的 LLM 提供商: {provider_name}. "
            f"支持的提供商: {supported}"
        )

    return PROVIDER_REGISTRY[provider_name_lower]


def create_provider(
    provider_name: str,
    api_key: str,
    model: str,
    base_url: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 2000,
    **kwargs
) -> LLMProvider:
    """
    创建 LLM 提供商实例

    Args:
        provider_name: 提供商名称 (openai, anthropic, deepseek, lm_studio)
        api_key: API 密钥
        model: 模型名称
        base_url: API 基础 URL (可选，用于本地模型)
        temperature: 温度参数
        max_tokens: 最大 token 数
        **kwargs: 其他参数

    Returns:
        LLM 提供商实例

    Raises:
        ValueError: 不支持的提供商

    Examples:
        >>> provider = create_provider("openai", "sk-xxx", "gpt-4o")
        >>> provider = create_provider("lm_studio", "", "local-model")
    """
    provider_class = get_provider_class(provider_name)

    config = LLMConfig(
        provider=provider_name,
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )

    return provider_class(config)


def create_provider_from_dict(config: Dict[str, Any]) -> LLMProvider:
    """
    从字典配置创建 LLM 提供商实例

    Args:
        config: 配置字典，包含:
            - provider: 提供商名称
            - api_key: API 密钥
            - model: 模型名称
            - base_url: (可选) API 基础 URL
            - temperature: (可选) 温度参数
            - max_tokens: (可选) 最大 token 数

    Returns:
        LLM 提供商实例

    Examples:
        >>> config = {
        ...     "provider": "openai",
        ...     "api_key": "sk-xxx",
        ...     "model": "gpt-4o",
        ...     "temperature": 0.5
        ... }
        >>> provider = create_provider_from_dict(config)
    """
    return create_provider(
        provider_name=config.get("provider", "lm_studio"),
        api_key=config.get("api_key", ""),
        model=config.get("model", "local-model"),
        base_url=config.get("base_url"),
        temperature=config.get("temperature", 0.3),
        max_tokens=config.get("max_tokens", 2000),
    )


def list_supported_providers() -> list[str]:
    """
    列出所有支持的 LLM 提供商

    Returns:
        提供商名称列表
    """
    return list(PROVIDER_REGISTRY.keys())


def get_provider_info(provider_name: str) -> Dict[str, Any]:
    """
    获取提供商信息

    Args:
        provider_name: 提供商名称

    Returns:
        提供商信息字典，包含:
            - name: 提供商名称
            - supported_models: 支持的模型列表
            - required_packages: 需要的依赖包
    """
    provider_class = get_provider_class(provider_name)

    return {
        "name": provider_class.PROVIDER_NAME,
        "supported_models": provider_class.SUPPORTED_MODELS,
        "required_packages": provider_class.REQUIRED_PACKAGES,
        "pricing": provider_class.PRICING,
    }


def check_provider_dependencies(provider_name: str) -> tuple[list, bool]:
    """
    检查提供商的依赖安装状态

    Args:
        provider_name: 提供商名称

    Returns:
        (依赖状态列表, 是否全部安装)
    """
    provider_class = get_provider_class(provider_name)
    return provider_class.check_dependencies()


# ==================== Convenience Functions ====================

def create_openai_provider(
    api_key: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> OpenAIProvider:
    """快捷创建 OpenAI 提供商"""
    return create_provider("openai", api_key, model, None, temperature, max_tokens)


def create_claude_provider(
    api_key: str,
    model: str = "claude-3-5-sonnet-20241022",
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> ClaudeProvider:
    """快捷创建 Claude 提供商"""
    return create_provider("anthropic", api_key, model, None, temperature, max_tokens)


def create_deepseek_provider(
    api_key: str,
    model: str = "deepseek-chat",
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> DeepseekProvider:
    """快捷创建 Deepseek 提供商"""
    return create_provider("deepseek", api_key, model, None, temperature, max_tokens)


def create_lm_studio_provider(
    base_url: str = "http://localhost:1234/v1",
    model: str = "local-model",
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> LMStudioProvider:
    """快捷创建 LM Studio 提供商"""
    return create_provider("lm_studio", "", model, base_url, temperature, max_tokens)
