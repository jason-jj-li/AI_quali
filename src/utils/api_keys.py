"""
API密钥管理模块
负责API密钥的本地存储、读取和验证
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional
import hashlib


class APIKeyManager:
    """API密钥管理器"""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        初始化API密钥管理器

        Args:
            storage_path: 存储路径，默认为data/api_keys.json
        """
        if storage_path is None:
            from config import DATA_DIR
            storage_path = DATA_DIR / "api_keys.json"

        self.storage_path = storage_path
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_key_hash(self, api_key: str) -> str:
        """
        对API密钥进行哈希处理（用于显示掩码）

        Args:
            api_key: API密钥

        Returns:
            哈希值
        """
        return hashlib.sha256(api_key.encode()).hexdigest()

    def _mask_key(self, api_key: str) -> str:
        """
        掩码API密钥，只显示前4位和后4位

        Args:
            api_key: API密钥

        Returns:
            掩码后的密钥
        """
        if len(api_key) <= 8:
            return "****"
        return f"{api_key[:4]}...{api_key[-4:]}"

    def _load_keys(self) -> Dict[str, Dict]:
        """
        从文件加载API密钥

        Returns:
            密钥字典 {provider: {"api_key": "...", "masked": "...", "hash": "..."}}
        """
        if not self.storage_path.exists():
            return {}

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_keys(self, keys: Dict[str, Dict]):
        """
        保存API密钥到文件

        Args:
            keys: 密钥字典
        """
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(keys, f, indent=2, ensure_ascii=False)

    def set_api_key(self, provider: str, api_key: str) -> bool:
        """
        设置API密钥

        Args:
            provider: 提供商名称 (openai, anthropic)
            api_key: API密钥

        Returns:
            是否成功
        """
        keys = self._load_keys()

        keys[provider] = {
            "api_key": api_key,
            "masked": self._mask_key(api_key),
            "hash": self._get_key_hash(api_key),
            "updated_at": str(Path.ctime(self.storage_path))
        }

        self._save_keys(keys)
        return True

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        获取API密钥

        Args:
            provider: 提供商名称

        Returns:
            API密钥，如果不存在则返回None
        """
        keys = self._load_keys()
        provider_data = keys.get(provider)

        if provider_data:
            return provider_data.get("api_key")

        return None

    def get_masked_key(self, provider: str) -> Optional[str]:
        """
        获取掩码后的API密钥

        Args:
            provider: 提供商名称

        Returns:
            掩码后的密钥，如果不存在则返回None
        """
        keys = self._load_keys()
        provider_data = keys.get(provider)

        if provider_data:
            return provider_data.get("masked")

        return None

    def has_api_key(self, provider: str) -> bool:
        """
        检查是否有API密钥

        Args:
            provider: 提供商名称

        Returns:
            是否有密钥
        """
        return self.get_api_key(provider) is not None

    def delete_api_key(self, provider: str) -> bool:
        """
        删除API密钥

        Args:
            provider: 提供商名称

        Returns:
            是否成功
        """
        keys = self._load_keys()

        if provider in keys:
            del keys[provider]
            self._save_keys(keys)
            return True

        return False

    def list_providers(self) -> list:
        """
        列出所有已配置密钥的提供商

        Returns:
            提供商名称列表
        """
        keys = self._load_keys()
        return list(keys.keys())

    def validate_key_format(self, provider: str, api_key: str) -> tuple[bool, str]:
        """
        验证API密钥格式

        Args:
            provider: 提供商名称
            api_key: API密钥

        Returns:
            (是否有效, 错误消息)
        """
        if not api_key or not api_key.strip():
            return False, "API密钥不能为空"

        api_key = api_key.strip()

        if provider == "openai":
            # OpenAI密钥格式：sk-开头，后面是48-51位字符
            if not api_key.startswith("sk-"):
                return False, "OpenAI API密钥应以 'sk-' 开头"
            if len(api_key) < 20:
                return False, "OpenAI API密钥长度不足"
            return True, ""

        elif provider == "anthropic":
            # Anthropic密钥格式：sk-ant-开头
            if not api_key.startswith("sk-ant-"):
                return False, "Anthropic API密钥应以 'sk-ant-' 开头"
            if len(api_key) < 20:
                return False, "Anthropic API密钥长度不足"
            return True, ""

        else:
            return False, f"未知提供商: {provider}"

    def get_provider_display_name(self, provider: str) -> str:
        """
        获取提供商的显示名称

        Args:
            provider: 提供商代码

        Returns:
            显示名称
        """
        display_names = {
            "openai": "OpenAI",
            "anthropic": "Anthropic (Claude)",
        }
        return display_names.get(provider, provider)

    def get_provider_models(self, provider: str) -> list:
        """
        获取提供商支持的模型列表

        Args:
            provider: 提供商代码

        Returns:
            模型列表
        """
        from config import SUPPORTED_LLM_PROVIDERS
        return SUPPORTED_LLM_PROVIDERS.get(provider, {}).get("models", [])

    def get_default_model(self, provider: str) -> str:
        """
        获取提供商的默认模型

        Args:
            provider: 提供商代码

        Returns:
            默认模型名称
        """
        from config import SUPPORTED_LLM_PROVIDERS
        return SUPPORTED_LLM_PROVIDERS.get(provider, {}).get("default_model", "")

    # Alias for backward compatibility
    def save_api_key(self, provider: str, api_key: str) -> bool:
        """保存API密钥（set_api_key的别名）"""
        return self.set_api_key(provider, api_key)
