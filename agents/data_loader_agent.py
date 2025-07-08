import os
import pandas as pd
from typing import Dict

def load_financial_reports(code: str, data_dir: str = "data") -> Dict[str, pd.DataFrame]:
    """
    加载指定公司三大会计报表csv，返回{报表类型: DataFrame}
    """
    base_dir = os.path.join(data_dir, code, "financial_reports")
    result = {}
    for name in ["利润表", "资产负债表", "现金流量表"]:
        path = os.path.join(base_dir, f"{name}.csv")
        if os.path.exists(path):
            result[name] = pd.read_csv(path)
    return result 