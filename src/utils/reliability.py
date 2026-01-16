"""
编码者间信度计算工具
支持Cohen's Kappa, Krippendorff's Alpha, 百分比一致性等指标
"""
from typing import List, Dict, Tuple
import numpy as np
from collections import defaultdict


def calculate_agreement_matrix(coder1_codes: List[str], coder2_codes: List[str]) -> Dict:
    """
    计算两个编码者的一致性矩阵
    
    Args:
        coder1_codes: 编码者1的编码列表
        coder2_codes: 编码者2的编码列表
        
    Returns:
        包含一致性矩阵和统计信息的字典
    """
    if len(coder1_codes) != len(coder2_codes):
        raise ValueError("两个编码者的编码数量必须相同")
    
    # 获取所有唯一编码
    all_codes = sorted(set(coder1_codes + coder2_codes))
    n = len(all_codes)
    
    # 创建编码到索引的映射
    code_to_idx = {code: idx for idx, code in enumerate(all_codes)}
    
    # 初始化混淆矩阵
    matrix = np.zeros((n, n), dtype=int)
    
    # 填充矩阵
    for c1, c2 in zip(coder1_codes, coder2_codes):
        i = code_to_idx[c1]
        j = code_to_idx[c2]
        matrix[i, j] += 1
    
    return {
        'matrix': matrix,
        'codes': all_codes,
        'code_to_idx': code_to_idx,
        'total_items': len(coder1_codes)
    }


def calculate_percent_agreement(coder1_codes: List[str], coder2_codes: List[str]) -> float:
    """
    计算百分比一致性
    
    Args:
        coder1_codes: 编码者1的编码列表
        coder2_codes: 编码者2的编码列表
        
    Returns:
        百分比一致性 (0-1)
    """
    if len(coder1_codes) != len(coder2_codes):
        raise ValueError("两个编码者的编码数量必须相同")
    
    agreements = sum(1 for c1, c2 in zip(coder1_codes, coder2_codes) if c1 == c2)
    return agreements / len(coder1_codes)


def calculate_cohens_kappa(coder1_codes: List[str], coder2_codes: List[str]) -> Dict:
    """
    计算Cohen's Kappa系数
    
    Args:
        coder1_codes: 编码者1的编码列表
        coder2_codes: 编码者2的编码列表
        
    Returns:
        包含Kappa系数和解释的字典
    """
    if len(coder1_codes) != len(coder2_codes):
        raise ValueError("两个编码者的编码数量必须相同")
    
    n = len(coder1_codes)
    
    # 计算观察到的一致性
    po = calculate_percent_agreement(coder1_codes, coder2_codes)
    
    # 计算期望的一致性
    # 统计每个编码的频率
    from collections import Counter
    c1_counts = Counter(coder1_codes)
    c2_counts = Counter(coder2_codes)
    
    all_codes = set(coder1_codes + coder2_codes)
    pe = 0
    for code in all_codes:
        p1 = c1_counts[code] / n
        p2 = c2_counts[code] / n
        pe += p1 * p2
    
    # 计算Kappa
    if pe == 1:
        kappa = 1.0
    else:
        kappa = (po - pe) / (1 - pe)
    
    # 解释Kappa值
    if kappa < 0:
        interpretation = "差（小于偶然一致性）"
    elif kappa < 0.2:
        interpretation = "轻微一致"
    elif kappa < 0.4:
        interpretation = "一般一致"
    elif kappa < 0.6:
        interpretation = "中等一致"
    elif kappa < 0.8:
        interpretation = "高度一致"
    else:
        interpretation = "几乎完全一致"
    
    return {
        'kappa': kappa,
        'observed_agreement': po,
        'expected_agreement': pe,
        'interpretation': interpretation,
        'n_items': n
    }


def calculate_krippendorffs_alpha(codings: List[List[str]], 
                                  missing_value: str = None) -> Dict:
    """
    计算Krippendorff's Alpha系数（支持多个编码者）
    
    Args:
        codings: 编码矩阵，每行是一个编码者的编码
        missing_value: 缺失值标记
        
    Returns:
        包含Alpha系数和统计信息的字典
    """
    # 转换为numpy数组
    n_coders = len(codings)
    n_items = len(codings[0])
    
    # 检查维度一致性
    for coding in codings:
        if len(coding) != n_items:
            raise ValueError("所有编码者的编码数量必须相同")
    
    # 获取所有唯一值
    all_values = set()
    for coding in codings:
        all_values.update([c for c in coding if c != missing_value])
    all_values = sorted(all_values)
    
    # 创建值到索引的映射
    value_to_idx = {v: i for i, v in enumerate(all_values)}
    n_values = len(all_values)
    
    # 计算coincidence matrix
    coincidence = np.zeros((n_values, n_values))
    
    for item_idx in range(n_items):
        # 获取该项目的所有非缺失编码
        item_codings = [codings[coder][item_idx] for coder in range(n_coders)
                       if codings[coder][item_idx] != missing_value]
        
        m = len(item_codings)  # 该项目的编码者数量
        
        if m < 2:
            continue
        
        # 更新coincidence matrix
        for i, c1 in enumerate(item_codings):
            for c2 in item_codings[i:]:
                idx1 = value_to_idx[c1]
                idx2 = value_to_idx[c2]
                
                if c1 == c2:
                    coincidence[idx1, idx2] += 1 / (m - 1)
                else:
                    weight = 1 / (m - 1)
                    coincidence[idx1, idx2] += weight / 2
                    coincidence[idx2, idx1] += weight / 2
    
    # 计算observed disagreement
    n_c = np.sum(coincidence)
    if n_c == 0:
        return {
            'alpha': 0.0,
            'observed_disagreement': 1.0,
            'expected_disagreement': 1.0,
            'interpretation': '无有效编码',
            'n_items': n_items,
            'n_coders': n_coders
        }
    
    d_o = 0
    for i in range(n_values):
        for j in range(n_values):
            if i != j:
                d_o += coincidence[i, j] * (i - j) ** 2
    d_o = d_o / n_c
    
    # 计算expected disagreement
    n_k = np.sum(coincidence, axis=1)
    d_e = 0
    for i in range(n_values):
        for j in range(n_values):
            if i != j:
                d_e += n_k[i] * n_k[j] * (i - j) ** 2
    d_e = d_e / (n_c * (n_c - 1))
    
    # 计算Alpha
    if d_e == 0:
        alpha = 1.0
    else:
        alpha = 1 - (d_o / d_e)
    
    # 解释Alpha值
    if alpha < 0.667:
        interpretation = "不可靠"
    elif alpha < 0.8:
        interpretation = "可接受"
    else:
        interpretation = "可靠"
    
    return {
        'alpha': alpha,
        'observed_disagreement': d_o,
        'expected_disagreement': d_e,
        'interpretation': interpretation,
        'n_items': n_items,
        'n_coders': n_coders
    }


def compare_multiple_coders(codings_dict: Dict[str, List[str]]) -> Dict:
    """
    比较多个编码者的编码
    
    Args:
        codings_dict: {编码者名称: 编码列表}
        
    Returns:
        包含所有指标的比较结果
    """
    coder_names = list(codings_dict.keys())
    codings = list(codings_dict.values())
    
    results = {
        'coder_names': coder_names,
        'n_coders': len(coder_names),
        'n_items': len(codings[0]),
        'pairwise_comparisons': {},
        'overall_reliability': {}
    }
    
    # 两两比较
    for i in range(len(coder_names)):
        for j in range(i + 1, len(coder_names)):
            name1, name2 = coder_names[i], coder_names[j]
            pair_key = f"{name1}_vs_{name2}"
            
            results['pairwise_comparisons'][pair_key] = {
                'percent_agreement': calculate_percent_agreement(codings[i], codings[j]),
                'cohens_kappa': calculate_cohens_kappa(codings[i], codings[j])
            }
    
    # 整体可靠性（如果有3个或以上编码者）
    if len(coder_names) >= 2:
        results['overall_reliability'] = calculate_krippendorffs_alpha(codings)
    
    return results


def identify_disagreements(coder1_codes: List[str], coder2_codes: List[str],
                          text_fragments: List[str] = None) -> List[Dict]:
    """
    识别编码不一致的位置
    
    Args:
        coder1_codes: 编码者1的编码列表
        coder2_codes: 编码者2的编码列表
        text_fragments: 对应的文本片段（可选）
        
    Returns:
        不一致位置的列表
    """
    disagreements = []
    
    for idx, (c1, c2) in enumerate(zip(coder1_codes, coder2_codes)):
        if c1 != c2:
            disagreement = {
                'index': idx,
                'coder1_code': c1,
                'coder2_code': c2,
            }
            if text_fragments and idx < len(text_fragments):
                disagreement['text'] = text_fragments[idx]
            disagreements.append(disagreement)
    
    return disagreements
