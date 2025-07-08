import os
from typing import List, Dict, Optional
import akshare as ak
import pandas as pd
"""
1. 抓取三大会计报表
2. 提取核心财务指标
3. 保存为CSV

备注：
1. 港股没有一三季报，只有年报中报，所以行业对比不考虑季报
"""

# 字段映射表（A股字段, 港股STD_ITEM_NAME, 中文名, 英文名）
FIELD_MAPPING_PROFIT = [
    # A股字段, 港股STD_ITEM_NAME, 中文, 英文
    ("OPERATE_INCOME", "营业额", "营业收入", "Operating Revenue"),
    ("OPERATE_COST", "销售成本", "营业成本", "Operating Cost"),
    ("OPERATE_PROFIT", "营业利润", "营业利润", "Operating Profit"),
    ("TOTAL_PROFIT", "利润总额", "利润总额", "Total Profit"),
    ("NETPROFIT", "年内溢利", "净利润", "Net Profit"),
    ("PARENT_NETPROFIT", "年内溢利", "归母净利润", "Net Profit Attributable to Parent"),
    ("BASIC_EPS", "每股盈利", "基本每股收益", "Basic EPS"),
    ("TOTAL_COMPRE_INCOME", "综合收益总额", "综合收益总额", "Total Comprehensive Income"),
    (None, "毛利", "毛利", "Gross Profit"),
    (None, "营运收入", "营运收入", "Operating Revenue (Alt)"),
]

FIELD_MAPPING_BALANCE = [
    # A股字段, 港股STD_ITEM_NAME, 中文, 英文
    ("MONETARY_CAP", "货币资金", "货币资金", "Monetary Capital"),
    ("ACCT_RCV", "应收账款", "应收账款", "Accounts Receivable"),
    ("INVENTORY", "存货", "存货", "Inventory"),
    ("TOTAL_ASSETS", "资产总额", "资产总额", "Total Assets"),
    ("TOTAL_LIAB", "负债总额", "负债总额", "Total Liabilities"),
    ("TOTAL_EQUITY", "权益总额", "所有者权益合计", "Total Equity"),
    ("PARENT_EQUITY", "股东权益（不含少数股东权益）", "归属于母公司股东权益", "Equity Attributable to Parent"),
    ("MINORITY_EQUITY", "少数股东权益", "少数股东权益", "Minority Equity"),
    ("FIXED_ASSETS", "固定资产", "固定资产", "Fixed Assets"),
    ("INTANGIBLE_ASSETS", "无形资产", "无形资产", "Intangible Assets"),
    ("LONG_TERM_INVEST", "长期投资", "长期投资", "Long-term Investment"),
]

FIELD_MAPPING_CASHFLOW = [
    # A股字段, 港股STD_ITEM_NAME, 中文, 英文
    ("NET_CASH_OPERATE", "经营活动产生的现金流量净额", "经营活动现金流净额", "Net Cash from Operating Activities"),
    ("NET_CASH_INVEST", "投资活动产生的现金流量净额", "投资活动现金流净额", "Net Cash from Investing Activities"),
    ("NET_CASH_FINANCE", "筹资活动产生的现金流量净额", "筹资活动现金流净额", "Net Cash from Financing Activities"),
    ("CASH_EQUI_END", "现金及现金等价物结余", "期末现金及现金等价物余额", "Cash and Cash Equivalents at End of Period"),
    ("CASH_EQUI_BEG", "现金及现金等价物年初结余", "期初现金及现金等价物余额", "Cash and Cash Equivalents at Beginning of Period"),
    ("NET_INCREASE_CASH_EQUI", "现金及现金等价物净增加额", "现金及现金等价物净增加额", "Net Increase in Cash and Cash Equivalents"),
    ("OPERATE_CASH_INFLOW", "经营活动现金流入", "经营活动现金流入", "Operating Cash Inflow"),
    ("OPERATE_CASH_OUTFLOW", "经营活动现金流出", "经营活动现金流出", "Operating Cash Outflow"),
    ("INVEST_CASH_INFLOW", "投资活动现金流入", "投资活动现金流入", "Investing Cash Inflow"),
    ("INVEST_CASH_OUTFLOW", "投资活动现金流出", "投资活动现金流出", "Investing Cash Outflow"),
    ("FINANCE_CASH_INFLOW", "筹资活动现金流入", "筹资活动现金流入", "Financing Cash Inflow"),
    ("FINANCE_CASH_OUTFLOW", "筹资活动现金流出", "筹资活动现金流出", "Financing Cash Outflow"),
]
# 保存三大会计报表映射表为csv

def save_field_mapping_csv():
    os.makedirs("data", exist_ok=True)  # 创建目录（如不存在）
    pd.DataFrame(FIELD_MAPPING_PROFIT, columns=["A股字段", "港股字段", "中文", "英文"]).to_csv("data/field_mapping_profit.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(FIELD_MAPPING_BALANCE, columns=["A股字段", "港股字段", "中文", "英文"]).to_csv("data/field_mapping_balance.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(FIELD_MAPPING_CASHFLOW, columns=["A股字段", "港股字段", "中文", "英文"]).to_csv("data/field_mapping_cashflow.csv", index=False, encoding="utf-8-sig")
    print("已保存字段映射表: data/field_mapping_profit.csv, data/field_mapping_balance.csv, data/field_mapping_cashflow.csv")


def fetch_financial_reports_akshare(code: str, market: str = None) -> Dict[str, Optional[pd.DataFrame]]:
    """
    用akshare爬取三大会计报表，支持A股和港股。
    输入: code（如'00020.HK'或'002594'），market可选（'hk'/'cn'）
    输出: {报表类型: DataFrame}
    """
    result = {}
    # 港股
    if code.endswith('.HK') or (market == 'hk'):
        code_hk = code.replace('.HK', '')
        try:
            income = ak.stock_financial_hk_report_em(stock=code_hk, symbol="利润表", indicator="报告期")
        except Exception as e:
            print(f"港股利润表抓取失败: {e}")
            income = None
        try:
            balance = ak.stock_financial_hk_report_em(stock=code_hk, symbol="资产负债表", indicator="报告期")
        except Exception as e:
            print(f"港股资产负债表抓取失败: {e}")
            balance = None
        try:
            cashflow = ak.stock_financial_hk_report_em(stock=code_hk, symbol="现金流量表", indicator="报告期")
        except Exception as e:
            print(f"港股现金流量表抓取失败: {e}")
            cashflow = None
        result = {"利润表": income, "资产负债表": balance, "现金流量表": cashflow}
    # A股
    else:
        code_cn = code
        if code_cn.isdigit() and len(code_cn) == 6:
            if code_cn.startswith('6'):
                code_cn = f"SH{code_cn}"
            else:
                code_cn = f"SZ{code_cn}"
        try:
            income = ak.stock_profit_sheet_by_report_em(symbol=code_cn)
        except Exception as e:
            print(f"A股利润表抓取失败: {e}")
            income = None
        try:
            balance = ak.stock_balance_sheet_by_report_em(symbol=code_cn)
        except Exception as e:
            print(f"A股资产负债表抓取失败: {e}")
            balance = None
        try:
            cashflow = ak.stock_cash_flow_sheet_by_report_em(symbol=code_cn)
        except Exception as e:
            print(f"A股现金流量表抓取失败: {e}")
            cashflow = None
        result = {"利润表": income, "资产负债表": balance, "现金流量表": cashflow}
    return result


def extract_core_financials_a(df: pd.DataFrame) -> pd.DataFrame:
    # 只保留核心字段，自动判断年报/季报/中报
    keep = [
        'REPORT_DATE', 'REPORT_TYPE', 'OPERATE_INCOME', 'OPERATE_COST', 'OPERATE_PROFIT',
        'TOTAL_PROFIT', 'NETPROFIT', 'PARENT_NETPROFIT', 'BASIC_EPS', 'TOTAL_COMPRE_INCOME'
    ]
    df = df.copy()
    for k in keep:
        if k not in df.columns:
            df[k] = None
    return df[keep]

def extract_core_financials_hk(df: pd.DataFrame) -> pd.DataFrame:
    # 只保留核心STD_ITEM_NAME，按FISCAL_YEAR和DATE_TYPE_CODE分类
    keep = ['营业额', '营运收入', '销售成本', '毛利', '营业利润', '利润总额', '年内溢利', '每股盈利', '综合收益总额']
    df_core = df[df['STD_ITEM_NAME'].isin(keep)].copy()
    # 透视为宽表，index为FISCAL_YEAR+DATE_TYPE_CODE（如有），columns为STD_ITEM_NAME
    if 'DATE_TYPE_CODE' in df_core.columns:
        wide = df_core.pivot_table(index=['FISCAL_YEAR', 'DATE_TYPE_CODE'], columns='STD_ITEM_NAME', values='AMOUNT', aggfunc='first').reset_index()
    else:
        wide = df_core.pivot_table(index=['FISCAL_YEAR'], columns='STD_ITEM_NAME', values='AMOUNT', aggfunc='first').reset_index()
    return wide

# 工具函数：字段英文/代码转中文

def replace_columns_with_chinese(df: pd.DataFrame, mapping: list) -> pd.DataFrame:
    col_map = {a: c for a, _, c, _ in mapping if a}  # A股字段->中文
    # 港股STD_ITEM_NAME直接就是中文
    # 先尝试A股字段映射
    df = df.copy()
    df.columns = [col_map.get(col, col) for col in df.columns]
    return df

# 保存分表和总表，全部用中文字段，分文件夹

def save_financial_reports(data: Dict[str, Optional[pd.DataFrame]], 
                        code: str, 
                        out_dir: str = "data",
                        is_hk: bool = False):
    """
    保存三大会计报表到CSV，按时间分段，字段全部中文，分文件夹存储。
    A股按REPORT_DATE+REPORT_TYPE，港股按FISCAL_YEAR+DATE_TYPE_CODE。
    """
    code = code.replace('.HK', '')[:6] if code.endswith('.HK') else code[:6]  # 统一股票代码格式，取前6位
    base_dir = os.path.join(out_dir, code, "financial_reports")  # 构建存储目录
    os.makedirs(base_dir, exist_ok=True)  # 创建目录（如不存在）
    report_types = {
        "利润表": FIELD_MAPPING_PROFIT,
        "资产负债表": FIELD_MAPPING_BALANCE,
        "现金流量表": FIELD_MAPPING_CASHFLOW,
    }
    for report_name, mapping in report_types.items():
        df = data.get(report_name)
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            continue
        # 字段替换为中文
        # df_cn = replace_columns_with_chinese(df, mapping)
        # 保存总表
        df.to_csv(os.path.join(base_dir, f"{report_name}.csv"), index=False, encoding="utf-8-sig")
        # 财报表格本身已经有完整的字段，不需要多余的行号列，且会影响后续数据处理。


        # 分表存储
        # sub_dir = os.path.join(base_dir, report_name)
        # os.makedirs(sub_dir, exist_ok=True)
        # if not is_hk:  # A股
        #     # 按REPORT_DATE+REPORT_TYPE分组
        #     if 'REPORT_DATE' in df.columns and 'REPORT_TYPE' in df.columns:
        #         for _, row in df.iterrows():
        #             date = str(row.get('REPORT_DATE', ''))[:10]
        #             rtype = str(row.get('REPORT_TYPE', ''))
        #             fname = f"{report_name}_{date}_{rtype}.csv"
        #             row_cn = replace_columns_with_chinese(row.to_frame().T, mapping)
        #             row_cn.to_csv(os.path.join(sub_dir, fname), index=False, encoding="utf-8-sig")
        # else:  # 港股
        #     # 按FISCAL_YEAR+DATE_TYPE_CODE分组
        #     if 'FISCAL_YEAR' in df.columns:
        #         for _, row in df.iterrows():
        #             year = str(row.get('FISCAL_YEAR', ''))
        #             dtype = str(row.get('DATE_TYPE_CODE', '')) if 'DATE_TYPE_CODE' in row else ''
        #             if dtype and dtype != 'nan':
        #                 fname = f"{report_name}_{year}_{dtype}.csv"
        #             else:
        #                 fname = f"{report_name}_{year}.csv"
        #             row_cn = replace_columns_with_chinese(row.to_frame().T, mapping)
        #             row_cn.to_csv(os.path.join(sub_dir, fname), index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    save_field_mapping_csv()
    # 继续原有批量抓取逻辑
    codes = ["00020.HK", "002594", "600519"]
    for code in codes:
        print(f"抓取{code}三大会计报表...")
        reports = fetch_financial_reports_akshare(code)  # 抓取三大会计报表
        save_financial_reports(reports, code)
        for k, v in reports.items():
            print(f"{code} {k}: {type(v)}, 行数: {getattr(v, 'shape', None)}")
