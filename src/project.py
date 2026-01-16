"""
AI辅助质性研究平台 - 项目管理模块
"""
from typing import List, Dict, Optional
from datetime import datetime

from src.utils.database import get_db


class ProjectManager:
    """项目管理类"""

    def __init__(self):
        self.db = get_db()

    def create_project(self, name: str, description: str = "",
                       research_question: str = "", methodology: str = "") -> Dict:
        """
        创建新项目

        Args:
            name: 项目名称
            description: 项目描述
            research_question: 研究问题
            methodology: 研究方法

        Returns:
            创建的项目信息
        """
        project_id = self.db.create_project(
            name=name,
            description=description,
            research_question=research_question,
            methodology=methodology
        )

        return self.db.get_project(project_id)

    def get_project(self, project_id: str) -> Optional[Dict]:
        """获取项目详情"""
        project = self.db.get_project(project_id)
        if project:
            # 添加统计信息
            stats = self.db.get_project_stats(project_id)
            project.update(stats)
        return project

    def list_projects(self) -> List[Dict]:
        """列出所有项目"""
        projects = self.db.list_projects()

        # 添加统计信息
        for project in projects:
            stats = self.db.get_project_stats(project['id'])
            project.update(stats)

        return projects

    def update_project(self, project_id: str, **kwargs) -> bool:
        """更新项目信息"""
        try:
            self.db.update_project(project_id, **kwargs)
            return True
        except Exception:
            return False

    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        try:
            self.db.delete_project(project_id)
            return True
        except Exception:
            return False

    def get_project_summary(self, project_id: str) -> Dict:
        """
        获取项目摘要信息（用于仪表板）

        Returns:
            包含项目基本信息、统计数据的字典
        """
        project = self.get_project(project_id)
        if not project:
            return None

        # 获取最近的文档
        documents = self.db.list_documents(project_id)

        # 获取编码统计
        codes = self.db.list_codes(project_id, include_stats=True)

        # 获取主题列表
        themes = self.db.list_themes(project_id)

        return {
            'project': project,
            'recent_documents': documents[:5],  # 最近5个文档
            'code_stats': codes,
            'themes': themes,
        }


# 全局项目管理器实例
_project_manager = None


def get_project_manager() -> ProjectManager:
    """获取项目管理器实例"""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager
