"""
情感编码分析助手
支持情感识别、情感强度、情感演化分析
"""
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from src.llm.base import LLMProvider


@dataclass
class SentimentResult:
    """情感分析结果"""
    text: str
    sentiment: str  # positive, negative, neutral, mixed
    intensity: float  # 0-1
    emotions: Dict[str, float]  # 具体情绪及其强度
    reasoning: str


class SentimentAnalyzer:
    """情感编码分析助手"""
    
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.system_prompt = """你是一位情感分析专家，擅长识别文本中的情感和情绪表达。

## 分析维度

1. **基本情感倾向**：积极(positive)、消极(negative)、中性(neutral)、复杂(mixed)
2. **情感强度**：0-1之间的分数，表示情感的强烈程度
3. **具体情绪**：如喜悦、悲伤、愤怒、恐惧、惊讶、厌恶、信任、期待等
4. **情感表达方式**：直接表达、隐含情感、反讽等

## 输出格式

请以JSON格式输出：
```json
{
    "sentiment": "positive|negative|neutral|mixed",
    "intensity": 0.8,
    "emotions": {
        "joy": 0.7,
        "trust": 0.5,
        "anticipation": 0.3
    },
    "reasoning": "分析理由"
}
```"""
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """
        分析单个文本的情感
        
        Args:
            text: 待分析文本
            
        Returns:
            情感分析结果
        """
        prompt = f"""请分析以下文本的情感：

文本：
```
{text}
```

请识别：
1. 整体情感倾向
2. 情感强度
3. 具体包含的情绪（如喜悦、悲伤、愤怒、恐惧等）
4. 分析理由

请以JSON格式输出。"""
        
        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=800
            )
            
            # 解析JSON响应
            result_dict = self._parse_json_response(response.content)
            
            return SentimentResult(
                text=text,
                sentiment=result_dict.get('sentiment', 'neutral'),
                intensity=result_dict.get('intensity', 0.5),
                emotions=result_dict.get('emotions', {}),
                reasoning=result_dict.get('reasoning', '')
            )
        
        except Exception as e:
            return SentimentResult(
                text=text,
                sentiment='neutral',
                intensity=0.0,
                emotions={},
                reasoning=f"分析失败: {str(e)}"
            )
    
    def batch_analyze(self, texts: List[str]) -> List[SentimentResult]:
        """批量分析情感"""
        results = []
        for text in texts:
            result = self.analyze_sentiment(text)
            results.append(result)
        return results
    
    def analyze_sentiment_evolution(self, texts: List[str], labels: List[str] = None) -> Dict:
        """
        分析情感演化趋势
        
        Args:
            texts: 按时间顺序的文本列表
            labels: 时间点标签
            
        Returns:
            情感演化分析结果
        """
        results = self.batch_analyze(texts)
        
        sentiments = [r.sentiment for r in results]
        intensities = [r.intensity for r in results]
        
        # 统计情感分布
        sentiment_counts = {}
        for s in sentiments:
            sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
        
        # 计算平均强度
        avg_intensity = sum(intensities) / len(intensities) if intensities else 0
        
        # 识别情感转折点
        turning_points = []
        for i in range(1, len(sentiments)):
            if sentiments[i] != sentiments[i-1]:
                turning_points.append({
                    'index': i,
                    'from': sentiments[i-1],
                    'to': sentiments[i],
                    'label': labels[i] if labels else f"位置{i}"
                })
        
        return {
            'timeline': {
                'labels': labels or [f"T{i}" for i in range(len(texts))],
                'sentiments': sentiments,
                'intensities': intensities
            },
            'statistics': {
                'sentiment_distribution': sentiment_counts,
                'average_intensity': avg_intensity,
                'most_common_sentiment': max(sentiment_counts, key=sentiment_counts.get) if sentiment_counts else 'neutral'
            },
            'turning_points': turning_points,
            'detailed_results': [
                {
                    'text': r.text[:100] + '...' if len(r.text) > 100 else r.text,
                    'sentiment': r.sentiment,
                    'intensity': r.intensity,
                    'emotions': r.emotions
                }
                for r in results
            ]
        }
    
    def compare_sentiments(self, groups: Dict[str, List[str]]) -> Dict:
        """
        比较不同组的情感差异
        
        Args:
            groups: {组名: 文本列表}
            
        Returns:
            情感对比结果
        """
        group_results = {}
        
        for group_name, texts in groups.items():
            results = self.batch_analyze(texts)
            
            sentiments = [r.sentiment for r in results]
            intensities = [r.intensity for r in results]
            
            sentiment_counts = {}
            for s in sentiments:
                sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
            
            # 汇总所有情绪
            all_emotions = {}
            for r in results:
                for emotion, score in r.emotions.items():
                    if emotion not in all_emotions:
                        all_emotions[emotion] = []
                    all_emotions[emotion].append(score)
            
            avg_emotions = {
                emotion: sum(scores) / len(scores)
                for emotion, scores in all_emotions.items()
            }
            
            group_results[group_name] = {
                'n_texts': len(texts),
                'sentiment_distribution': sentiment_counts,
                'average_intensity': sum(intensities) / len(intensities) if intensities else 0,
                'dominant_emotions': dict(sorted(avg_emotions.items(), key=lambda x: x[1], reverse=True)[:5])
            }
        
        return {
            'groups': group_results,
            'comparison': self._generate_comparison_insights(group_results)
        }
    
    def _parse_json_response(self, content: str) -> Dict:
        """解析JSON响应"""
        # 尝试提取JSON
        import re
        
        # 移除markdown代码块标记
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # 如果失败，尝试提取第一个{}之间的内容
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            else:
                return {}
    
    def _generate_comparison_insights(self, group_results: Dict) -> List[str]:
        """生成对比洞察"""
        insights = []
        
        # 比较情感倾向
        group_names = list(group_results.keys())
        if len(group_names) >= 2:
            for i in range(len(group_names)):
                for j in range(i+1, len(group_names)):
                    g1, g2 = group_names[i], group_names[j]
                    
                    # 比较主导情感
                    dist1 = group_results[g1]['sentiment_distribution']
                    dist2 = group_results[g2]['sentiment_distribution']
                    
                    if dist1 and dist2:
                        dom1 = max(dist1, key=dist1.get)
                        dom2 = max(dist2, key=dist2.get)
                        
                        if dom1 != dom2:
                            insights.append(f"{g1}主要表现为{dom1}情感，而{g2}主要表现为{dom2}情感")
                    
                    # 比较情感强度
                    int1 = group_results[g1]['average_intensity']
                    int2 = group_results[g2]['average_intensity']
                    
                    if abs(int1 - int2) > 0.2:
                        stronger = g1 if int1 > int2 else g2
                        insights.append(f"{stronger}的情感表达强度更高")
        
        return insights


def get_sentiment_analyzer(provider_name: str = None, api_key: str = None, 
                          model: str = None, base_url: str = None):
    """获取情感分析助手实例"""
    import streamlit as st
    from src.llm.base import LLMConfig
    from src.llm.openai import OpenAIProvider
    from src.llm.deepseek import DeepseekProvider
    from src.llm.lm_studio import LMStudioProvider
    
    # 从session state获取配置
    if provider_name is None:
        provider_name = st.session_state.get('llm_provider', 'lm_studio')
    if api_key is None:
        api_key = st.session_state.get('llm_api_key', 'not-needed')
    if model is None:
        model = st.session_state.get('llm_model', 'local-model')
    if base_url is None:
        base_url = st.session_state.get('llm_base_url', 'http://localhost:1234/v1')
    
    config = LLMConfig(
        provider=provider_name,
        model=model,
        api_key=api_key,
        base_url=base_url
    )
    
    # 创建provider
    if provider_name == 'lm_studio':
        provider = LMStudioProvider(config)
    elif provider_name == 'openai':
        provider = OpenAIProvider(config)
    elif provider_name == 'deepseek':
        provider = DeepseekProvider(config)
    else:
        provider = LMStudioProvider(config)
    
    return SentimentAnalyzer(provider)
