from typing import Dict
import pandas as pd

def analyze_financial_reports(financial_reports: Dict[str, pd.DataFrame]) -> Dict:
    """
    输入: {报表类型: DataFrame}
    输出: 简单财务摘要（如利润表的营业收入、净利润等均值）
    """
    result = {}
    income = financial_reports.get("利润表")
    if income is not None:
        result["营业收入均值"] = income["营业收入"].mean() if "营业收入" in income.columns else None
        result["净利润均值"] = income["净利润"].mean() if "净利润" in income.columns else None
    return result 