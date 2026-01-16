"""
AI辅助质性研究平台 - 可视化模块
使用Plotly创建交互式图表
"""
from typing import List, Dict, Optional, Any
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


class ThemeNetworkGraph:
    """主题-编码网络图"""

    def __init__(self, themes: List[Dict], codes: List[Dict],
                 associations: List[Dict]):
        """
        初始化网络图

        Args:
            themes: 主题列表
            codes: 编码列表
            associations: 主题-编码关联列表
        """
        self.themes = themes
        self.codes = codes
        self.associations = associations

    def create_network_graph(self, layout_type: str = "spring") -> go.Figure:
        """
        创建网络图

        Args:
            layout_type: 布局类型 ("spring", "circular", "hierarchical")

        Returns:
            Plotly Figure对象
        """
        # 构建节点
        nodes = []
        node_colors = []
        node_sizes = []
        node_texts = []
        node_labels = []  # 用于悬停显示的完整信息

        # 添加主题节点
        for theme in self.themes:
            theme_name = theme.get('name', '未知主题')
            code_count = len(theme.get('codes', []))

            nodes.append({
                'id': theme['id'],
                'label': theme_name,
                'type': 'theme',
                'size': 30 + min(code_count * 3, 30),  # 根据关联编码数调整大小
                'color': '#3498db'  # 蓝色
            })
            node_colors.append('#3498db')
            node_sizes.append(30 + min(code_count * 3, 30))
            node_texts.append(theme_name)
            node_labels.append(f"主题: {theme_name}<br>关联编码: {code_count}个")

        # 添加编码节点
        for code in self.codes:
            code_name = code.get('name', '未知编码')
            usage_count = code.get('usage_count', 0)
            color = code.get('color', '#95a5a6')

            nodes.append({
                'id': code['id'],
                'label': code_name,
                'type': 'code',
                'size': 15 + min(usage_count, 15),  # 根据使用次数调整大小
                'color': color
            })
            node_colors.append(color)
            node_sizes.append(15 + min(usage_count, 15))
            node_texts.append(code_name)
            node_labels.append(f"编码: {code_name}<br>使用次数: {usage_count}")

        # 构建边
        edges = []
        edge_colors = []
        edge_widths = []

        for assoc in self.associations:
            theme_id = assoc.get('theme_id')
            code_id = assoc.get('code_id')
            relevance = assoc.get('relevance_score', 1.0)

            edges.append((theme_id, code_id))
            edge_colors.append(f'rgba(52, 152, 219, {0.3 + relevance * 0.5})')
            edge_widths.append(1 + relevance * 4)

        # 计算节点位置（使用简单的力导向布局）
        node_positions = self._calculate_layout(nodes, edges, layout_type)

        # 提取x和y坐标
        x_coords = [node_positions[n['id']]['x'] for n in nodes]
        y_coords = [node_positions[n['id']]['y'] for n in nodes]

        # 创建边
        edge_traces = []
        for i, (source, target) in enumerate(edges):
            x0 = node_positions[source]['x']
            y0 = node_positions[source]['y']
            x1 = node_positions[target]['x']
            y1 = node_positions[target]['y']

            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(
                    color=edge_colors[i],
                    width=edge_widths[i]
                ),
                hoverinfo='none',
                showlegend=False
            )
            edge_traces.append(edge_trace)

        # 创建节点
        node_trace = go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='white')
            ),
            text=node_texts,
            textposition='middle center',
            textfont=dict(size=10),
            hovertext=node_labels,
            hoverinfo='text',
            customdata=[n['id'] for n in nodes],
            showlegend=False
        )

        # 创建图形
        fig = go.Figure(data=edge_traces + [node_trace])

        # 更新布局
        fig.update_layout(
            title={
                'text': '主题-编码关系网络图',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="蓝色圆形=主题，彩色方形=编码<br>线条粗细=关联强度",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.005,
                    y=-0.002,
                    xanchor='left',
                    yanchor='bottom',
                    font=dict(size=10)
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            height=600
        )

        return fig

    def _calculate_layout(self, nodes: List[Dict], edges: List[tuple],
                         layout_type: str) -> Dict[str, Dict[str, float]]:
        """计算节点位置"""
        positions = {}

        if layout_type == "circular":
            # 圆形布局
            import math
            n = len(nodes)
            for i, node in enumerate(nodes):
                angle = 2 * math.pi * i / n
                positions[node['id']] = {
                    'x': math.cos(angle),
                    'y': math.sin(angle)
                }

        elif layout_type == "hierarchical":
            # 层级布局：主题在上，编码在下
            theme_y = 0.8
            code_y = 0.2

            # 放置主题
            themes = [n for n in nodes if n['type'] == 'theme']
            for i, theme in enumerate(themes):
                x = (i + 1) / (len(themes) + 1)
                positions[theme['id']] = {'x': x, 'y': theme_y}

            # 放置编码
            codes = [n for n in nodes if n['type'] == 'code']
            for i, code in enumerate(codes):
                x = (i + 1) / (len(codes) + 1)
                positions[code['id']] = {'x': x, 'y': code_y}

        else:  # spring (default)
            # 简化的力导向布局
            import random
            random.seed(42)

            # 初始化随机位置
            for node in nodes:
                positions[node['id']] = {
                    'x': random.random(),
                    'y': random.random()
                }

            # 简单的迭代优化
            for _ in range(50):
                for node_id in positions:
                    dx, dy = 0, 0

                    # 斥力：推开所有节点
                    for other_id in positions:
                        if node_id == other_id:
                            continue
                        diff_x = positions[node_id]['x'] - positions[other_id]['x']
                        diff_y = positions[node_id]['y'] - positions[other_id]['y']
                        dist = max(0.01, (diff_x**2 + diff_y**2)**0.5)
                        force = 0.01 / dist**2
                        dx += diff_x / dist * force
                        dy += diff_y / dist * force

                    # 引力：拉近连接的节点
                    for source, target in edges:
                        if source == node_id:
                            other_id = target
                        elif target == node_id:
                            other_id = source
                        else:
                            continue

                        diff_x = positions[node_id]['x'] - positions[other_id]['x']
                        diff_y = positions[node_id]['y'] - positions[other_id]['y']
                        dist = max(0.01, (diff_x**2 + diff_y**2)**0.5)
                        force = dist * 0.01
                        dx -= diff_x / dist * force
                        dy -= diff_y / dist * force

                    # 更新位置（限制在0-1范围内）
                    positions[node_id]['x'] = max(0.1, min(0.9, positions[node_id]['x'] + dx))
                    positions[node_id]['y'] = max(0.1, min(0.9, positions[node_id]['y'] + dy))

        return positions


class CodingFrequencyChart:
    """编码频率图表"""

    def __init__(self, codes: List[Dict]):
        """
        初始化频率图表

        Args:
            codes: 编码列表（包含usage_count统计）
        """
        self.codes = codes

    def create_bar_chart(self, top_n: int = 20) -> go.Figure:
        """
        创建编码频率柱状图

        Args:
            top_n: 显示前N个编码

        Returns:
            Plotly Figure对象
        """
        # 按使用频率排序
        sorted_codes = sorted(self.codes, key=lambda x: x.get('usage_count', 0), reverse=True)[:top_n]

        code_names = [code.get('name', '未知') for code in sorted_codes]
        usage_counts = [code.get('usage_count', 0) for code in sorted_codes]
        colors = [code.get('color', '#3498db') for code in sorted_codes]

        fig = go.Figure(data=[
            go.Bar(
                x=usage_counts,
                y=code_names,
                orientation='h',
                marker=dict(color=colors),
                text=usage_counts,
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>使用次数: %{x}<extra></extra>'
            )
        ])

        fig.update_layout(
            title=f'编码使用频率 (Top {top_n})',
            xaxis_title='使用次数',
            yaxis_title='编码名称',
            height=max(400, len(code_names) * 30),
            margin=dict(l=100, r=20, t=40, b=20),
            yaxis={'categoryorder': 'total ascending'}
        )

        return fig

    def create_heatmap(self, documents: List[Dict]) -> go.Figure:
        """
        创建编码-文档热力图

        Args:
            documents: 文档列表（包含每个文档的编码统计）

        Returns:
            Plotly Figure对象
        """
        # 准备数据
        code_names = [code.get('name', '未知') for code in self.codes]
        doc_names = [doc.get('filename', '未知') for doc in documents]

        # 构建矩阵
        matrix = []
        for doc in documents:
            row = []
            doc_codings = doc.get('codings', [])
            doc_code_ids = {c.get('code_id') for c in doc_codings}

            for code in self.codes:
                if code['id'] in doc_code_ids:
                    # 计算该编码在此文档中的使用次数
                    count = sum(1 for c in doc_codings if c.get('code_id') == code['id'])
                    row.append(count)
                else:
                    row.append(0)
            matrix.append(row)

        # 转置矩阵（编码在Y轴，文档在X轴）
        matrix = list(zip(*matrix)) if matrix else []

        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=doc_names,
            y=code_names,
            colorscale='Blues',
            hovertemplate='<b>%{y}</b><br>文档: %{x}<br>使用次数: %{z}<extra></extra>'
        ))

        fig.update_layout(
            title='编码-文档分布热力图',
            xaxis_title='文档',
            yaxis_title='编码',
            height=max(400, len(code_names) * 25),
            margin=dict(l=100, r=20, t=40, b=100)
        )

        return fig


class ThemeStatsChart:
    """主题统计图表"""

    def __init__(self, themes: List[Dict]):
        """
        初始化主题统计图表

        Args:
            themes: 主题列表（包含关联编码统计）
        """
        self.themes = themes

    def create_theme_overview(self) -> go.Figure:
        """
        创建主题概览图表

        Returns:
            Plotly Figure对象（包含子图）
        """
        from plotly.subplots import make_subplots

        theme_names = [t.get('name', '未知') for t in self.themes]
        code_counts = [len(t.get('codes', [])) for t in self.themes]
        coding_counts = [t.get('coding_count', 0) for t in self.themes]

        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('每个主题的关联编码数', '每个主题的编码实例数'),
            horizontal_spacing=0.2
        )

        # 柱状图1：关联编码数
        fig.add_trace(
            go.Bar(
                x=theme_names,
                y=code_counts,
                name='关联编码数',
                marker=dict(color='#3498db'),
                text=code_counts,
                textposition='outside'
            ),
            row=1, col=1
        )

        # 柱状图2：编码实例数
        fig.add_trace(
            go.Bar(
                x=theme_names,
                y=coding_counts,
                name='编码实例数',
                marker=dict(color='#2ecc71'),
                text=coding_counts,
                textposition='outside'
            ),
            row=1, col=2
        )

        fig.update_layout(
            title_text='主题统计概览',
            height=400,
            showlegend=False,
            margin=dict(t=80, b=100)
        )

        fig.update_xaxes(tickangle=45)

        return fig

    def create_theme_sunburst(self, codes: List[Dict]) -> go.Figure:
        """
        创建主题层级图（旭日图）

        Args:
            codes: 编码列表

        Returns:
            Plotly Figure对象
        """
        labels = []
        parents = []
        values = []
        colors = []

        # 添加主题节点
        for theme in self.themes:
            theme_name = theme.get('name', '未知')
            labels.append(theme_name)
            parents.append('')
            values.append(len(theme.get('codes', [])))
            colors.append('#3498db')

            # 添加编码节点
            for code in theme.get('codes', []):
                code_name = code.get('name', '未知')
                labels.append(code_name)
                parents.append(theme_name)
                values.append(code.get('coding_count', 1))
                colors.append(code.get('color', '#95a5a6'))

        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(colors=colors),
            hovertemplate='<b>%{label}</b><br>数值: %{value}<extra></extra>'
        ))

        fig.update_layout(
            title='主题-编码层级结构',
            height=600
        )

        return fig


def create_theme_network(project_id: str) -> go.Figure:
    """
    便捷函数：为项目创建主题网络图

    Args:
        project_id: 项目ID

    Returns:
        Plotly Figure对象
    """
    from src.utils.database import get_db

    db = get_db()
    themes = db.list_themes(project_id)
    codes = db.list_codes(project_id)
    associations = db.get_theme_code_associations(project_id)

    # 为每个主题添加关联编码
    for theme in themes:
        theme['codes'] = db.get_theme_codes(theme['id'])

    graph = ThemeNetworkGraph(themes, codes, associations)
    return graph.create_network_graph()


def create_coding_frequency_chart(project_id: str) -> go.Figure:
    """
    便捷函数：为项目创建编码频率图

    Args:
        project_id: 项目ID

    Returns:
        Plotly Figure对象
    """
    from src.utils.database import get_db

    db = get_db()
    codes = db.list_codes(project_id, include_stats=True)

    chart = CodingFrequencyChart(codes)
    return chart.create_bar_chart()


def create_theme_overview_chart(project_id: str) -> go.Figure:
    """
    便捷函数：为项目创建主题概览图

    Args:
        project_id: 项目ID

    Returns:
        Plotly Figure对象
    """
    from src.utils.database import get_db

    db = get_db()
    themes = db.list_themes(project_id)

    # 为每个主题添加编码统计
    for theme in themes:
        codes = db.get_theme_codes_with_stats(theme['id'])
        theme['codes'] = codes
        theme['coding_count'] = sum(c.get('coding_count', 0) for c in codes)

    chart = ThemeStatsChart(themes)
    return chart.create_theme_overview()
