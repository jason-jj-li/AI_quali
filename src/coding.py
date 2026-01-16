"""
AI辅助质性研究平台 - 编码模块
"""
from typing import List, Dict, Optional
import random

from src.utils.database import get_db
import config


class CodingManager:
    """编码管理类"""

    def __init__(self):
        self.db = get_db()

    def create_code(self, project_id: str, name: str, description: str = "",
                    color: str = None, parent_id: str = None) -> Dict:
        """
        创建新编码

        Args:
            project_id: 项目ID
            name: 编码名称
            description: 编码描述
            color: 编码颜色
            parent_id: 父编码ID（用于层级编码）

        Returns:
            创建的编码信息
        """
        # 如果没有指定颜色，随机选择一个
        if color is None:
            color = random.choice(config.CODE_COLORS)

        code_id = self.db.create_code(
            project_id=project_id,
            name=name,
            description=description,
            color=color,
            parent_id=parent_id
        )

        return self.db.get_code(code_id)

    def get_code(self, code_id: str) -> Optional[Dict]:
        """获取编码详情"""
        code = self.db.get_code(code_id)
        if code:
            # 添加使用统计
            # TODO: 添加统计查询
            code['usage_count'] = 0
        return code

    def list_codes(self, project_id: str, include_stats: bool = True) -> List[Dict]:
        """列出项目的所有编码"""
        return self.db.list_codes(project_id, include_stats=include_stats)

    def update_code(self, code_id: str, **kwargs) -> bool:
        """更新编码信息"""
        try:
            self.db.update_code(code_id, **kwargs)
            return True
        except Exception:
            return False

    def delete_code(self, code_id: str) -> bool:
        """删除编码"""
        try:
            self.db.delete_code(code_id)
            return True
        except Exception:
            return False

    def apply_coding(self, document_id: str, code_id: str,
                     start_pos: int, end_pos: int,
                     text_content: str = None,
                     created_by: str = 'human',
                     ai_confidence: float = None,
                     notes: str = None) -> Dict:
        """
        对文本片段应用编码

        Args:
            document_id: 文档ID
            code_id: 编码ID
            start_pos: 起始位置
            end_pos: 结束位置
            text_content: 文本内容
            created_by: 创建者（human/ai）
            ai_confidence: AI置信度（0-1）
            notes: 备注

        Returns:
            创建的编码关联信息
        """
        coding_id = self.db.create_coding(
            document_id=document_id,
            code_id=code_id,
            start_pos=start_pos,
            end_pos=end_pos,
            text_content=text_content,
            created_by=created_by,
            ai_confidence=ai_confidence,
            notes=notes
        )

        # 获取完整的编码信息
        codings = self.db.get_document_codings(document_id)
        for coding in codings:
            if coding['id'] == coding_id:
                return coding

        return {'id': coding_id}

    def get_document_codings(self, document_id: str) -> List[Dict]:
        """获取文档的所有编码"""
        return self.db.get_document_codings(document_id)

    def delete_coding(self, coding_id: str) -> bool:
        """删除编码关联"""
        try:
            self.db.delete_coding(coding_id)
            return True
        except Exception:
            return False

    def get_coding_stats(self, project_id: str) -> Dict:
        """
        获取项目的编码统计信息

        Returns:
            包含编码频率、分布等统计信息的字典
        """
        codes = self.db.list_codes(project_id, include_stats=True)

        # 按使用频率排序
        codes_by_usage = sorted(codes, key=lambda x: x['usage_count'], reverse=True)

        # 计算总编码数
        total_codings = sum(code['usage_count'] for code in codes)

        # 计算平均每个编码的使用次数
        avg_usage = total_codings / len(codes) if codes else 0

        return {
            'total_codes': len(codes),
            'total_codings': total_codings,
            'avg_usage': avg_usage,
            'codes_by_usage': codes_by_usage,
            'most_used_codes': codes_by_usage[:10] if codes_by_usage else [],
            'unused_codes': [code for code in codes if code['usage_count'] == 0],
        }

    def get_code_matrix(self, project_id: str) -> List[Dict]:
        """
        获取编码-文档矩阵

        Returns:
            每个文档中各编码的使用情况
        """
        documents = self.db.list_documents(project_id)
        codes = self.db.list_codes(project_id)

        matrix = []

        for doc in documents:
            row = {
                'document_id': doc['id'],
                'document_name': doc['filename'],
            }

            # 获取该文档的编码
            codings = self.db.get_document_codings(doc['id'])

            # 统计每个编码的使用次数
            for code in codes:
                code_codings = [c for c in codings if c['code_id'] == code['id']]
                row[code['name']] = len(code_codings)

            matrix.append(row)

        return matrix


# 全局编码管理器实例
_coding_manager = None


def get_coding_manager() -> CodingManager:
    """获取编码管理器实例"""
    global _coding_manager
    if _coding_manager is None:
        _coding_manager = CodingManager()
    return _coding_manager
