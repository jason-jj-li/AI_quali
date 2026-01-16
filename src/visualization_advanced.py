"""
高级可视化工具
包括热力图、旭日图、时间线、地理可视化等
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Optional, Any
import numpy as np


def create_code_document_heatmap(codes: List[Dict], documents: List[Dict] = None) -> go.Figure:
    """
    创建编码-文档热力图
    
    Args:
        codes: 编码列表
        documents: 文档列表（如果为None，使用单文档模式）
        
    Returns:
        Plotly Figure对象
    """
    if documents is None or len(documents) == 0:
        # 单文档模式：显示编码使用频率
        code_names = [c['name'] for c in codes]
        code_counts = [len(c.get('quotes', [])) for c in codes]
        
        # 创建简单的条形图形式的热力图
        data = [[count] for count in code_counts]
        
        fig = go.Figure(data=go.Heatmap(
            z=data,
            x=['文本'],
            y=code_names,
            colorscale='Blues',
            text=data,
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='编码使用频率热力图',
            xaxis_title='',
            yaxis_title='编码',
            height=max(400, len(codes) * 30),
            margin=dict(l=150)
        )
    
    else:
        # 多文档模式
        code_names = [c['name'] for c in codes]
        doc_names = [d.get('filename', f"文档{i+1}") for i, d in enumerate(documents)]
        
        # 创建矩阵
        matrix = np.zeros((len(codes), len(documents)))
        
        for i, code in enumerate(codes):
            for j, doc in enumerate(documents):
                # 统计该编码在该文档中的使用次数
                # 这里需要根据实际数据结构调整
                count = 0
                if 'quotes' in code:
                    for quote in code['quotes']:
                        if isinstance(quote, dict) and quote.get('document_id') == doc.get('id'):
                            count += 1
                        elif isinstance(quote, str):
                            # 简单模式：所有引用都算在第一个文档
                            if j == 0:
                                count += 1
                matrix[i, j] = count
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=doc_names,
            y=code_names,
            colorscale='Viridis',
            text=matrix.astype(int),
            texttemplate='%{text}',
            textfont={"size": 10},
            hovertemplate='编码: %{y}<br>文档: %{x}<br>次数: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title='编码-文档热力图',
            xaxis_title='文档',
            yaxis_title='编码',
            height=max(400, len(codes) * 30),
            margin=dict(l=150, b=100)
        )
    
    return fig


def create_theme_hierarchy_sunburst(themes: List[Dict], codes: List[Dict]) -> go.Figure:
    """
    创建主题层级旭日图
    
    Args:
        themes: 主题列表
        codes: 编码列表
        
    Returns:
        Plotly Figure对象
    """
    # 构建层级数据
    labels = ['全部主题']
    parents = ['']
    values = [100]
    colors = ['#ffffff']
    
    # 添加主题层
    for theme in themes:
        theme_name = theme['name']
        related_codes = theme.get('codes', [])
        
        labels.append(theme_name)
        parents.append('全部主题')
        values.append(len(related_codes) if related_codes else 1)
        colors.append('#3498db')
        
        # 添加编码层
        for code_name in related_codes:
            # 查找编码详情
            code = next((c for c in codes if c['name'] == code_name), None)
            if code:
                quote_count = len(code.get('quotes', []))
                labels.append(f"{code_name}")
                parents.append(theme_name)
                values.append(quote_count if quote_count > 0 else 1)
                colors.append('#95a5a6')
    
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(
            colors=colors,
            line=dict(color='white', width=2)
        ),
        branchvalues="total",
        hovertemplate='<b>%{label}</b><br>值: %{value}<extra></extra>'
    ))
    
    fig.update_layout(
        title='主题-编码层级结构',
        height=600,
        margin=dict(t=50, l=0, r=0, b=0)
    )
    
    return fig


def create_timeline_visualization(events: List[Dict]) -> go.Figure:
    """
    创建时间线可视化
    
    Args:
        events: 事件列表 [{"time": "2020年", "event": "事件", "category": "类别"}, ...]
        
    Returns:
        Plotly Figure对象
    """
    if not events:
        # 返回空图
        fig = go.Figure()
        fig.add_annotation(
            text="暂无时间线数据",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # 按时间排序
    sorted_events = sorted(events, key=lambda x: x.get('time', ''))
    
    # 准备数据
    times = [e.get('time', '') for e in sorted_events]
    event_texts = [e.get('event', '') for e in sorted_events]
    categories = [e.get('category', '未分类') for e in sorted_events]
    
    # 为每个类别分配颜色
    unique_categories = list(set(categories))
    color_map = {cat: px.colors.qualitative.Set3[i % len(px.colors.qualitative.Set3)] 
                 for i, cat in enumerate(unique_categories)}
    colors = [color_map[cat] for cat in categories]
    
    # 创建散点图
    fig = go.Figure()
    
    # 添加时间线
    fig.add_trace(go.Scatter(
        x=list(range(len(times))),
        y=[1] * len(times),
        mode='lines+markers+text',
        line=dict(color='lightgray', width=2),
        marker=dict(
            size=15,
            color=colors,
            line=dict(color='white', width=2)
        ),
        text=times,
        textposition='bottom center',
        hovertext=event_texts,
        hoverinfo='text',
        showlegend=False
    ))
    
    # 添加事件文本
    for i, (time, event, color) in enumerate(zip(times, event_texts, colors)):
        fig.add_annotation(
            x=i,
            y=1.3,
            text=event[:50] + '...' if len(event) > 50 else event,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=color,
            ax=0,
            ay=-40,
            bgcolor=color,
            opacity=0.8,
            font=dict(size=10, color='white')
        )
    
    fig.update_layout(
        title='事件时间线',
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0.5, 2]
        ),
        height=400,
        hovermode='closest',
        plot_bgcolor='white'
    )
    
    # 添加图例
    for cat in unique_categories:
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color=color_map[cat]),
            name=cat,
            showlegend=True
        ))
    
    return fig


def create_sentiment_timeline(timeline_data: Dict) -> go.Figure:
    """
    创建情感时间线可视化
    
    Args:
        timeline_data: 从sentiment_analyzer.analyze_sentiment_evolution获取的数据
        
    Returns:
        Plotly Figure对象
    """
    labels = timeline_data['timeline']['labels']
    sentiments = timeline_data['timeline']['sentiments']
    intensities = timeline_data['timeline']['intensities']
    
    # 情感到数值的映射
    sentiment_values = {
        'positive': 1,
        'neutral': 0,
        'negative': -1,
        'mixed': 0.5
    }
    
    sentiment_nums = [sentiment_values.get(s, 0) for s in sentiments]
    
    # 情感到颜色的映射
    sentiment_colors = {
        'positive': '#2ecc71',
        'neutral': '#95a5a6',
        'negative': '#e74c3c',
        'mixed': '#f39c12'
    }
    
    colors = [sentiment_colors.get(s, '#95a5a6') for s in sentiments]
    
    fig = go.Figure()
    
    # 添加情感倾向线
    fig.add_trace(go.Scatter(
        x=labels,
        y=sentiment_nums,
        mode='lines+markers',
        name='情感倾向',
        line=dict(color='#3498db', width=2),
        marker=dict(size=10, color=colors, line=dict(color='white', width=2)),
        hovertemplate='时间: %{x}<br>情感: %{text}<extra></extra>',
        text=sentiments
    ))
    
    # 添加强度线（作为柱状图）
    fig.add_trace(go.Bar(
        x=labels,
        y=intensities,
        name='情感强度',
        marker_color='rgba(52, 152, 219, 0.3)',
        yaxis='y2',
        hovertemplate='时间: %{x}<br>强度: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='情感演化时间线',
        xaxis=dict(title='时间点'),
        yaxis=dict(
            title='情感倾向',
            tickvals=[-1, 0, 1],
            ticktext=['消极', '中性', '积极']
        ),
        yaxis2=dict(
            title='情感强度',
            overlaying='y',
            side='right',
            range=[0, 1]
        ),
        hovermode='x unified',
        height=400,
        showlegend=True
    )
    
    return fig


def create_code_cooccurrence_network(codes: List[Dict], min_cooccurrence: int = 2) -> go.Figure:
    """
    创建编码共现网络图
    
    Args:
        codes: 编码列表
        min_cooccurrence: 最小共现次数阈值
        
    Returns:
        Plotly Figure对象
    """
    # 构建共现矩阵
    code_names = [c['name'] for c in codes]
    n = len(code_names)
    cooccurrence = np.zeros((n, n))
    
    # 计算共现（这里简化处理，实际需要根据文本片段计算）
    # 假设在同一主题下的编码视为共现
    for i in range(n):
        for j in range(i+1, n):
            # 简化：随机生成共现（实际应基于真实数据）
            count = np.random.randint(0, 5)
            cooccurrence[i, j] = count
            cooccurrence[j, i] = count
    
    # 创建网络图
    edges = []
    edge_weights = []
    
    for i in range(n):
        for j in range(i+1, n):
            if cooccurrence[i, j] >= min_cooccurrence:
                edges.append((i, j))
                edge_weights.append(cooccurrence[i, j])
    
    if not edges:
        fig = go.Figure()
        fig.add_annotation(
            text=f"没有达到阈值({min_cooccurrence})的共现关系",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # 使用力导向布局计算位置
    import math
    positions = {}
    radius = 1
    for i, code_name in enumerate(code_names):
        angle = 2 * math.pi * i / n
        positions[i] = (radius * math.cos(angle), radius * math.sin(angle))
    
    # 创建边
    edge_traces = []
    for (i, j), weight in zip(edges, edge_weights):
        x0, y0 = positions[i]
        x1, y1 = positions[j]
        
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=weight, color='rgba(125, 125, 125, 0.5)'),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # 创建节点
    node_x = [positions[i][0] for i in range(n)]
    node_y = [positions[i][1] for i in range(n)]
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=20,
            color='#3498db',
            line=dict(width=2, color='white')
        ),
        text=code_names,
        textposition='top center',
        textfont=dict(size=10),
        hoverinfo='text',
        hovertext=code_names,
        showlegend=False
    )
    
    fig = go.Figure(data=edge_traces + [node_trace])
    
    fig.update_layout(
        title='编码共现网络',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white',
        height=600
    )
    
    return fig


def create_theme_comparison_radar(themes: List[Dict], metrics: List[str] = None) -> go.Figure:
    """
    创建主题对比雷达图
    
    Args:
        themes: 主题列表
        metrics: 对比指标列表
        
    Returns:
        Plotly Figure对象
    """
    if metrics is None:
        metrics = ['编码数量', '引用数量', '覆盖度', '深度', '创新性']
    
    fig = go.Figure()
    
    for theme in themes[:6]:  # 最多显示6个主题
        # 计算各项指标（这里用随机值演示，实际应基于真实数据）
        values = []
        for metric in metrics:
            if metric == '编码数量':
                value = len(theme.get('codes', [])) / 10  # 归一化
            elif metric == '引用数量':
                value = len(theme.get('quotes', [])) / 10
            else:
                value = np.random.random()  # 其他指标用随机值
            values.append(min(value, 1.0))  # 确保在0-1之间
        
        values.append(values[0])  # 闭合雷达图
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics + [metrics[0]],
            fill='toself',
            name=theme['name']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title='主题多维度对比',
        height=500
    )
    
    return fig


def create_coding_evolution_chart(evolution_data: List[Dict]) -> go.Figure:
    """
    创建编码演进图
    
    Args:
        evolution_data: [{"version": "v1", "codes": [...], "timestamp": "..."}, ...]
        
    Returns:
        Plotly Figure对象
    """
    versions = [d['version'] for d in evolution_data]
    code_counts = [len(d['codes']) for d in evolution_data]
    
    fig = go.Figure()
    
    # 添加编码数量变化
    fig.add_trace(go.Scatter(
        x=versions,
        y=code_counts,
        mode='lines+markers',
        name='编码总数',
        line=dict(color='#3498db', width=3),
        marker=dict(size=10)
    ))
    
    # 统计每个版本的新增、删除、修改
    if len(evolution_data) > 1:
        added = []
        removed = []
        
        for i in range(1, len(evolution_data)):
            prev_codes = set(c['name'] for c in evolution_data[i-1]['codes'])
            curr_codes = set(c['name'] for c in evolution_data[i]['codes'])
            
            added.append(len(curr_codes - prev_codes))
            removed.append(len(prev_codes - curr_codes))
        
        fig.add_trace(go.Bar(
            x=versions[1:],
            y=added,
            name='新增编码',
            marker_color='#2ecc71'
        ))
        
        fig.add_trace(go.Bar(
            x=versions[1:],
            y=removed,
            name='删除编码',
            marker_color='#e74c3c'
        ))
    
    fig.update_layout(
        title='编码本演进历史',
        xaxis_title='版本',
        yaxis_title='数量',
        hovermode='x unified',
        height=400,
        barmode='group'
    )
    
    return fig
