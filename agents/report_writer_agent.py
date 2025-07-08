from typing import Dict

def generate_report_content(analysis: Dict) -> str:
    """
    输入: 财报分析结果dict
    输出: 结构化文本
    """
    lines = ["# 财务分析摘要"]
    for k, v in analysis.items():
        lines.append(f"{k}: {v}")
    return "\n".join(lines) 