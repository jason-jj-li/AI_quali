"""
AI辅助质性研究平台 - 主题模块
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from src.utils.database import get_db


@dataclass
class ThemeSuggestion:
    """主题建议数据类"""
    name: str
    description: str
    definition: str
    suggested_codes: List[Dict[str, Any]]  # [{"code_id": "...", "relevance_score": 0.9, "reason": "..."}]
    confidence: float
    representative_quotes: List[Dict[str, Any]] = None


class ThemeManager:
    """主题管理类"""

    def __init__(self):
        self.db = get_db()

    def create_theme(self, project_id: str, name: str, description: str = "",
                     definition: str = "", created_by: str = 'human') -> Dict:
        """
        创建新主题

        Args:
            project_id: 项目ID
            name: 主题名称
            description: 主题描述
            definition: 主题的学术性定义
            created_by: 创建者（human/ai）

        Returns:
            创建的主题信息
        """
        theme_id = self.db.create_theme(
            project_id=project_id,
            name=name,
            description=description,
            definition=definition,
            created_by=created_by
        )

        return self.db.get_theme(theme_id)

    def get_theme(self, theme_id: str) -> Optional[Dict]:
        """获取主题详情"""
        theme = self.db.get_theme(theme_id)
        if theme:
            # 添加关联编码统计
            theme['codes'] = self.get_theme_codes_with_stats(theme_id)
            theme['code_count'] = len(theme['codes'])

            # 计算编码实例总数
            total_coding_count = sum(code.get('coding_count', 0) for code in theme['codes'])
            theme['coding_count'] = total_coding_count

            # 计算涉及文档数
            documents = set()
            for code in theme['codes']:
                if code.get('document_count'):
                    documents.add(code['document_count'])
            theme['document_count'] = len(documents)

        return theme

    def list_themes(self, project_id: str) -> List[Dict]:
        """列出项目的所有主题"""
        return self.db.list_themes(project_id)

    def update_theme(self, theme_id: str, **kwargs) -> bool:
        """
        更新主题信息

        Args:
            theme_id: 主题ID
            **kwargs: 要更新的字段（name, description, definition）

        Returns:
            是否成功
        """
        try:
            self.db.update_theme(theme_id, **kwargs)
            return True
        except Exception:
            return False

    def delete_theme(self, theme_id: str) -> bool:
        """删除主题"""
        try:
            self.db.delete_theme(theme_id)
            return True
        except Exception:
            return False

    def get_theme_codes(self, theme_id: str) -> List[Dict]:
        """获取主题关联的所有编码"""
        return self.db.get_theme_codes(theme_id)

    def get_theme_codes_with_stats(self, theme_id: str) -> List[Dict]:
        """获取主题关联的编码及统计信息"""
        return self.db.get_theme_codes_with_stats(theme_id)

    def get_theme_stats(self, project_id: str) -> Dict:
        """
        获取项目的主题统计信息

        Returns:
            包含主题数量、编码关联等统计信息的字典
        """
        themes = self.db.list_themes(project_id)

        # 计算总关联数
        total_associations = sum(theme['code_count'] for theme in themes)

        # 计算平均每个主题的编码数
        avg_codes = total_associations / len(themes) if themes else 0

        return {
            'total_themes': len(themes),
            'total_associations': total_associations,
            'avg_codes_per_theme': avg_codes,
            'themes': themes
        }


class ThemeAssociator:
    """主题关联管理类"""

    def __init__(self):
        self.db = get_db()

    def add_code_to_theme(self, theme_id: str, code_id: str,
                          relevance_score: float = 1.0) -> bool:
        """
        将编码关联到主题

        Args:
            theme_id: 主题ID
            code_id: 编码ID
            relevance_score: 关联强度评分（0-1）

        Returns:
            是否成功
        """
        try:
            self.db.add_code_to_theme(theme_id, code_id, relevance_score)
            return True
        except Exception:
            return False

    def remove_code_from_theme(self, theme_id: str, code_id: str) -> bool:
        """
        从主题中移除编码

        Args:
            theme_id: 主题ID
            code_id: 编码ID

        Returns:
            是否成功
        """
        try:
            self.db.remove_code_from_theme(theme_id, code_id)
            return True
        except Exception:
            return False

    def get_associations(self, project_id: str) -> List[Dict]:
        """
        获取项目的所有主题-编码关联

        Returns:
            关联列表，包含主题ID、编码ID、关联强度等
        """
        return self.db.get_theme_code_associations(project_id)

    def batch_associate_codes(self, theme_id: str,
                              code_associations: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        批量关联编码到主题

        Args:
            theme_id: 主题ID
            code_associations: 编码关联列表
                [{"code_id": "...", "relevance_score": 0.9}, ...]

        Returns:
            每个编码的关联结果 {code_id: success}
        """
        results = {}
        for assoc in code_associations:
            code_id = assoc.get('code_id')
            relevance_score = assoc.get('relevance_score', 1.0)
            results[code_id] = self.add_code_to_theme(theme_id, code_id, relevance_score)
        return results

    def get_unassociated_codes(self, project_id: str, theme_id: str) -> List[Dict]:
        """
        获取项目中未关联到指定主题的编码

        Args:
            project_id: 项目ID
            theme_id: 主题ID

        Returns:
            未关联的编码列表
        """
        # 获取项目所有编码
        all_codes = self.db.list_codes(project_id)

        # 获取主题已关联的编码
        associated_codes = self.db.get_theme_codes(theme_id)
        associated_code_ids = {code['id'] for code in associated_codes}

        # 返回未关联的编码
        return [code for code in all_codes if code['id'] not in associated_code_ids]


class ThemeQuoteManager:
    """典型引用管理类"""

    def __init__(self):
        self.db = get_db()

    def create_quote(self, theme_id: str, coding_id: str, quote_type: str,
                     reason: str = None, created_by: str = 'ai') -> Dict:
        """
        创建主题典型引用

        Args:
            theme_id: 主题ID
            coding_id: 编码实例ID
            quote_type: 引用类型（supporting/deviant/borderline）
            reason: 选择理由
            created_by: 创建者（human/ai）

        Returns:
            创建的引用信息
        """
        quote_id = self.db.create_theme_quote(
            theme_id=theme_id,
            coding_id=coding_id,
            quote_type=quote_type,
            reason=reason,
            created_by=created_by
        )

        # 获取完整的引用信息
        quotes = self.db.get_theme_quotes(theme_id)
        for quote in quotes:
            if quote['id'] == quote_id:
                return quote

        return {'id': quote_id}

    def get_theme_quotes(self, theme_id: str, quote_type: str = None) -> List[Dict]:
        """
        获取主题的典型引用

        Args:
            theme_id: 主题ID
            quote_type: 引用类型（可选，不指定则返回所有类型）

        Returns:
            引用列表
        """
        return self.db.get_theme_quotes(theme_id, quote_type)

    def delete_quote(self, quote_id: str) -> bool:
        """删除典型引用"""
        try:
            self.db.delete_theme_quote(quote_id)
            return True
        except Exception:
            return False

    def get_quotes_by_type(self, theme_id: str) -> Dict[str, List[Dict]]:
        """
        按类型获取主题的典型引用

        Args:
            theme_id: 主题ID

        Returns:
            按类型分组的引用 {quote_type: [quotes]}
        """
        all_quotes = self.db.get_theme_quotes(theme_id)

        result = {
            'supporting': [],
            'deviant': [],
            'borderline': []
        }

        for quote in all_quotes:
            quote_type = quote.get('quote_type', 'supporting')
            if quote_type in result:
                result[quote_type].append(quote)

        return result


# 全局主题管理器实例
_theme_manager = None
_theme_associator = None
_theme_quote_manager = None


def get_theme_manager() -> ThemeManager:
    """获取主题管理器实例"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def get_theme_associator() -> ThemeAssociator:
    """获取主题关联管理器实例"""
    global _theme_associator
    if _theme_associator is None:
        _theme_associator = ThemeAssociator()
    return _theme_associator


def get_theme_quote_manager() -> ThemeQuoteManager:
    """获取典型引用管理器实例"""
    global _theme_quote_manager
    if _theme_quote_manager is None:
        _theme_quote_manager = ThemeQuoteManager()
    return _theme_quote_manager
