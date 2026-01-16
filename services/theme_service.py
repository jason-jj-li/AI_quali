# -*- coding: utf-8 -*-
"""
QualInsight Theme Service
主题分析业务逻辑层
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import json
from datetime import datetime
import uuid


@dataclass
class Theme:
    """
    主题数据类
    """
    id: str
    name: str
    definition: str
    supporting_quotes: List[Dict[str, Any]]
    related_codes: List[str]
    parent_id: Optional[str] = None
    color: str = "#33FF57"
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Theme':
        """从字典创建"""
        return cls(**data)


@dataclass
class ThemeRelationship:
    """主题关系数据类"""
    source_id: str
    target_id: str
    relationship_type: str  # complementary, opposing, causal, hierarchical
    description: str = ""


class ThemeService:
    """
    主题服务

    职责：
    - 主题的 CRUD 操作
    - 主题层级管理
    - 主题关系分析
    - 主题统计
    """

    def __init__(self):
        self._themes: List[Theme] = []
        self._relationships: List[ThemeRelationship] = []

    def create_theme(
        self,
        name: str,
        definition: str,
        supporting_quotes: List[Dict[str, Any]],
        related_codes: List[str],
        parent_id: Optional[str] = None,
        color: str = "#33FF57"
    ) -> Theme:
        """
        创建新主题

        Args:
            name: 主题名称
            definition: 主题定义
            supporting_quotes: 支持性引用
            related_codes: 相关编码 ID 列表
            parent_id: 父主题 ID
            color: 颜色

        Returns:
            创建的主题
        """
        theme = Theme(
            id=str(uuid.uuid4()),
            name=name,
            definition=definition,
            supporting_quotes=supporting_quotes,
            related_codes=related_codes,
            parent_id=parent_id,
            color=color,
            created_at=datetime.now().isoformat()
        )

        self._themes.append(theme)
        return theme

    def get_theme(self, theme_id: str) -> Optional[Theme]:
        """
        获取指定主题

        Args:
            theme_id: 主题 ID

        Returns:
            找到的主题对象，不存在则返回 None
        """
        for theme in self._themes:
            if theme.id == theme_id:
                return theme
        return None

    def update_theme(self, theme_id: str, **kwargs) -> Optional[Theme]:
        """
        更新主题属性

        Args:
            theme_id: 主题 ID
            **kwargs: 要更新的属性键值对

        Returns:
            更新后的主题对象，主题不存在则返回 None
        """
        theme = self.get_theme(theme_id)
        if theme:
            for key, value in kwargs.items():
                if hasattr(theme, key):
                    setattr(theme, key, value)
        return theme

    def delete_theme(self, theme_id: str) -> bool:
        """
        删除主题及其所有子主题和相关关系

        Args:
            theme_id: 主题 ID

        Returns:
            是否成功删除

        Note:
            删除主题时会同时删除:
            - 所有以该主题为父级的子主题
            - 所有与该主题相关的关系
        """
        theme = self.get_theme(theme_id)
        if theme:
            self._themes.remove(theme)
            # 删除子主题
            self._themes = [t for t in self._themes if t.parent_id != theme_id]
            # 删除相关关系
            self._relationships = [
                r for r in self._relationships
                if r.source_id != theme_id and r.target_id != theme_id
            ]
            return True
        return False

    def list_themes(self, parent_id: Optional[str] = None) -> List[Theme]:
        """
        列出主题

        Args:
            parent_id: 父主题 ID，None 表示获取顶级主题

        Returns:
            主题列表
        """
        if parent_id is None:
            return [t for t in self._themes if t.parent_id is None]
        return [t for t in self._themes if t.parent_id == parent_id]

    def get_all_themes(self) -> List[Theme]:
        """
        获取所有主题（包含副本）

        Returns:
            所有主题的列表副本

        Note:
            返回的是副本，修改返回值不会影响内部存储
        """
        return self._themes.copy()

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        description: str = ""
    ) -> ThemeRelationship:
        """
        添加主题关系

        Args:
            source_id: 源主题 ID
            target_id: 目标主题 ID
            relationship_type: 关系类型，支持:
                - "complementary": 互补关系
                - "opposing": 对立关系
                - "causal": 因果关系
                - "hierarchical": 层级关系
            description: 关系描述

        Returns:
            创建的主题关系对象

        Examples:
            >>> service = ThemeService()
            >>> rel = service.add_relationship(
            ...     "theme-1", "theme-2", "causal", "主题1导致主题2"
            ... )
        """
        relationship = ThemeRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            description=description
        )

        self._relationships.append(relationship)
        return relationship

    def get_relationships(self, theme_id: Optional[str] = None) -> List[ThemeRelationship]:
        """
        获取主题关系

        Args:
            theme_id: 主题 ID，None 表示获取所有关系

        Returns:
            关系列表。指定 theme_id 时返回与该主题相关的所有关系
        """
        if theme_id is None:
            return self._relationships.copy()

        return [
            r for r in self._relationships
            if r.source_id == theme_id or r.target_id == theme_id
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取主题统计信息

        Returns:
            统计信息字典，包含:
                - total_themes: 总主题数
                - top_level_themes: 顶级主题数
                - total_relationships: 总关系数
                - relationship_types: 关系类型分布
                - avg_quotes_per_theme: 平均每主题引用数
                - max_depth: 最大层级深度
        """
        total_themes = len(self._themes)
        top_level_themes = len(self.list_themes())
        total_relationships = len(self._relationships)

        # 关系类型分布
        relationship_types = {}
        for r in self._relationships:
            relationship_types[r.relationship_type] = relationship_types.get(r.relationship_type, 0) + 1

        # 计算每个主题的平均引用数
        quotes_per_theme = [
            len(t.supporting_quotes) for t in self._themes if t.supporting_quotes
        ]
        avg_quotes = sum(quotes_per_theme) / len(quotes_per_theme) if quotes_per_theme else 0

        return {
            "total_themes": total_themes,
            "top_level_themes": top_level_themes,
            "total_relationships": total_relationships,
            "relationship_types": relationship_types,
            "avg_quotes_per_theme": avg_quotes,
            "max_depth": self._get_max_depth()
        }

    def _get_max_depth(self, parent_id: Optional[str] = None, current_depth: int = 0) -> int:
        """
        计算主题树的最大深度（私有方法）

        Args:
            parent_id: 父主题 ID
            current_depth: 当前深度

        Returns:
            从当前节点的最大深度
        """
        children = self.list_themes(parent_id)
        if not children:
            return current_depth
        return max(self._get_max_depth(c.id, current_depth + 1) for c in children)

    def export_themes(self, format: str = "json") -> str:
        """
        导出主题为指定格式

        Args:
            format: 导出格式，当前仅支持 "json"

        Returns:
            导出内容的字符串

        Raises:
            ValueError: 不支持的导出格式

        Examples:
            >>> service = ThemeService()
            >>> json_export = service.export_themes("json")
        """
        if format == "json":
            return json.dumps({
                "themes": [t.to_dict() for t in self._themes],
                "relationships": [
                    {"source": r.source_id, "target": r.target_id, "type": r.relationship_type, "description": r.description}
                    for r in self._relationships
                ]
            }, ensure_ascii=False, indent=2)

        raise ValueError(f"Unsupported format: {format}")
