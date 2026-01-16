"""
AI辅助质性研究平台 - 文档处理模块
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
import PyPDF2
from docx import Document

from src.utils.database import get_db


class DocumentManager:
    """文档管理类"""

    def __init__(self):
        self.db = get_db()

    def extract_text_from_file(self, file_path: str) -> str:
        """
        从文件中提取文本

        Args:
            file_path: 文件路径

        Returns:
            提取的文本内容
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        if suffix == '.txt':
            return self._extract_from_txt(file_path)
        elif suffix == '.pdf':
            return self._extract_from_pdf(file_path)
        elif suffix == '.docx':
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")

    def _extract_from_txt(self, file_path: Path) -> str:
        """从TXT文件提取文本"""
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'big5']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        # 如果所有编码都失败，使用默认编码并忽略错误
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _extract_from_pdf(self, file_path: Path) -> str:
        """从PDF文件提取文本"""
        text_parts = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

        return '\n\n'.join(text_parts)

    def _extract_from_docx(self, file_path: Path) -> str:
        """从DOCX文件提取文本"""
        doc = Document(file_path)
        text_parts = []

        for paragraph in doc.paragraphs:
            if paragraph.text:
                text_parts.append(paragraph.text)

        return '\n\n'.join(text_parts)

    def upload_document(self, project_id: str, file_path: str,
                        metadata: Dict = None) -> Dict:
        """
        上传文档到项目

        Args:
            project_id: 项目ID
            file_path: 文件路径
            metadata: 元数据（如参与者ID、访谈日期等）

        Returns:
            创建的文档信息
        """
        file_path = Path(file_path)

        # 提取文本内容
        content = self.extract_text_from_file(file_path)

        # 获取文件类型
        file_type = file_path.suffix.lower().lstrip('.')

        # 创建文档记录
        doc_id = self.db.create_document(
            project_id=project_id,
            filename=file_path.name,
            content=content,
            file_type=file_type,
            metadata=metadata
        )

        return self.db.get_document(doc_id)

    def create_document_from_text(self, project_id: str, filename: str,
                                  content: str, metadata: Dict = None) -> Dict:
        """
        从文本内容创建文档

        Args:
            project_id: 项目ID
            filename: 文件名
            content: 文本内容
            metadata: 元数据

        Returns:
            创建的文档信息
        """
        doc_id = self.db.create_document(
            project_id=project_id,
            filename=filename,
            content=content,
            file_type='txt',
            metadata=metadata
        )

        return self.db.get_document(doc_id)

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """获取文档详情"""
        doc = self.db.get_document(doc_id)
        if doc:
            # 添加编码统计
            codings = self.db.get_document_codings(doc_id)
            doc['codings'] = codings
            doc['coding_count'] = len(codings)
        return doc

    def list_documents(self, project_id: str) -> List[Dict]:
        """列出项目的所有文档"""
        return self.db.list_documents(project_id)

    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        try:
            self.db.delete_document(doc_id)
            return True
        except Exception:
            return False

    def search_documents(self, project_id: str, query: str) -> List[Dict]:
        """
        在项目中搜索文档

        Args:
            project_id: 项目ID
            query: 搜索关键词

        Returns:
            匹配的文档列表
        """
        documents = self.db.list_documents(project_id)
        results = []

        query_lower = query.lower()

        for doc in documents:
            # 搜索文件名
            if query_lower in doc['filename'].lower():
                results.append(doc)
                continue

            # 搜索内容
            if doc['content'] and query_lower in doc['content'].lower():
                results.append(doc)
                continue

            # 搜索元数据
            if doc.get('metadata'):
                metadata_str = str(doc['metadata']).lower()
                if query_lower in metadata_str:
                    results.append(doc)

        return results


# 全局文档管理器实例
_document_manager = None


def get_document_manager() -> DocumentManager:
    """获取文档管理器实例"""
    global _document_manager
    if _document_manager is None:
        _document_manager = DocumentManager()
    return _document_manager
