import os
from typing import List, Dict

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../reference/fundamental')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../reference/public_opinion')))

# 导入深交所、上交所、东方财富爬虫主函数
try:
    from szse_crawler import crawl_szse
    from sse_crawler import crawl_sse
except ImportError:
    crawl_szse = None
    crawl_sse = None

try:
    from eastmoney_crawler import crawl_eastmoney
except ImportError:
    crawl_eastmoney = None

# 统一公告抓取接口

def fetch_announcements_szse(stock_code: str, **kwargs) -> List[Dict]:
    """
    调用reference/fundamental/szse_crawler.py的crawl_szse函数抓取深交所公告
    """
    if crawl_szse is None:
        print("未找到深交所爬虫实现")
        return []
    return crawl_szse(stock_code, **kwargs) or []

def fetch_announcements_sse(stock_code: str, **kwargs) -> List[Dict]:
    """
    调用reference/fundamental/sse_crawler.py的crawl_sse函数抓取上交所公告
    """
    if crawl_sse is None:
        print("未找到上交所爬虫实现")
        return []
    return crawl_sse(stock_code, **kwargs) or []

def fetch_announcements_eastmoney(stock_code: str, **kwargs) -> List[Dict]:
    """
    调用reference/public_opinion/eastmoney_crawler.py的crawl_eastmoney函数抓取东方财富公告
    """
    if crawl_eastmoney is None:
        print("未找到东方财富爬虫实现")
        return []
    return crawl_eastmoney(stock_code, **kwargs) or []

# 可继续添加其他数据源爬虫函数

if __name__ == "__main__":
    # 示例：抓取商汤科技、比亚迪公告
    companies = {"00020.HK": "商汤科技", "002594.SZ": "比亚迪"}
    for code, name in companies.items():
        print(f"抓取{name}（{code}）的公告...")
        results_szse = fetch_announcements_szse(code)
        print(f"深交所公告数：{len(results_szse)}")
        results_sse = fetch_announcements_sse(code)
        print(f"上交所公告数：{len(results_sse)}")
        results_em = fetch_announcements_eastmoney(code)
        print(f"东方财富公告数：{len(results_em)}") 