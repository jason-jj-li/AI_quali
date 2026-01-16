"""
LLM基类和依赖检查模块
参考scientific-skills的依赖管理模式
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import subprocess
import sys


@dataclass
class DependencyStatus:
    """依赖状态数据类"""
    package_name: str
    installed: bool
    version: Optional[str] = None
    purpose: str = ""


@dataclass
class LLMResponse:
    """LLM响应数据类"""
    content: str
    model: str
    provider: str
    tokens_used: Dict[str, int]  # {"prompt": 100, "completion": 200}
    cost: float = 0.0
    raw_response: Any = None


@dataclass
class LLMConfig:
    """LLM配置数据类"""
    provider: str
    model: str
    api_key: str
    temperature: float = 0.3
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    base_url: Optional[str] = None  # 用于LM Studio等本地LLM服务


class LLMProvider(ABC):
    """
    LLM提供商抽象基类

    所有LLM提供商必须实现此接口，确保：
    1. 依赖检查
    2. API密钥验证
    3. 统一的调用接口
    4. 成本估算
    """

    # 子类必须定义这些类属性
    PROVIDER_NAME: str = ""
    REQUIRED_PACKAGES: List[str] = []
    SUPPORTED_MODELS: List[str] = []
    PRICING: Dict[str, Dict[str, float]] = {}  # {"model": {"input": 0.01, "output": 0.02}}

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None

    @classmethod
    def check_dependencies(cls) -> Tuple[List[DependencyStatus], bool]:
        """
        检查依赖包安装状态
        参考scientific-skills的依赖管理模式

        Returns:
            (依赖状态列表, 是否全部安装)
        """
        import re
        statuses = []
        all_installed = True

        for package in cls.REQUIRED_PACKAGES:
            # 提取纯包名（去除版本号等修饰符，如 "openai>=1.0.0" -> "openai"）
            package_name = re.split(r'[<>=!~\s]', package)[0].strip()

            # 使用pip show检查安装状态
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", package_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                installed = result.returncode == 0

                if installed:
                    # 解析版本号
                    version = None
                    for line in result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            version = line.split(':', 1)[1].strip()
                            break
                    statuses.append(DependencyStatus(
                        package_name=package,
                        installed=True,
                        version=version,
                        purpose=f"{cls.PROVIDER_NAME} LLM接口"
                    ))
                else:
                    all_installed = False
                    statuses.append(DependencyStatus(
                        package_name=package,
                        installed=False,
                        purpose=f"{cls.PROVIDER_NAME} LLM接口"
                    ))
            except Exception as e:
                all_installed = False
                statuses.append(DependencyStatus(
                    package_name=package,
                    installed=False,
                    purpose=f"{cls.PROVIDER_NAME} LLM接口"
                ))

        return statuses, all_installed

    @classmethod
    def get_missing_dependencies_info(cls) -> Optional[str]:
        """
        获取缺失依赖的安装信息
        用于向用户显示安装提示

        Returns:
            None如果全部安装，否则返回安装命令字符串
        """
        statuses, all_installed = cls.check_dependencies()

        if all_installed:
            return None

        missing = [s.package_name for s in statuses if not s.installed]

        info = f"## 依赖检查 - {cls.PROVIDER_NAME}\n\n"
        info += f"以下{cls.PROVIDER_NAME}所需的包未安装：\n\n"

        for status in statuses:
            if not status.installed:
                info += f"- **{status.package_name}**: 用于 {status.purpose}\n"

        info += f"\n安装命令：\n```bash\npip install {' '.join(missing)}\n```\n"

        return info

    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        验证API密钥是否有效

        Returns:
            密钥是否有效
        """
        pass

    @abstractmethod
    def _initialize_client(self):
        """初始化LLM客户端"""
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        生成文本响应

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数（覆盖配置）
            max_tokens: 最大token数（覆盖配置）
            **kwargs: 其他参数

        Returns:
            LLMResponse对象
        """
        pass

    @abstractmethod
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        估算API调用成本

        Args:
            prompt_tokens: 输入token数
            completion_tokens: 输出token数

        Returns:
            估算成本（美元）
        """
        pass

    def count_tokens(self, text: str) -> int:
        """
        计算文本的token数（近似值）
        默认使用简单的4字符=1token估算
        子类可以覆盖为更精确的计算

        Args:
            text: 输入文本

        Returns:
            token数估算
        """
        # 粗略估算：英文约4字符=1token，中文约2字符=1token
        # 取中间值3字符=1token
        return len(text) // 3

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        获取模型信息

        Args:
            model: 模型名称

        Returns:
            模型信息字典
        """
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(f"不支持的模型: {model}. 支持的模型: {self.SUPPORTED_MODELS}")

        pricing = self.PRICING.get(model, {})
        return {
            "name": model,
            "provider": self.PROVIDER_NAME,
            "input_price": pricing.get("input", 0),
            "output_price": pricing.get("output", 0),
        }


class LLMError(Exception):
    """LLM相关错误基类"""
    pass


class DependencyError(LLMError):
    """依赖包缺失错误"""
    def __init__(self, provider: str, missing_packages: List[str]):
        self.provider = provider
        self.missing_packages = missing_packages
        super().__init__(
            f"{provider}需要以下依赖包: {', '.join(missing_packages)}。"
            f"请运行: pip install {' '.join(missing_packages)}"
        )


class APIKeyError(LLMError):
    """API密钥错误"""
    pass


class ModelNotFoundError(LLMError):
    """模型不存在错误"""
    pass


class RateLimitError(LLMError):
    """速率限制错误"""
    pass


class TokenLimitError(LLMError):
    """Token超限错误"""
    pass
