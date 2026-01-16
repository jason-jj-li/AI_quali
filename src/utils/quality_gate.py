"""
质量检查门控框架
参考scientific-skills的质量检查机制
实现编码质量的多维度检查和报告
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class QualityStatus(Enum):
    """质量状态"""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class QualityCheckResult:
    """质量检查结果"""
    check_name: str
    status: QualityStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class QualityReport:
    """质量报告"""
    project_id: str
    project_name: str
    check_results: List[QualityCheckResult]
    overall_status: QualityStatus
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    summary: Dict[str, Any] = field(default_factory=dict)

    def get_passed_checks(self) -> List[QualityCheckResult]:
        """获取通过的检查"""
        return [r for r in self.check_results if r.status == QualityStatus.PASSED]

    def get_failed_checks(self) -> List[QualityCheckResult]:
        """获取失败的检查"""
        return [r for r in self.check_results if r.status == QualityStatus.FAILED]

    def get_warning_checks(self) -> List[QualityCheckResult]:
        """获取警告的检查"""
        return [r for r in self.check_results if r.status == QualityStatus.WARNING]

    def get_score(self) -> float:
        """
        计算质量分数 (0-1)

        Returns:
            质量分数
        """
        if not self.check_results:
            return 0.0

        passed = len(self.get_passed_checks())
        warnings = len(self.get_warning_checks())
        total = len(self.check_results)

        # 通过得1分，警告得0.5分，失败得0分
        score = (passed + 0.5 * warnings) / total
        return round(score, 2)


class QualityGate(ABC):
    """
    质量检查门控基类

    所有质量检查都应继承此类并实现check方法
    """

    def __init__(self, name: str, description: str = ""):
        """
        初始化质量检查

        Args:
            name: 检查名称
            description: 检查描述
        """
        self.name = name
        self.description = description

    @abstractmethod
    def check(self, project_id: str, **kwargs) -> QualityCheckResult:
        """
        执行质量检查

        Args:
            project_id: 项目ID
            **kwargs: 其他参数

        Returns:
            质量检查结果
        """
        pass

    def _pass(self, message: str, details: Dict[str, Any] = None) -> QualityCheckResult:
        """创建通过结果"""
        return QualityCheckResult(
            check_name=self.name,
            status=QualityStatus.PASSED,
            message=message,
            details=details or {}
        )

    def _fail(self, message: str, details: Dict[str, Any] = None, suggestions: List[str] = None) -> QualityCheckResult:
        """创建失败结果"""
        return QualityCheckResult(
            check_name=self.name,
            status=QualityStatus.FAILED,
            message=message,
            details=details or {},
            suggestions=suggestions or []
        )

    def _warn(self, message: str, details: Dict[str, Any] = None, suggestions: List[str] = None) -> QualityCheckResult:
        """创建警告结果"""
        return QualityCheckResult(
            check_name=self.name,
            status=QualityStatus.WARNING,
            message=message,
            details=details or {},
            suggestions=suggestions or []
        )


class CodingConsistencyCheck(QualityGate):
    """编码一致性检查"""

    def __init__(self):
        super().__init__(
            name="编码一致性检查",
            description="检查编码应用的一致性，识别不一致的编码应用"
        )

    def check(self, project_id: str, **kwargs) -> QualityCheckResult:
        """
        检查编码一致性

        Args:
            project_id: 项目ID
            **kwargs: coding_manager (必需)

        Returns:
            质量检查结果
        """
        from src.coding import get_coding_manager

        coding_manager = kwargs.get("coding_manager") or get_coding_manager()

        # 获取所有编码
        codes = coding_manager.list_codes(project_id, include_stats=True)

        if not codes:
            return self._warn("项目没有编码，跳过一致性检查")

        # 检查每个编码的使用情况
        inconsistent_codes = []
        for code in codes:
            # 检查编码使用率
            usage_count = code.get("usage_count", 0)
            if usage_count == 0:
                inconsistent_codes.append({
                    "code": code["name"],
                    "issue": "未使用的编码"
                })

        if inconsistent_codes:
            return self._warn(
                f"发现 {len(inconsistent_codes)} 个编码可能存在一致性问题",
                details={"inconsistent_codes": inconsistent_codes},
                suggestions=[
                    "删除未使用的编码或添加相应的内容",
                    "检查编码定义是否清晰",
                    "考虑合并相似的编码"
                ]
            )

        return self._pass(
            f"所有 {len(codes)} 个编码使用一致",
            details={"total_codes": len(codes)}
        )


class CodingCoverageCheck(QualityGate):
    """编码覆盖率检查"""

    def __init__(self):
        super().__init__(
            name="编码覆盖率检查",
            description="检查文档的编码覆盖率，识别未编码的内容"
        )

    def check(self, project_id: str, **kwargs) -> QualityCheckResult:
        """
        检查编码覆盖率

        Args:
            project_id: 项目ID
            **kwargs: document_manager, coding_manager (必需)

        Returns:
            质量检查结果
        """
        from src.document import get_document_manager
        from src.coding import get_coding_manager

        document_manager = kwargs.get("document_manager") or get_document_manager()
        coding_manager = kwargs.get("coding_manager") or get_coding_manager()

        # 获取所有文档
        documents = document_manager.list_documents(project_id)

        if not documents:
            return self._warn("项目没有文档，跳过覆盖率检查")

        # 计算每个文档的编码覆盖率
        coverage_data = []
        total_chars = 0
        coded_chars = 0

        for doc in documents:
            doc_id = doc["id"]
            content = doc.get("content", "")
            doc_length = len(content)

            if doc_length == 0:
                continue

            # 获取该文档的所有编码
            codings = coding_manager.get_document_codings(doc_id)

            # 计算编码覆盖的字符数
            coded_length = sum(
                c["end_pos"] - c["start_pos"]
                for c in codings
            )

            coverage_rate = coded_length / doc_length if doc_length > 0 else 0

            coverage_data.append({
                "document_id": doc_id,
                "filename": doc["filename"],
                "total_chars": doc_length,
                "coded_chars": coded_length,
                "coverage_rate": coverage_rate
            })

            total_chars += doc_length
            coded_chars += coded_length

        # 计算总体覆盖率
        overall_coverage = coded_chars / total_chars if total_chars > 0 else 0

        # 判断质量状态
        if overall_coverage >= 0.5:
            return self._pass(
                f"编码覆盖率良好: {overall_coverage:.1%}",
                details={
                    "overall_coverage": overall_coverage,
                    "total_documents": len(documents),
                    "coverage_data": coverage_data
                }
            )
        elif overall_coverage >= 0.3:
            return self._warn(
                f"编码覆盖率较低: {overall_coverage:.1%}，建议继续编码",
                details={
                    "overall_coverage": overall_coverage,
                    "total_documents": len(documents),
                    "coverage_data": coverage_data
                },
                suggestions=[
                    "继续对文档进行编码",
                    "使用AI辅助编码功能提高效率",
                    "优先编码关键内容"
                ]
            )
        else:
            return self._fail(
                f"编码覆盖率过低: {overall_coverage:.1%}，需要大量编码工作",
                details={
                    "overall_coverage": overall_coverage,
                    "total_documents": len(documents),
                    "coverage_data": coverage_data
                },
                suggestions=[
                    "开始系统性的编码工作",
                    "考虑使用AI辅助编码",
                    "建立编码本框架"
                ]
            )


class RedundantCodeCheck(QualityGate):
    """冗余编码检查"""

    def __init__(self):
        super().__init__(
            name="冗余编码检查",
            description="检测相似或冗余的编码"
        )

    def check(self, project_id: str, **kwargs) -> QualityCheckResult:
        """
        检查冗余编码

        Args:
            project_id: 项目ID
            **kwargs: coding_manager (必需)

        Returns:
            质量检查结果
        """
        from src.coding import get_coding_manager

        coding_manager = kwargs.get("coding_manager") or get_coding_manager()

        # 获取所有编码
        codes = coding_manager.list_codes(project_id)

        if len(codes) < 2:
            return self._pass("编码数量过少，无需检查冗余")

        # 简单的相似度检测：名称相似或描述相似
        redundant_pairs = []
        for i, code1 in enumerate(codes):
            for code2 in codes[i + 1:]:
                # 检查名称相似度（简单检查：一个名称包含另一个）
                name1 = code1["name"].lower()
                name2 = code2["name"].lower()

                if name1 in name2 or name2 in name1:
                    if name1 != name2:  # 排除完全相同的
                        redundant_pairs.append({
                            "code1": code1["name"],
                            "code2": code2["name"],
                            "reason": "名称相似"
                        })

        if redundant_pairs:
            return self._warn(
                f"发现 {len(redundant_pairs)} 对可能的冗余编码",
                details={"redundant_pairs": redundant_pairs},
                suggestions=[
                    "考虑合并相似的编码",
                    "明确每个编码的边界",
                    "删除不必要的编码"
                ]
            )

        return self._pass(
            f"未发现明显的冗余编码",
            details={"total_codes": len(codes)}
        )


class UnusedCodeCheck(QualityGate):
    """未使用编码检查"""

    def __init__(self):
        super().__init__(
            name="未使用编码检查",
            description="检测从未使用的编码"
        )

    def check(self, project_id: str, **kwargs) -> QualityCheckResult:
        """
        检查未使用的编码

        Args:
            project_id: 项目ID
            **kwargs: coding_manager (必需)

        Returns:
            质量检查结果
        """
        from src.coding import get_coding_manager

        coding_manager = kwargs.get("coding_manager") or get_coding_manager()

        # 获取编码统计
        stats = coding_manager.get_coding_stats(project_id)
        unused_codes = stats.get("unused_codes", [])

        if unused_codes:
            return self._warn(
                f"发现 {len(unused_codes)} 个未使用的编码",
                details={
                    "unused_codes": [c["name"] for c in unused_codes],
                    "total_codes": stats["total_codes"]
                },
                suggestions=[
                    "删除未使用的编码",
                    "或为这些编码添加相应的内容",
                    "检查这些编码是否真的需要"
                ]
            )

        return self._pass(
            "所有编码都已使用",
            details={"total_codes": stats["total_codes"]}
        )


class QualityGateRegistry:
    """
    质量检查注册表

    管理所有可用的质量检查
    """

    def __init__(self):
        self._checks: Dict[str, type] = {}
        self._register_default_checks()

    def _register_default_checks(self):
        """注册默认的质量检查"""
        self.register("coding_consistency", CodingConsistencyCheck)
        self.register("coding_coverage", CodingCoverageCheck)
        self.register("redundant_code", RedundantCodeCheck)
        self.register("unused_code", UnusedCodeCheck)

    def register(self, name: str, check_class: type):
        """
        注册质量检查

        Args:
            name: 检查名称
            check_class: 检查类（必须继承QualityGate）
        """
        if not issubclass(check_class, QualityGate):
            raise ValueError(f"{check_class} 必须继承 QualityGate")

        self._checks[name] = check_class

    def get_check(self, name: str) -> Optional[QualityGate]:
        """
        获取质量检查实例

        Args:
            name: 检查名称

        Returns:
            质量检查实例，如果不存在则返回None
        """
        check_class = self._checks.get(name)
        if check_class:
            return check_class()
        return None

    def list_checks(self) -> List[str]:
        """
        列出所有已注册的检查

        Returns:
            检查名称列表
        """
        return list(self._checks.keys())


class QualityInspector:
    """
    质量检查器

    执行质量检查并生成报告
    """

    def __init__(self, registry: Optional[QualityGateRegistry] = None):
        """
        初始化质量检查器

        Args:
            registry: 质量检查注册表，默认使用默认注册表
        """
        self.registry = registry or QualityGateRegistry()

    def inspect(
        self,
        project_id: str,
        project_name: str,
        checks: Optional[List[str]] = None,
        **kwargs
    ) -> QualityReport:
        """
        执行质量检查

        Args:
            project_id: 项目ID
            project_name: 项目名称
            checks: 要执行的检查列表，None表示执行所有检查
            **kwargs: 传递给各个检查的参数

        Returns:
            质量报告
        """
        # 确定要执行的检查
        if checks is None:
            checks = self.registry.list_checks()

        # 执行检查
        results = []
        for check_name in checks:
            check = self.registry.get_check(check_name)
            if check:
                try:
                    result = check.check(project_id, **kwargs)
                    results.append(result)
                except Exception as e:
                    # 如果检查失败，创建失败结果
                    results.append(QualityCheckResult(
                        check_name=check_name,
                        status=QualityStatus.FAILED,
                        message=f"检查执行失败: {str(e)}"
                    ))

        # 确定总体状态
        overall_status = self._determine_overall_status(results)

        # 生成摘要
        summary = self._generate_summary(results)

        return QualityReport(
            project_id=project_id,
            project_name=project_name,
            check_results=results,
            overall_status=overall_status,
            summary=summary
        )

    def _determine_overall_status(self, results: List[QualityCheckResult]) -> QualityStatus:
        """确定总体质量状态"""
        if any(r.status == QualityStatus.FAILED for r in results):
            return QualityStatus.FAILED
        elif any(r.status == QualityStatus.WARNING for r in results):
            return QualityStatus.WARNING
        elif all(r.status == QualityStatus.PASSED for r in results):
            return QualityStatus.PASSED
        else:
            return QualityStatus.SKIPPED

    def _generate_summary(self, results: List[QualityCheckResult]) -> Dict[str, Any]:
        """生成质量摘要"""
        total = len(results)
        passed = sum(1 for r in results if r.status == QualityStatus.PASSED)
        warnings = sum(1 for r in results if r.status == QualityStatus.WARNING)
        failed = sum(1 for r in results if r.status == QualityStatus.FAILED)

        return {
            "total_checks": total,
            "passed_checks": passed,
            "warning_checks": warnings,
            "failed_checks": failed,
            "quality_score": round((passed + 0.5 * warnings) / total, 2) if total > 0 else 0.0
        }


def get_quality_inspector() -> QualityInspector:
    """
    获取质量检查器实例

    Returns:
        QualityInspector实例
    """
    return QualityInspector()
