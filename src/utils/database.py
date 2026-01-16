"""
AI辅助质性研究平台 - 数据库操作模块
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import uuid

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import DATABASE_PATH


class Database:
    """数据库操作类"""

    def __init__(self, db_path: str = None):
        """初始化数据库连接"""
        self.db_path = db_path or DATABASE_PATH
        self.conn = None
        self.connect()
        self.init_tables()

    def connect(self):
        """建立数据库连接"""
        # 确保数据目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 返回字典格式的行

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

    def init_tables(self):
        """初始化数据库表"""
        cursor = self.conn.cursor()

        # 项目表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                research_question TEXT,
                methodology TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 文档表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                content TEXT,
                file_type TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # 编码表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS codes (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                color TEXT,
                parent_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES codes(id) ON DELETE SET NULL
            )
        """)

        # 编码关联表（文本片段与编码的关联）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS codings (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                code_id TEXT NOT NULL,
                start_pos INTEGER NOT NULL,
                end_pos INTEGER NOT NULL,
                text_content TEXT,
                created_by TEXT DEFAULT 'human',
                ai_confidence REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                FOREIGN KEY (code_id) REFERENCES codes(id) ON DELETE CASCADE
            )
        """)

        # 主题表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS themes (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                definition TEXT,
                created_by TEXT DEFAULT 'human',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # 主题-编码关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS theme_codes (
                theme_id TEXT NOT NULL,
                code_id TEXT NOT NULL,
                relevance_score REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (theme_id, code_id),
                FOREIGN KEY (theme_id) REFERENCES themes(id) ON DELETE CASCADE,
                FOREIGN KEY (code_id) REFERENCES codes(id) ON DELETE CASCADE
            )
        """)

        # 典型引用表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS theme_quotes (
                id TEXT PRIMARY KEY,
                theme_id TEXT NOT NULL,
                coding_id TEXT NOT NULL,
                quote_type TEXT,
                reason TEXT,
                created_by TEXT DEFAULT 'ai',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (theme_id) REFERENCES themes(id) ON DELETE CASCADE,
                FOREIGN KEY (coding_id) REFERENCES codings(id) ON DELETE CASCADE
            )
        """)

        # 研究备忘录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memos (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                title TEXT,
                content TEXT,
                linked_type TEXT,
                linked_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # 报告表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                title TEXT,
                report_type TEXT DEFAULT 'paper',
                language TEXT DEFAULT 'zh',
                citation_style TEXT DEFAULT 'APA',
                content TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        self.conn.commit()

        # 创建索引（如果不存在）
        self._create_indexes()

    def _create_indexes(self):
        """创建数据库索引"""
        cursor = self.conn.cursor()

        # 主题相关索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_themes_project ON themes(project_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_theme_codes_theme ON theme_codes(theme_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_theme_codes_code ON theme_codes(code_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_theme_quotes_theme ON theme_quotes(theme_id)
        """)

        # 文档相关索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_documents_project ON documents(project_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_codings_document ON codings(document_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_codings_code ON codings(code_id)
        """)

        # 编码相关索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_codes_project ON codes(project_id)
        """)

        # 报告相关索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_reports_project ON reports(project_id)
        """)

        self.conn.commit()

    # ==================== 项目操作 ====================

    def create_project(self, name: str, description: str = None,
                       research_question: str = None, methodology: str = None) -> str:
        """创建新项目"""
        project_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO projects (id, name, description, research_question, methodology)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, name, description, research_question, methodology))
        self.conn.commit()
        return project_id

    def get_project(self, project_id: str) -> Optional[Dict]:
        """获取项目信息"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def list_projects(self) -> List[Dict]:
        """列出所有项目"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*,
                   COUNT(DISTINCT d.id) as doc_count,
                   COUNT(DISTINCT c.id) as code_count
            FROM projects p
            LEFT JOIN documents d ON p.id = d.project_id
            LEFT JOIN codes c ON p.id = c.project_id
            GROUP BY p.id
            ORDER BY p.updated_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def update_project(self, project_id: str, **kwargs):
        """更新项目信息"""
        allowed_fields = ['name', 'description', 'research_question', 'methodology']
        updates = [f"{k} = ?" for k in kwargs.keys() if k in allowed_fields]
        if updates:
            query = f"UPDATE projects SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            values = list(kwargs.values()) + [project_id]
            cursor = self.conn.cursor()
            cursor.execute(query, values)
            self.conn.commit()

    def delete_project(self, project_id: str):
        """删除项目（级联删除相关数据）"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()

    # ==================== 文档操作 ====================

    def create_document(self, project_id: str, filename: str, content: str,
                        file_type: str = None, metadata: Dict = None) -> str:
        """创建文档"""
        doc_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO documents (id, project_id, filename, content, file_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (doc_id, project_id, filename, content, file_type,
              json.dumps(metadata) if metadata else None))
        self.conn.commit()
        return doc_id

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """获取文档"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        if row:
            doc = dict(row)
            if doc['metadata']:
                doc['metadata'] = json.loads(doc['metadata'])
            return doc
        return None

    def list_documents(self, project_id: str) -> List[Dict]:
        """列出项目的所有文档"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT d.*,
                   COUNT(DISTINCT c.id) as coding_count
            FROM documents d
            LEFT JOIN codings c ON d.id = c.document_id
            WHERE d.project_id = ?
            GROUP BY d.id
            ORDER BY d.created_at DESC
        """, (project_id,))
        docs = []
        for row in cursor.fetchall():
            doc = dict(row)
            if doc['metadata']:
                doc['metadata'] = json.loads(doc['metadata'])
            docs.append(doc)
        return docs

    def delete_document(self, doc_id: str):
        """删除文档"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        self.conn.commit()

    # ==================== 编码操作 ====================

    def create_code(self, project_id: str, name: str, description: str = None,
                    color: str = None, parent_id: str = None) -> str:
        """创建编码"""
        code_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO codes (id, project_id, name, description, color, parent_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (code_id, project_id, name, description, color, parent_id))
        self.conn.commit()
        return code_id

    def get_code(self, code_id: str) -> Optional[Dict]:
        """获取编码"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM codes WHERE id = ?", (code_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_codes(self, project_id: str, include_stats: bool = True) -> List[Dict]:
        """列出项目的所有编码"""
        cursor = self.conn.cursor()
        if include_stats:
            cursor.execute("""
                SELECT c.*,
                       COUNT(DISTINCT co.id) as usage_count,
                       COUNT(DISTINCT co.document_id) as document_count
                FROM codes c
                LEFT JOIN codings co ON c.id = co.code_id
                WHERE c.project_id = ?
                GROUP BY c.id
                ORDER BY c.name
            """, (project_id,))
        else:
            cursor.execute("""
                SELECT * FROM codes
                WHERE project_id = ?
                ORDER BY name
            """, (project_id,))
        return [dict(row) for row in cursor.fetchall()]

    def update_code(self, code_id: str, **kwargs):
        """更新编码"""
        allowed_fields = ['name', 'description', 'color', 'parent_id']
        updates = [f"{k} = ?" for k in kwargs.keys() if k in allowed_fields]
        if updates:
            query = f"UPDATE codes SET {', '.join(updates)} WHERE id = ?"
            values = list(kwargs.values()) + [code_id]
            cursor = self.conn.cursor()
            cursor.execute(query, values)
            self.conn.commit()

    def delete_code(self, code_id: str):
        """删除编码"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM codes WHERE id = ?", (code_id,))
        self.conn.commit()

    # ==================== 编码关联操作 ====================

    def create_coding(self, document_id: str, code_id: str, start_pos: int,
                      end_pos: int, text_content: str = None, created_by: str = 'human',
                      ai_confidence: float = None, notes: str = None) -> str:
        """创建编码关联（对文本片段进行编码）"""
        coding_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO codings (id, document_id, code_id, start_pos, end_pos,
                               text_content, created_by, ai_confidence, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (coding_id, document_id, code_id, start_pos, end_pos,
              text_content, created_by, ai_confidence, notes))
        self.conn.commit()
        return coding_id

    def get_document_codings(self, document_id: str) -> List[Dict]:
        """获取文档的所有编码"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.*, co.name as code_name, co.color as code_color,
                   d.filename as document_filename
            FROM codings c
            JOIN codes co ON c.code_id = co.id
            JOIN documents d ON c.document_id = d.id
            WHERE c.document_id = ?
            ORDER BY c.start_pos
        """, (document_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_document_codings_by_code(self, code_id: str) -> List[Dict]:
        """获取指定编码的所有编码实例"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.*, co.name as code_name, co.color as code_color,
                   d.filename as document_filename
            FROM codings c
            JOIN codes co ON c.code_id = co.id
            JOIN documents d ON c.document_id = d.id
            WHERE c.code_id = ?
            ORDER BY d.filename, c.start_pos
        """, (code_id,))
        return [dict(row) for row in cursor.fetchall()]

    def delete_coding(self, coding_id: str):
        """删除编码关联"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM codings WHERE id = ?", (coding_id,))
        self.conn.commit()

    # ==================== 主题操作 ====================

    def create_theme(self, project_id: str, name: str, description: str = None,
                     definition: str = None, created_by: str = 'human') -> str:
        """创建主题"""
        theme_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO themes (id, project_id, name, description, definition, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (theme_id, project_id, name, description, definition, created_by))
        self.conn.commit()
        return theme_id

    def get_theme(self, theme_id: str) -> Optional[Dict]:
        """获取主题"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM themes WHERE id = ?", (theme_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_themes(self, project_id: str) -> List[Dict]:
        """列出项目的所有主题"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.*, COUNT(DISTINCT tc.code_id) as code_count
            FROM themes t
            LEFT JOIN theme_codes tc ON t.id = tc.theme_id
            WHERE t.project_id = ?
            GROUP BY t.id
            ORDER BY t.name
        """, (project_id,))
        return [dict(row) for row in cursor.fetchall()]

    def update_theme(self, theme_id: str, **kwargs):
        """更新主题"""
        allowed_fields = ['name', 'description', 'definition']
        updates = [f"{k} = ?" for k in kwargs.keys() if k in allowed_fields]
        if updates:
            query = f"UPDATE themes SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            values = list(kwargs.values()) + [theme_id]
            cursor = self.conn.cursor()
            cursor.execute(query, values)
            self.conn.commit()

    def delete_theme(self, theme_id: str):
        """删除主题"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM themes WHERE id = ?", (theme_id,))
        self.conn.commit()

    def add_code_to_theme(self, theme_id: str, code_id: str, relevance_score: float = 1.0):
        """将编码添加到主题"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO theme_codes (theme_id, code_id, relevance_score)
            VALUES (?, ?, ?)
        """, (theme_id, code_id, relevance_score))
        self.conn.commit()

    def remove_code_from_theme(self, theme_id: str, code_id: str):
        """从主题中移除编码"""
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM theme_codes WHERE theme_id = ? AND code_id = ?
        """, (theme_id, code_id))
        self.conn.commit()

    def get_theme_codes(self, theme_id: str) -> List[Dict]:
        """获取主题关联的所有编码"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.*, tc.relevance_score
            FROM codes c
            JOIN theme_codes tc ON c.id = tc.code_id
            WHERE tc.theme_id = ?
            ORDER BY tc.relevance_score DESC, c.name
        """, (theme_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_theme_codes_with_stats(self, theme_id: str) -> List[Dict]:
        """获取主题关联的编码及统计信息"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.*, tc.relevance_score,
                   COUNT(DISTINCT co.id) as coding_count,
                   COUNT(DISTINCT co.document_id) as document_count
            FROM codes c
            JOIN theme_codes tc ON c.id = tc.code_id
            LEFT JOIN codings co ON c.id = co.code_id
            WHERE tc.theme_id = ?
            GROUP BY c.id, tc.relevance_score
            ORDER BY tc.relevance_score DESC, c.name
        """, (theme_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_theme_code_associations(self, project_id: str) -> List[Dict]:
        """获取项目的所有主题-编码关联"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT tc.theme_id, tc.code_id, tc.relevance_score,
                   t.name as theme_name, c.name as code_name, c.color as code_color
            FROM theme_codes tc
            JOIN themes t ON tc.theme_id = t.id
            JOIN codes c ON tc.code_id = c.id
            WHERE t.project_id = ?
        """, (project_id,))
        return [dict(row) for row in cursor.fetchall()]

    # ==================== 典型引用操作 ====================

    def create_theme_quote(self, theme_id: str, coding_id: str, quote_type: str,
                          reason: str = None, created_by: str = 'ai') -> str:
        """创建主题典型引用"""
        quote_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO theme_quotes (id, theme_id, coding_id, quote_type, reason, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (quote_id, theme_id, coding_id, quote_type, reason, created_by))
        self.conn.commit()
        return quote_id

    def get_theme_quotes(self, theme_id: str, quote_type: str = None) -> List[Dict]:
        """获取主题的典型引用"""
        cursor = self.conn.cursor()
        if quote_type:
            cursor.execute("""
                SELECT tq.*, co.text_content, co.start_pos, co.end_pos,
                       d.filename as document_filename
                FROM theme_quotes tq
                JOIN codings co ON tq.coding_id = co.id
                JOIN documents d ON co.document_id = d.id
                WHERE tq.theme_id = ? AND tq.quote_type = ?
                ORDER BY tq.created_at DESC
            """, (theme_id, quote_type))
        else:
            cursor.execute("""
                SELECT tq.*, co.text_content, co.start_pos, co.end_pos,
                       d.filename as document_filename
                FROM theme_quotes tq
                JOIN codings co ON tq.coding_id = co.id
                JOIN documents d ON co.document_id = d.id
                WHERE tq.theme_id = ?
                ORDER BY tq.created_at DESC
            """, (theme_id,))
        return [dict(row) for row in cursor.fetchall()]

    def delete_theme_quote(self, quote_id: str):
        """删除典型引用"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM theme_quotes WHERE id = ?", (quote_id,))
        self.conn.commit()

    # ==================== 统计查询 ====================

    def get_project_stats(self, project_id: str) -> Dict:
        """获取项目统计信息"""
        cursor = self.conn.cursor()

        # 文档数量
        cursor.execute("SELECT COUNT(*) as count FROM documents WHERE project_id = ?",
                      (project_id,))
        doc_count = cursor.fetchone()['count']

        # 编码数量
        cursor.execute("SELECT COUNT(*) as count FROM codes WHERE project_id = ?",
                      (project_id,))
        code_count = cursor.fetchone()['count']

        # 编码关联数量
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM codings co
            JOIN documents d ON co.document_id = d.id
            WHERE d.project_id = ?
        """, (project_id,))
        coding_count = cursor.fetchone()['count']

        # 主题数量
        cursor.execute("SELECT COUNT(*) as count FROM themes WHERE project_id = ?",
                      (project_id,))
        theme_count = cursor.fetchone()['count']

        return {
            'doc_count': doc_count,
            'code_count': code_count,
            'coding_count': coding_count,
            'theme_count': theme_count,
        }

    # ==================== 报告操作 ====================

    def create_report(self, project_id: str, title: str, report_type: str = 'paper',
                     language: str = 'zh', citation_style: str = 'APA',
                     content: Dict = None) -> str:
        """创建报告"""
        report_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO reports (id, project_id, title, report_type, language, citation_style, content)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (report_id, project_id, title, report_type, language, citation_style,
              json.dumps(content) if content else None))
        self.conn.commit()
        return report_id

    def get_report(self, report_id: str) -> Optional[Dict]:
        """获取报告"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        row = cursor.fetchone()
        if row:
            report = dict(row)
            if report['content']:
                report['content'] = json.loads(report['content'])
            return report
        return None

    def list_reports(self, project_id: str) -> List[Dict]:
        """列出项目的所有报告"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM reports
            WHERE project_id = ?
            ORDER BY updated_at DESC
        """, (project_id,))
        reports = []
        for row in cursor.fetchall():
            report = dict(row)
            if report['content']:
                report['content'] = json.loads(report['content'])
            reports.append(report)
        return reports

    def update_report(self, report_id: str, **kwargs):
        """更新报告"""
        allowed_fields = ['title', 'report_type', 'language', 'citation_style', 'content', 'status']
        updates = []
        values = []
        for k, v in kwargs.items():
            if k in allowed_fields:
                updates.append(f"{k} = ?")
                if k == 'content' and isinstance(v, dict):
                    values.append(json.dumps(v))
                else:
                    values.append(v)

        if updates:
            query = f"UPDATE reports SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            values.append(report_id)
            cursor = self.conn.cursor()
            cursor.execute(query, values)
            self.conn.commit()

    def update_report_content(self, report_id: str, section: str, content: str):
        """更新报告的特定部分"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT content FROM reports WHERE id = ?", (report_id,))
        row = cursor.fetchone()
        if row and row['content']:
            report_content = json.loads(row['content'])
            report_content[section] = content
            cursor.execute("""
                UPDATE reports SET content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps(report_content), report_id))
            self.conn.commit()

    def delete_report(self, report_id: str):
        """删除报告"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        self.conn.commit()

    def get_report_by_project_latest(self, project_id: str) -> Optional[Dict]:
        """获取项目的最新报告"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM reports
            WHERE project_id = ?
            ORDER BY updated_at DESC
            LIMIT 1
        """, (project_id,))
        row = cursor.fetchone()
        if row:
            report = dict(row)
            if report['content']:
                report['content'] = json.loads(report['content'])
            return report
        return None


# 单例模式
_db_instance = None


def get_db() -> Database:
    """获取数据库实例（单例）"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
