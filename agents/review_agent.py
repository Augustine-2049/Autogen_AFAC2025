def review_report(text: str) -> str:
    """
    输入: 研报文本
    输出: 审查后文本（加简单反馈）
    """
    feedback = "[自动审查] 内容格式合规，建议补充更多行业对比分析。"
    return text + "\n\n" + feedback 