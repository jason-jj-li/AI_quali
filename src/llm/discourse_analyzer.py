"""
话语分析和叙事结构分析工具
"""
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from src.llm.base import LLMProvider


@dataclass
class DiscourseElement:
    """话语元素"""
    text: str
    element_type: str  # claim, evidence, warrant, qualifier, rebuttal
    role: str
    reasoning: str


@dataclass
class NarrativeStructure:
    """叙事结构"""
    orientation: str  # 背景
    complicating_action: str  # 冲突/转折
    evaluation: str  # 评价
    resolution: str  # 解决
    coda: str  # 结语
    narrative_type: str  # 叙事类型


class DiscourseAnalyzer:
    """话语分析助手"""
    
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.system_prompt = """你是一位话语分析专家，擅长识别文本中的论证结构、权力关系和意识形态。

## 分析维度

### 1. 论证结构（Toulmin模型）
- Claim（主张）：核心观点
- Data（数据）：支持证据
- Warrant（保证）：推理依据
- Backing（支撑）：进一步支持
- Qualifier（限定）：程度限制
- Rebuttal（反驳）：反例或限制

### 2. 话语功能
- 描述性话语：客观描述
- 叙事性话语：讲故事
- 论证性话语：说服
- 说明性话语：解释

### 3. 权力关系
- 主导话语：谁的声音更响
- 边缘化话语：被忽视的声音
- 话语权力：谁有定义权

### 4. 意识形态标记
- 价值判断
- 隐含假设
- 规范性陈述

请以JSON格式输出分析结果。"""
    
    def analyze_discourse(self, text: str, focus: str = "argumentation") -> Dict:
        """
        话语分析
        
        Args:
            text: 待分析文本
            focus: 分析焦点（argumentation/power/ideology）
            
        Returns:
            话语分析结果
        """
        if focus == "argumentation":
            prompt = f"""请分析以下文本的论证结构（基于Toulmin模型）：

文本：
```
{text}
```

请识别：
1. 主张（Claims）：作者提出的观点
2. 数据/证据（Data）：支持主张的证据
3. 保证（Warrants）：连接数据和主张的推理
4. 限定语（Qualifiers）：对主张的限定
5. 反驳（Rebuttals）：可能的反对或例外

输出JSON格式：
{{
    "claims": ["主张1", "主张2"],
    "data": ["证据1", "证据2"],
    "warrants": ["推理1", "推理2"],
    "qualifiers": ["限定1"],
    "rebuttals": ["反驳1"],
    "argument_strength": 0.8,
    "analysis": "整体分析"
}}"""
        
        elif focus == "power":
            prompt = f"""请分析以下文本中的权力关系：

文本：
```
{text}
```

请识别：
1. 主导话语：谁的声音占主导？
2. 边缘化声音：哪些观点被忽视？
3. 话语权力：谁有定义问题的权力？
4. 权力动态：权力关系如何展现？

输出JSON格式：
{{
    "dominant_voices": ["主导者1", "主导者2"],
    "marginalized_voices": ["边缘声音1"],
    "power_dynamics": "权力关系描述",
    "discourse_control": "话语控制分析",
    "implications": ["影响1", "影响2"]
}}"""
        
        else:  # ideology
            prompt = f"""请分析以下文本中的意识形态标记：

文本：
```
{text}
```

请识别：
1. 价值判断：隐含的价值观
2. 假设前提：未明说的假设
3. 规范性陈述：应该/不应该
4. 意识形态倾向：背后的意识形态

输出JSON格式：
{{
    "value_judgments": ["价值判断1", "价值判断2"],
    "assumptions": ["假设1", "假设2"],
    "normative_statements": ["规范1", "规范2"],
    "ideological_orientation": "意识形态倾向",
    "analysis": "综合分析"
}}"""
        
        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=1500
            )
            
            return self._parse_json_response(response.content)
        
        except Exception as e:
            return {
                'error': str(e),
                'analysis': '分析失败'
            }
    
    def analyze_conversation(self, conversation: List[Dict[str, str]]) -> Dict:
        """
        会话分析（对话分析）
        
        Args:
            conversation: [{"speaker": "A", "text": "..."}, ...]
            
        Returns:
            会话分析结果
        """
        # 格式化会话
        conv_text = "\n".join([f"{turn['speaker']}: {turn['text']}" 
                               for turn in conversation])
        
        prompt = f"""请分析以下会话的结构和特征：

会话：
```
{conv_text}
```

请识别：
1. 话轮特征：谁说得多？话轮长度？
2. 打断模式：谁打断谁？
3. 话题控制：谁在引导话题？
4. 权力动态：权力关系如何体现？
5. 合作模式：说话者如何互动？

输出JSON格式：
{{
    "turn_taking": {{
        "speaker_stats": {{"A": 5, "B": 3}},
        "interruptions": ["A打断B", "B打断A"]
    }},
    "topic_control": "话题控制分析",
    "power_dynamics": "权力动态分析",
    "cooperation_patterns": ["模式1", "模式2"],
    "analysis": "综合分析"
}}"""
        
        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=1500
            )
            
            result = self._parse_json_response(response.content)
            
            # 添加基础统计
            result['basic_stats'] = {
                'total_turns': len(conversation),
                'speakers': list(set(turn['speaker'] for turn in conversation)),
                'average_turn_length': sum(len(turn['text']) for turn in conversation) / len(conversation)
            }
            
            return result
        
        except Exception as e:
            return {
                'error': str(e),
                'analysis': '分析失败'
            }
    
    def _parse_json_response(self, content: str) -> Dict:
        """解析JSON响应"""
        import re
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            else:
                return {'error': 'JSON解析失败', 'raw_content': content}


class NarrativeAnalyzer:
    """叙事结构分析助手"""
    
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.system_prompt = """你是一位叙事分析专家，擅长识别叙事结构和叙事功能。

## 叙事结构（Labov模型）

1. **定位（Orientation）**：时间、地点、人物、情境
2. **复杂化行动（Complicating Action）**：发生了什么？冲突或转折
3. **评价（Evaluation）**：为什么这个故事值得讲？
4. **解决（Resolution）**：最后发生了什么？
5. **尾声（Coda）**：回到现在

## 叙事类型

- **经历叙事**：个人体验
- **习惯叙事**：重复性事件
- **假设叙事**：可能发生的事
- **集体叙事**：共同经历

请以JSON格式输出分析结果。"""
    
    def analyze_narrative(self, text: str) -> Dict:
        """
        叙事结构分析
        
        Args:
            text: 叙事文本
            
        Returns:
            叙事分析结果
        """
        prompt = f"""请分析以下文本的叙事结构：

文本：
```
{text}
```

请识别：
1. 定位（Orientation）：时间、地点、人物、背景
2. 复杂化行动（Complicating Action）：发生了什么冲突或转折？
3. 评价（Evaluation）：叙述者如何评价这个故事？为什么重要？
4. 解决（Resolution）：问题如何解决？结果是什么？
5. 尾声（Coda）：叙述者的反思或总结

输出JSON格式：
{{
    "orientation": "背景描述",
    "complicating_action": "冲突描述",
    "evaluation": "评价内容",
    "resolution": "解决方式",
    "coda": "尾声反思",
    "narrative_type": "经历叙事|习惯叙事|假设叙事",
    "temporal_structure": "时间结构描述",
    "plot_points": ["关键情节1", "关键情节2"],
    "analysis": "综合分析"
}}"""
        
        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=1500
            )
            
            return self._parse_json_response(response.content)
        
        except Exception as e:
            return {
                'error': str(e),
                'analysis': '分析失败'
            }
    
    def extract_timeline(self, narratives: List[str]) -> Dict:
        """
        从多个叙事中提取时间线
        
        Args:
            narratives: 叙事文本列表
            
        Returns:
            时间线分析
        """
        prompt = f"""请从以下多个叙事中提取时间线：

叙事文本：
{chr(10).join([f'[文本{i+1}] {n[:200]}...' for i, n in enumerate(narratives)])}

请识别：
1. 关键时间点
2. 事件顺序
3. 时间跨度
4. 转折点

输出JSON格式：
{{
    "timeline": [
        {{"time": "2020年", "event": "事件描述", "source": "文本1"}},
        {{"time": "2021年", "event": "事件描述", "source": "文本2"}}
    ],
    "key_turning_points": ["转折点1", "转折点2"],
    "temporal_span": "时间跨度",
    "narrative_arc": "叙事弧线描述"
}}"""
        
        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=2000
            )
            
            return self._parse_json_response(response.content)
        
        except Exception as e:
            return {
                'error': str(e),
                'timeline': []
            }
    
    def compare_narratives(self, narratives_dict: Dict[str, str]) -> Dict:
        """
        比较不同叙事者的叙事
        
        Args:
            narratives_dict: {叙事者: 叙事文本}
            
        Returns:
            叙事对比结果
        """
        narrator_analyses = {}
        
        for narrator, text in narratives_dict.items():
            narrator_analyses[narrator] = self.analyze_narrative(text)
        
        # 生成对比洞察
        prompt = f"""请对比以下不同叙事者的叙事：

{chr(10).join([f'{narrator}: {json.dumps(analysis, ensure_ascii=False)}' 
               for narrator, analysis in narrator_analyses.items()])}

请识别：
1. 叙事差异：不同叙事者的视角差异
2. 共同主题：共同的经历或主题
3. 冲突点：叙事中的矛盾
4. 互补性：叙事如何互补

输出JSON格式：
{{
    "common_themes": ["共同主题1", "共同主题2"],
    "differences": ["差异1", "差异2"],
    "conflicts": ["冲突1", "冲突2"],
    "complementarity": "互补性分析",
    "insights": ["洞察1", "洞察2"]
}}"""
        
        try:
            response = self.provider.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.4,
                max_tokens=1500
            )
            
            comparison = self._parse_json_response(response.content)
            comparison['individual_analyses'] = narrator_analyses
            
            return comparison
        
        except Exception as e:
            return {
                'error': str(e),
                'individual_analyses': narrator_analyses
            }
    
    def _parse_json_response(self, content: str) -> Dict:
        """解析JSON响应"""
        import re
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            else:
                return {'error': 'JSON解析失败', 'raw_content': content}


def get_discourse_analyzer(provider_name: str = None, api_key: str = None,
                          model: str = None, base_url: str = None):
    """获取话语分析助手"""
    import streamlit as st
    from src.llm.base import LLMConfig
    from src.llm.openai import OpenAIProvider
    from src.llm.deepseek import DeepseekProvider
    from src.llm.lm_studio import LMStudioProvider
    
    if provider_name is None:
        provider_name = st.session_state.get('llm_provider', 'lm_studio')
    if api_key is None:
        api_key = st.session_state.get('llm_api_key', 'not-needed')
    if model is None:
        model = st.session_state.get('llm_model', 'local-model')
    if base_url is None:
        base_url = st.session_state.get('llm_base_url', 'http://localhost:1234/v1')
    
    config = LLMConfig(provider=provider_name, model=model, api_key=api_key, base_url=base_url)
    
    if provider_name == 'lm_studio':
        provider = LMStudioProvider(config)
    elif provider_name == 'openai':
        provider = OpenAIProvider(config)
    elif provider_name == 'deepseek':
        provider = DeepseekProvider(config)
    else:
        provider = LMStudioProvider(config)
    
    return DiscourseAnalyzer(provider)


def get_narrative_analyzer(provider_name: str = None, api_key: str = None,
                          model: str = None, base_url: str = None):
    """获取叙事分析助手"""
    import streamlit as st
    from src.llm.base import LLMConfig
    from src.llm.openai import OpenAIProvider
    from src.llm.deepseek import DeepseekProvider
    from src.llm.lm_studio import LMStudioProvider
    
    if provider_name is None:
        provider_name = st.session_state.get('llm_provider', 'lm_studio')
    if api_key is None:
        api_key = st.session_state.get('llm_api_key', 'not-needed')
    if model is None:
        model = st.session_state.get('llm_model', 'local-model')
    if base_url is None:
        base_url = st.session_state.get('llm_base_url', 'http://localhost:1234/v1')
    
    config = LLMConfig(provider=provider_name, model=model, api_key=api_key, base_url=base_url)
    
    if provider_name == 'lm_studio':
        provider = LMStudioProvider(config)
    elif provider_name == 'openai':
        provider = OpenAIProvider(config)
    elif provider_name == 'deepseek':
        provider = DeepseekProvider(config)
    else:
        provider = LMStudioProvider(config)
    
    return NarrativeAnalyzer(provider)
