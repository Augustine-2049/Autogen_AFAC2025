#!/usr/bin/env python3
"""
调试深交所页面结构
"""

import requests
from bs4 import BeautifulSoup
import json
import time

# 尝试导入Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("警告: Selenium未安装")

def analyze_szse_page(stock_code):
    """分析深交所页面结构"""
    url = f"http://www.szse.cn/disclosure/listed/notice/index.html?stock={stock_code}"
    
    if SELENIUM_AVAILABLE:
        # 使用Selenium获取页面
        print("使用Selenium获取页面...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            print(f"正在访问: {url}")
            driver.get(url)
            
            # 等待页面加载
            print("等待页面加载...")
            time.sleep(5)
            
            html_content = driver.page_source
        
            # 保存原始HTML用于分析
            with open(f"szse_{stock_code}_debug.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 分析表格结构
            tables = soup.find_all('table')
            print(f"找到 {len(tables)} 个表格")
            
            for i, table in enumerate(tables):
                print(f"\n=== 表格 {i+1} 分析 ===")
                
                # 查找表头行
                header_rows = table.find_all('tr', class_='header') or table.find_all('th')
                if header_rows:
                    print("表头行:")
                    for header_row in header_rows:
                        cells = header_row.find_all(['th', 'td'])
                        header_texts = [cell.get_text(strip=True) for cell in cells]
                        print(f"  {header_texts}")
                
                # 查找数据行
                data_rows = table.find_all('tr')
                print(f"数据行数量: {len(data_rows)}")
                
                if data_rows:
                    # 分析前几行
                    for j, row in enumerate(data_rows[:3]):
                        cells = row.find_all(['th', 'td'])
                        if cells:
                            row_texts = []
                            for cell in cells:
                                text = cell.get_text(strip=True)
                                links = cell.find_all('a')
                                if links:
                                    text += f" [链接: {len(links)}个]"
                                row_texts.append(text)
                            print(f"  行 {j+1}: {row_texts}")
                
                # 分析表格属性
                table_attrs = {
                    'id': table.get('id', ''),
                    'class': table.get('class', []),
                    'style': table.get('style', '')
                }
                print(f"表格属性: {table_attrs}")
            
            return html_content
        except Exception as e:
            print(f"Selenium获取页面失败: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    else:
        # 使用requests获取页面
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'http://www.szse.cn/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        try:
            print(f"正在获取页面: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            html_content = response.text
        
            # 保存原始HTML用于分析
            with open(f"szse_{stock_code}_debug.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 分析表格结构
            tables = soup.find_all('table')
            print(f"找到 {len(tables)} 个表格")
            
            for i, table in enumerate(tables):
                print(f"\n=== 表格 {i+1} 分析 ===")
                
                # 查找表头行
                header_rows = table.find_all('tr', class_='header') or table.find_all('th')
                if header_rows:
                    print("表头行:")
                    for header_row in header_rows:
                        cells = header_row.find_all(['th', 'td'])
                        header_texts = [cell.get_text(strip=True) for cell in cells]
                        print(f"  {header_texts}")
                
                # 查找数据行
                data_rows = table.find_all('tr')
                print(f"数据行数量: {len(data_rows)}")
                
                if data_rows:
                    # 分析前几行
                    for j, row in enumerate(data_rows[:3]):
                        cells = row.find_all(['th', 'td'])
                        if cells:
                            row_texts = []
                            for cell in cells:
                                text = cell.get_text(strip=True)
                                links = cell.find_all('a')
                                if links:
                                    text += f" [链接: {len(links)}个]"
                                row_texts.append(text)
                            print(f"  行 {j+1}: {row_texts}")
                
                # 分析表格属性
                table_attrs = {
                    'id': table.get('id', ''),
                    'class': table.get('class', []),
                    'style': table.get('style', '')
                }
                print(f"表格属性: {table_attrs}")
            
            return html_content
        
        except Exception as e:
            print(f"获取页面失败: {e}")
            return None

if __name__ == "__main__":
    analyze_szse_page('000001') 