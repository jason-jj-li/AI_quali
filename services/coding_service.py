# -*- coding: utf-8 -*-
"""
QualInsight Coding Service
编码业务逻辑层
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import json
import re


@dataclass
class Code:
    """
    编码数据类
    """
    id: str
    name: str
    description: str
    quotes: List[Dict[str, Any]]
    parent_id: Optional[str] = None
    color: str = "#FF5733"
    created_at: str = ""
    confidence: float = 0.0
    reasoning: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Code':
        """从字典创建"""
        return cls(**data)


class CodingService:
    """
    编码服务

    职责：
    - 编码的 CRUD 操作
    - 编码层级管理
    - 编码统计分析
    - AI 辅助编码
    """

    def __init__(self):
        self._codes: List[Code] = []

    def create_code(
        self,
        name: str,
        description: str,
        quotes: List[Dict[str, Any]],
        parent_id: Optional[str] = None,
        color: str = "#FF5733",
        confidence: float = 0.0,
        reasoning: str = ""
    ) -> Code:
        """
        创建新编码

        Args:
            name: 编码名称
            description: 编码描述
            quotes: 引用列表
            parent_id: 父编码 ID
            color: 颜色
            confidence: 置信度
            reasoning: 推理说明

        Returns:
            创建的编码
        """
        import uuid
        from datetime import datetime

        code = Code(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            quotes=quotes,
            parent_id=parent_id,
            color=color,
            created_at=datetime.now().isoformat(),
            confidence=confidence,
            reasoning=reasoning
        )

        self._codes.append(code)
        return code

    def get_code(self, code_id: str) -> Optional[Code]:
        """
        获取指定编码

        Args:
            code_id: 编码 ID

        Returns:
            找到的编码对象，不存在则返回 None

        Examples:
            >>> service = CodingService()
            >>> code = service.get_code("code-123")
            >>> if code:
            ...     print(code.name)
        """
        for code in self._codes:
            if code.id == code_id:
                return code
        return None

    def update_code(self, code_id: str, **kwargs) -> Optional[Code]:
        """
        更新编码属性

        Args:
            code_id: 编码 ID
            **kwargs: 要更新的属性键值对，可选:
                - name: 编码名称
                - description: 编码描述
                - color: 颜色值
                - confidence: 置信度
                - reasoning: 推理说明

        Returns:
            更新后的编码对象，编码不存在则返回 None

        Examples:
            >>> service = CodingService()
            >>> code = service.update_code("code-123", name="New Name", color="#FF0000")
        """
        code = self.get_code(code_id)
        if code:
            for key, value in kwargs.items():
                if hasattr(code, key):
                    setattr(code, key, value)
        return code

    def delete_code(self, code_id: str) -> bool:
        """
        删除编码及其所有子编码

        Args:
            code_id: 编码 ID

        Returns:
            是否成功删除

        Note:
            删除编码时会同时删除所有以该编码为父级的子编码
        """
        code = self.get_code(code_id)
        if code:
            self._codes.remove(code)
            # 同时删除子编码
            self._codes = [c for c in self._codes if c.parent_id != code_id]
            return True
        return False

    def list_codes(self, parent_id: Optional[str] = None) -> List[Code]:
        """
        列出编码

        Args:
            parent_id: 父编码 ID，None 表示获取顶级编码

        Returns:
            编码列表
        """
        if parent_id is None:
            return [c for c in self._codes if c.parent_id is None]
        return [c for c in self._codes if c.parent_id == parent_id]

    def get_all_codes(self) -> List[Code]:
        """
        获取所有编码（包含副本）

        Returns:
            所有编码的列表副本

        Note:
            返回的是副本，修改返回值不会影响内部存储
        """
        return self._codes.copy()

    def get_code_hierarchy(self) -> List[Dict[str, Any]]:
        """
        获取编码层级结构

        Returns:
            层级结构列表，每个节点包含:
                - code: 编码数据字典
                - children: 子编码列表

        Examples:
            >>> service = CodingService()
            >>> hierarchy = service.get_code_hierarchy()
            >>> for node in hierarchy:
            ...     print(node['code']['name'])
        """
        def build_tree(parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
            tree = []
            for code in self.list_codes(parent_id):
                node = {
                    "code": code.to_dict(),
                    "children": build_tree(code.id)
                }
                tree.append(node)
            return tree

        return build_tree()

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取编码统计信息

        Returns:
            统计信息字典，包含:
                - total_codes: 总编码数
                - top_level_codes: 顶级编码数
                - total_quotes: 总引用数
                - avg_quotes_per_code: 平均每编码引用数
                - avg_confidence: 平均置信度
                - color_distribution: 颜色分布
                - max_depth: 最大层级深度
        """
        total_codes = len(self._codes)
        top_level_codes = len(self.list_codes())
        total_quotes = sum(len(c.quotes) for c in self._codes)

        # 计算平均置信度
        confidences = [c.confidence for c in self._codes if c.confidence > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # 编码颜色分布
        color_distribution = {}
        for code in self._codes:
            color_distribution[code.color] = color_distribution.get(code.color, 0) + 1

        return {
            "total_codes": total_codes,
            "top_level_codes": top_level_codes,
            "total_quotes": total_quotes,
            "avg_quotes_per_code": total_quotes / total_codes if total_codes > 0 else 0,
            "avg_confidence": avg_confidence,
            "color_distribution": color_distribution,
            "max_depth": self._get_max_depth()
        }

    def _get_max_depth(self, parent_id: Optional[str] = None, current_depth: int = 0) -> int:
        """
        计算编码树的最大深度（私有方法）

        Args:
            parent_id: 父编码 ID
            current_depth: 当前深度

        Returns:
            从当前节点的最大深度
        """
        children = self.list_codes(parent_id)
        if not children:
            return current_depth
        return max(self._get_max_depth(c.id, current_depth + 1) for c in children)

    def merge_codes(self, source_ids: List[str], target_name: str, target_description: str) -> Optional[Code]:
        """
        合并多个编码为一个新编码

        Args:
            source_ids: 要合并的编码 ID 列表
            target_name: 新编码名称
            target_description: 新编码描述

        Returns:
            合并后的新编码，源编码不存在则返回 None

        Note:
            - 合并后会删除所有源编码
            - 新编码包含所有源编码的引用
            - 新编码不继承父子关系，成为顶级编码
        """
        import uuid
        from datetime import datetime

        # 收集所有引用
        all_quotes = []
        for code_id in source_ids:
            code = self.get_code(code_id)
            if code:
                all_quotes.extend(code.quotes)

        # 创建新编码
        new_code = Code(
            id=str(uuid.uuid4()),
            name=target_name,
            description=target_description,
            quotes=all_quotes,
            created_at=datetime.now().isoformat()
        )

        # 删除旧编码
        for code_id in source_ids:
            self.delete_code(code_id)

        self._codes.append(new_code)
        return new_code

    def split_code(
        self,
        source_id: str,
        first_name: str,
        first_description: str,
        second_name: str,
        second_description: str,
        first_quotes: List[Dict[str, Any]],
        second_quotes: List[Dict[str, Any]]
    ) -> tuple[Optional[Code], Optional[Code]]:
        """
        拆分编码

        Args:
            source_id: 要拆分的编码 ID
            first_name: 第一个编码名称
            first_description: 第一个编码描述
            second_name: 第二个编码名称
            second_description: 第二个编码描述
            first_quotes: 第一个编码的引用
            second_quotes: 第二个编码的引用

        Returns:
            (新编码1, 新编码2)
        """
        # 删除原编码
        original = self.get_code(source_id)
        parent_id = original.parent_id if original else None
        self.delete_code(source_id)

        # 创建两个新编码
        code1 = self.create_code(
            name=first_name,
            description=first_description,
            quotes=first_quotes,
            parent_id=parent_id
        )

        code2 = self.create_code(
            name=second_name,
            description=second_description,
            quotes=second_quotes,
            parent_id=parent_id
        )

        return code1, code2

    def search_codes(self, query: str) -> List[Code]:
        """
        搜索编码

        Args:
            query: 搜索关键词

        Returns:
            匹配的编码列表
        """
        query_lower = query.lower()
        results = []

        for code in self._codes:
            if (query_lower in code.name.lower() or
                query_lower in code.description.lower() or
                any(query_lower in str(q).lower() for q in code.quotes)):
                results.append(code)

        return results

    def export_codes(self, format: str = "json") -> str:
        """
        导出编码为指定格式

        Args:
            format: 导出格式，支持:
                - "json": JSON 格式
                - "csv": CSV 格式

        Returns:
            导出内容的字符串

        Raises:
            ValueError: 不支持的导出格式

        Examples:
            >>> service = CodingService()
            >>> json_export = service.export_codes("json")
            >>> csv_export = service.export_codes("csv")
        """
        if format == "json":
            return json.dumps([c.to_dict() for c in self._codes], ensure_ascii=False, indent=2)
        elif format == "csv":
            import csv
            from io import StringIO

            output = StringIO()
            writer = csv.writer(output)

            # 写入表头
            writer.writerow(["ID", "Name", "Description", "Parent ID", "Quotes Count", "Color"])

            # 写入数据
            for code in self._codes:
                writer.writerow([
                    code.id,
                    code.name,
                    code.description,
                    code.parent_id or "",
                    len(code.quotes),
                    code.color
                ])

            return output.getvalue()

        raise ValueError(f"Unsupported format: {format}")

    def load_codes(self, data: List[Dict[str, Any]]) -> int:
        """
        从字典列表加载编码

        Args:
            data: 编码数据列表，每个字典包含 Code 所需的字段

        Returns:
            成功加载的编码数量

        Note:
            无效的编码数据会被跳过，不会抛出异常
        """
        count = 0
        for item in data:
            try:
                code = Code.from_dict(item)
                self._codes.append(code)
                count += 1
            except Exception:
                continue
        return count
