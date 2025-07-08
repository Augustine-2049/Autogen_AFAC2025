#!/usr/bin/env python3
"""
深交所股票公告爬虫
使用Selenium模拟真实浏览器访问，获取完整的页面内容
支持分别提取多个表格到不同的CSV文件
"""

import pandas as pd
import re
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time
import json

# 尝试导入Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("警告: Selenium未安装，将使用requests方式")

import requests

def ensure_dir(path):
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)

def get_page_with_selenium(url, code):
    """使用Selenium获取页面内容"""
    if not SELENIUM_AVAILABLE:
        print("Selenium不可用，使用requests方式")
        return get_page_with_requests(url)
    
    print("使用Selenium获取页面...")
    
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = None
    try:
        # 尝试创建Chrome驱动
        driver = webdriver.Chrome(options=chrome_options)
        
        print(f"正在访问: {url}")
        driver.get(url)
        
        # 等待页面加载
        print("等待页面加载...")
        time.sleep(5)
        
        # 等待特定元素出现（如果有的话）
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except:
            print("等待超时，继续处理...")
        
        # 获取页面内容
        page_source = driver.page_source
        
        # 保存页面截图（用于调试）
        ensure_dir(f"financial/{code}")
        # driver.save_screenshot(f"financial/{code}/szse_{code}_screenshot.png")
        
        return page_source
        
    except Exception as e:
        print(f"Selenium获取页面失败: {e}")
        return get_page_with_requests(url)
    
    finally:
        if driver:
            driver.quit()

def get_page_with_requests(url):
    """使用requests获取页面内容"""
    print("使用requests获取页面...")
    
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
        
        return response.text
        
    except Exception as e:
        print(f"获取页面失败: {e}")
        return None

def extract_all_tables(html_content):
    """提取页面中的所有表格"""
    print("提取页面中的所有表格...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    
    print(f"找到 {len(tables)} 个表格")
    
    extracted_tables = []
    
    for i, table in enumerate(tables):
        if i < 2:
            continue
        print(f"\n处理表格 {i+1}/{len(tables)}...")
        
        # 尝试获取表格标题或上下文信息
        table_title = get_table_title(table, i)
        
        # 提取表格数据
        table_data = extract_table_data(table)
        if table_data:
            extracted_tables.append({
                'index': i + 1,
                'title': table_title,
                'data': table_data,
                'rows': len(table_data),
                'columns': len(table_data[0]) if table_data else 0
            })
            
            print(f"  表格 {i+1}: {table_title} - {len(table_data)} 行, {len(table_data[0]) if table_data else 0} 列")
        else:
            print(f"  表格 {i+1}: 空表格或无法解析")
    
    return extracted_tables

def get_table_title(table, index):
    """获取表格标题或上下文信息"""
    # 方法1: 查找表格前的h1-h6标题元素
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        prev_title = table.find_previous(tag)
        if prev_title:
            title = prev_title.get_text(strip=True)
            if title and len(title) < 100 and not title.isdigit():  # 避免过长的文本和纯数字
                return title
    
    # 方法2: 查找表格的caption
    caption = table.find('caption')
    if caption:
        title = caption.get_text(strip=True)
        if title and len(title) < 100:
            return title
    
    # 方法3: 查找表格父级容器中的标题元素
    parent = table.parent
    for _ in range(3):  # 向上查找3层父级
        if parent:
            # 查找当前父级中的标题元素
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                title_elem = parent.find(tag)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) < 100 and not title.isdigit():
                        return title
            
            # 查找包含"title"的class或id
            if hasattr(parent, 'get'):
                parent_class = parent.get('class', [])
                parent_id = parent.get('id', '')
                
                if parent_class:
                    for cls in parent_class:
                        if 'title' in cls.lower() and len(cls) < 50:
                            return cls
                
                if parent_id and 'title' in parent_id.lower():
                    return parent_id
            
            parent = parent.parent
    
    # 方法4: 查找表格的id或class
    table_id = table.get('id', '')
    table_class = table.get('class', [])
    
    if table_id and len(table_id) < 50:
        return table_id
    
    if table_class:
        for cls in table_class:
            if len(cls) < 50 and not cls.isdigit():
                return cls
    
    # 方法5: 根据表格内容推断标题
    # 查找表格中的第一行，看是否包含标题信息
    first_row = table.find('tr')
    if first_row:
        first_cell = first_row.find(['th', 'td'])
        if first_cell:
            cell_text = first_cell.get_text(strip=True)
            if cell_text and len(cell_text) < 50:
                return cell_text
    
    # 默认标题
    return f"表格_{index + 1}"

def extract_table_data(table):
    """提取表格数据"""
    rows = []
    
    # 查找所有行
    table_rows = table.find_all('tr')
    
    # 首先分析表格结构，确定最大列数
    max_columns = 0
    for row in table_rows:
        cells = row.find_all(['th', 'td'])
        if cells:
            # 计算这一行的实际列数（包括可能的链接列）
            row_columns = 0
            for cell in cells:
                cell_text, cell_link = extract_cell_with_links(cell)
                row_columns += 1  # 文本列
                if cell_link:  # 如果有链接，再加一列
                    row_columns += 1
            max_columns = max(max_columns, row_columns)
    
    # 然后提取数据，确保所有行都有相同的列数
    for row in table_rows:
        cells = row.find_all(['th', 'td'])
        
        if cells:
            row_data = []
            for cell in cells:
                # 检查是否包含链接
                cell_text, cell_link = extract_cell_with_links(cell)
                row_data.append(cell_text)
                
                # 如果有链接，添加到下一列
                if cell_link:
                    row_data.append(cell_link)
            
            # 如果这一行的列数少于最大列数，用空值填充
            while len(row_data) < max_columns:
                row_data.append('')
            print(row_data)
            rows.append(row_data)
    
    return rows

def extract_cell_text(cell):
    """提取单元格文本"""
    # 移除script和style标签
    for script in cell(["script", "style"]):
        script.decompose()
    
    text = cell.get_text(strip=True)
    return text

def extract_cell_with_links(cell):
    """提取单元格文本和链接"""
    # 查找链接
    link = cell.find('a')
    cell_text = extract_cell_text(cell)
    
    if link:
        href = link.get('href', '')
        # 处理相对链接
        if href.startswith('/'):
            href = f"http://www.szse.cn{href}"
        elif href.startswith('./'):
            href = f"http://www.szse.cn{href[1:]}"
        elif not href.startswith('http'):
            href = f"http://www.szse.cn/{href}"
        
        return cell_text, href
    else:
        return cell_text, None

def save_table_to_csv(table_info, base_dir):
    """保存表格到CSV文件"""
    try:
        data = table_info['data']
        title = table_info['title']
        
        if not data:
            print(f"  表格 {table_info['index']} 无数据，跳过保存")
            return None
        
        # 清理文件名
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        safe_title = re.sub(r'\s+', '_', safe_title)
        safe_title = safe_title[:50]  # 限制长度
        
        # 生成文件名
        filename = f"{table_info['index']:02d}_{safe_title}.csv"
        filepath = os.path.join(base_dir, filename)
        
        # 创建DataFrame，使用第一行作为表头
        if data:
            # 使用第一行作为列名
            headers = data[0]
            # 其余行作为数据
            data_rows = data[1:] if len(data) > 1 else []
            df = pd.DataFrame(data_rows, columns=headers)
        else:
            df = pd.DataFrame()
        
        # 如果是公司公告表格（通常包含日期列），处理缺失日期
        if '公告' in title or '公告时间' in str(df.iloc[0] if len(df) > 0 else ''):
            df = fill_missing_dates_in_df(df)
        
        # 保存到CSV
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"  保存表格 {table_info['index']}: {filepath}")
        
        return filepath
        
    except Exception as e:
        print(f"  保存表格 {table_info['index']} 失败: {e}")
        return None

def fill_missing_dates_in_df(df):
    """在DataFrame中填充缺失的日期"""
    if len(df) == 0:
        return df
    
    # 查找日期列（通常是第一列或包含"时间"、"日期"的列）
    date_col = None
    for i, col in enumerate(df.columns):
        if isinstance(col, str) and ('时间' in col or '日期' in col):
            date_col = i
            break
    
    if date_col is None:
        # 如果没有找到明确的日期列，假设第一列是日期
        date_col = 0
    
    # 填充缺失的日期
    last_date = None
    for i in range(len(df)):
        current_date = df.iloc[i, date_col]
        if pd.isna(current_date) or current_date == '' or str(current_date).strip() == '':
            if last_date is not None:
                df.iloc[i, date_col] = last_date
        else:
            last_date = current_date
    
    return df

def save_tables_summary(tables_info, base_dir):
    """保存表格摘要信息"""
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_tables': len(tables_info),
        'tables': []
    }
    
    for table_info in tables_info:
        summary['tables'].append({
            'index': table_info['index'],
            'title': table_info['title'],
            'rows': table_info['rows'],
            'columns': table_info['columns']
        })
    
    summary_file = os.path.join(base_dir, 'tables_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"表格摘要已保存: {summary_file}")

def analyze_page_content(html_content):
    """分析页面内容"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    analysis = {
        'total_tables': len(soup.find_all('table')),
        'total_links': len(soup.find_all('a')),
        'total_images': len(soup.find_all('img')),
        'page_title': soup.title.get_text(strip=True) if soup.title else '无标题',
        'meta_description': '',
        'has_forms': len(soup.find_all('form')) > 0,
        'has_scripts': len(soup.find_all('script')) > 0,
        'has_styles': len(soup.find_all('style')) > 0
    }
    
    # 获取meta描述
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        analysis['meta_description'] = meta_desc.get('content', '')
    
    return analysis

def crawl_szse(stock_code, logger=None, max_tables=None, save_analysis=True):
    """
    爬取深交所指定股票代码的表格数据
    
    Args:
        stock_code (str): 股票代码，如 '000001'
        logger: 日志记录器，可选
        max_tables (int): 最大提取表格数量，None表示提取所有表格
        save_analysis (bool): 是否保存页面分析结果
    
    Returns:
        dict: 包含爬取结果的字典
        {
            'success': bool,
            'stock_code': str,
            'tables_count': int,
            'saved_files': list,
            'base_dir': str,
            'error': str (如果失败)
        }
    """
    def log_info(message):
        if logger:
            logger.info(message)
        else:
            print(message)
    
    def log_error(message):
        if logger:
            logger.error(message)
        else:
            print(f"错误: {message}")
    
    try:
        log_info(f"开始爬取深交所 {stock_code} 的表格数据...")
        
        # 构建深交所URL
        url = f"http://www.szse.cn/disclosure/listed/notice/index.html?stock={stock_code}"
        
        # 获取页面内容
        html_content = get_page_with_selenium(url, stock_code)
        if not html_content:
            error_msg = f"获取深交所 {stock_code} 页面失败"
            log_error(error_msg)
            return {
                'success': False,
                'stock_code': stock_code,
                'tables_count': 0,
                'saved_files': [],
                'base_dir': '',
                'error': error_msg
            }
        
        # 分析页面内容
        if save_analysis:
            analysis = analyze_page_content(html_content)
            log_info(f"页面分析完成，包含 {analysis.get('tables_count', 0)} 个表格")
        
        # 提取所有表格
        log_info("开始提取表格...")
        tables_info = extract_all_tables(html_content)
        
        if not tables_info:
            error_msg = f"未找到任何表格"
            log_error(error_msg)
            return {
                'success': False,
                'stock_code': stock_code,
                'tables_count': 0,
                'saved_files': [],
                'base_dir': '',
                'error': error_msg
            }
        
        
        # 保存表格到CSV文件
        base_dir = f"financial/{stock_code}"
        ensure_dir(base_dir)
        
        log_info(f"保存表格到CSV文件...")
        saved_files = []
        for table_info in tables_info:
            filepath = save_table_to_csv(table_info, base_dir)
            if filepath:
                saved_files.append(filepath)
        
        # 保存表格摘要
        save_tables_summary(tables_info, base_dir)
        
        # 返回结果
        result = {
            'success': True,
            'stock_code': stock_code,
            'tables_count': len(tables_info),
            'saved_files': saved_files,
            'base_dir': base_dir,
            'error': None
        }
        
        log_info("=" * 60)
        log_info(f"爬取 {stock_code} 完成！")
        log_info(f"表格文件保存在: {base_dir}")
        log_info(f"共提取 {len(tables_info)} 个表格")
        log_info(f"成功保存 {len(saved_files)} 个CSV文件")
        log_info("=" * 60)
        
        return result
        
    except Exception as e:
        error_msg = f"爬取 {stock_code} 时发生异常: {str(e)}"
        log_error(error_msg)
        return {
            'success': False,
            'stock_code': stock_code,
            'tables_count': 0,
            'saved_files': [],
            'base_dir': '',
            'error': error_msg
        }

def crawl_szse_multiple(stock_codes, logger=None, max_tables=None, save_analysis=True):
    """
    批量爬取多个股票代码的深交所表格数据
    
    Args:
        stock_codes (list): 股票代码列表，如 ['000001', '000002']
        logger: 日志记录器，可选
        max_tables (int): 每个股票最大提取表格数量
        save_analysis (bool): 是否保存页面分析结果
    
    Returns:
        list: 每个股票的爬取结果列表
    """
    results = []
    
    for stock_code in stock_codes:
        # 深交所股票代码以0开头
        if len(stock_code) != 6 or (stock_code[0] != '0' and stock_code[0] != '3'):
            continue
        result = crawl_szse(stock_code, logger, max_tables, save_analysis)
        results.append(result)
        
        # 添加延迟，避免请求过于频繁
        time.sleep(2)
    
    return results

def fix_szse_table_header(csv_path, save_path=None, header_row=1):
    """
    读取深交所csv表格，将第header_row行作为表头，去除前面多余的行。
    :param csv_path: 原始csv文件路径
    :param save_path: 修正后保存路径，若为None则覆盖原文件
    :param header_row: 作为表头的行号（从0开始，通常为1）
    :return: 修正后的DataFrame
    """
    df_raw = pd.read_csv(csv_path, header=None)
    new_header = df_raw.iloc[header_row]
    df = df_raw[header_row+1:]
    df.columns = new_header
    df = df.reset_index(drop=True)
    if save_path is None:
        save_path = csv_path
    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"已修正表头并保存到: {save_path}")
    return df

def get_total_pages(html_content):
    """从页面内容中获取总页数"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找分页信息
    pagination = soup.find('div', class_='pagination') or soup.find('div', class_='page')
    if pagination:
        # 查找最后一页的链接
        page_links = pagination.find_all('a')
        if page_links:
            last_page = 1
            for link in page_links:
                try:
                    page_num = int(link.get_text(strip=True))
                    last_page = max(last_page, page_num)
                except ValueError:
                    continue
            return last_page
    
    # 如果没有找到分页信息，尝试查找其他分页元素
    page_info = soup.find(text=re.compile(r'共.*页'))
    if page_info:
        match = re.search(r'共(\d+)页', page_info)
        if match:
            return int(match.group(1))
    
    return 1

def crawl_szse_page(stock_code, page=1, logger=None):
    """爬取深交所指定股票代码指定页面的表格数据"""
    def log_info(message):
        if logger:
            logger.info(message)
        else:
            print(message)
    
    try:
        log_info(f"爬取深交所 {stock_code} 第 {page} 页...")
        
        # 构建深交所URL（添加页码参数）
        if page == 1:
            url = f"http://www.szse.cn/disclosure/listed/notice/index.html?stock={stock_code}"
        else:
            url = f"http://www.szse.cn/disclosure/listed/notice/index.html?stock={stock_code}&page={page}"
        
        # 获取页面内容
        html_content = get_page_with_selenium(url, stock_code)
        if not html_content:
            error_msg = f"获取深交所 {stock_code} 第 {page} 页失败"
            log_info(error_msg)
            return None
        
        # 提取所有表格
        tables_info = extract_all_tables(html_content)
        
        if not tables_info:
            log_info(f"第 {page} 页未找到任何表格")
            return None
        
        # 只返回第三个表格（如果存在）
        if len(tables_info) >= 3:
            return tables_info[2]  # 第三个表格（索引为2）
        else:
            log_info(f"第 {page} 页没有第三个表格")
            return None
        
    except Exception as e:
        log_info(f"爬取第 {page} 页时发生异常: {str(e)}")
        return None

def crawl_szse_multiple_pages(stock_code, logger=None, max_pages=None):
    """
    爬取深交所指定股票代码的多页数据，并合并第三个表格
    
    Args:
        stock_code (str): 股票代码，如 '000001'
        logger: 日志记录器，可选
        max_pages (int): 最大爬取页数，None表示爬取所有页面
    
    Returns:
        dict: 包含爬取结果的字典
    """
    def log_info(message):
        if logger:
            logger.info(message)
        else:
            print(message)
    
    try:
        log_info(f"开始爬取深交所 {stock_code} 的多页数据...")
        
        # 先获取第一页，确定总页数
        first_page_tables = crawl_szse_page(stock_code, 1, logger)
        if not first_page_tables:
            return {
                'success': False,
                'stock_code': stock_code,
                'error': '无法获取第一页数据'
            }
        
        # 获取总页数（这里需要根据实际情况调整）
        # 由于深交所可能没有明显的分页信息，我们可以尝试爬取前几页
        total_pages = max_pages if max_pages else 5  # 默认尝试5页
        
        log_info(f"开始爬取 {total_pages} 页数据...")
        
        # 收集所有页面的第三个表格数据
        all_table_data = []
        successful_pages = 0
        
        for page in range(1, total_pages + 1):
            table_info = crawl_szse_page(stock_code, page, logger)
            if table_info and table_info['data']:
                all_table_data.extend(table_info['data'])
                successful_pages += 1
                log_info(f"第 {page} 页成功，获取 {len(table_info['data'])} 行数据")
            else:
                log_info(f"第 {page} 页无数据或失败")
            
            # 添加延迟避免请求过于频繁
            time.sleep(1)
        
        if not all_table_data:
            return {
                'success': False,
                'stock_code': stock_code,
                'error': '所有页面都没有获取到数据'
            }
        
        # 合并数据
        merged_table_info = {
            'index': 3,
            'title': '信息披露_多页合并',
            'data': all_table_data,
            'rows': len(all_table_data),
            'columns': len(all_table_data[0]) if all_table_data else 0
        }
        
        # 保存合并后的表格
        base_dir = f"financial/{stock_code}"
        ensure_dir(base_dir)
        
        filepath = save_table_to_csv(merged_table_info, base_dir)
        
        result = {
            'success': True,
            'stock_code': stock_code,
            'total_pages': total_pages,
            'successful_pages': successful_pages,
            'total_rows': len(all_table_data),
            'saved_file': filepath,
            'base_dir': base_dir,
            'error': None
        }
        
        log_info("=" * 60)
        log_info(f"爬取 {stock_code} 完成！")
        log_info(f"成功爬取 {successful_pages}/{total_pages} 页")
        log_info(f"合并后总行数: {len(all_table_data)}")
        log_info(f"文件保存在: {filepath}")
        log_info("=" * 60)
        
        return result
        
    except Exception as e:
        error_msg = f"爬取 {stock_code} 多页数据时发生异常: {str(e)}"
        log_info(error_msg)
        return {
            'success': False,
            'stock_code': stock_code,
            'error': error_msg
        }

# 使用示例
if __name__ == "__main__":
    # 单个股票多页爬取（推荐）
    result = crawl_szse_multiple_pages('000001', max_pages=10)
    print(f"多页爬取结果: {result}")
    
    # 批量爬取（单页）
    # code_list = ['002594', '300474', '600036', '688981']
    # results = crawl_szse_multiple(code_list)
    # for result in results:
    #     print(f"{result['stock_code']}: {'成功' if result['success'] else '失败'}") 