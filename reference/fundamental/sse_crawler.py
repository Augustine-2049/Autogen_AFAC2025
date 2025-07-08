#!/usr/bin/env python3
"""
上交所600519高级公告爬虫
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
        # screenshot_file = f"financial/{code}/sse_{code}_screenshot.png"
        ensure_dir("financial/600519")
        # driver.save_screenshot(screenshot_file)
        # print(f"页面截图已保存: {screenshot_file}")
        
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
        'Referer': 'https://www.sse.com.cn/',
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
    
    if table_id:
        return f"表格_{index+1}_{table_id}"
    elif table_class:
        # 过滤掉通用的class名
        meaningful_classes = [cls for cls in table_class if cls not in ['table', 'table-hover', 'table-striped']]
        if meaningful_classes:
            return f"表格_{index+1}_{'_'.join(meaningful_classes[:2])}"  # 只取前2个有意义的class
        else:
            return f"表格_{index+1}"
    else:
        return f"表格_{index+1}"

def extract_table_data(table):
    """提取表格数据，若包含链接则链接单独成列"""
    rows = table.find_all('tr')
    if not rows:
        return []

    table_data = []
    has_links = False
    link_col_indices = set()

    # 检查表格是否包含链接，并记录哪些列有链接
    for row in rows:
        cells = row.find_all(['td', 'th'])
        for idx, cell in enumerate(cells):
            if cell.find('a'):
                has_links = True
                link_col_indices.add(idx)
        if has_links:
            break

    for row_idx, row in enumerate(rows):
        cells = row.find_all(['td', 'th'])
        if not cells:
            continue

        row_data = []
        for idx, cell in enumerate(cells):
            if has_links and idx in link_col_indices:
                # 提取文本和链接
                cell_info = extract_cell_with_links(cell)
                # 表头行特殊处理
                if row_idx == 0:
                    row_data.append(cell_info['text'] or '')
                    row_data.append('公告链接')
                else:
                    row_data.append(cell_info['text'] or '')
                    if cell_info['links']:
                        row_data.append(cell_info['links'][0]['url'])
                    else:
                        row_data.append('')
            else:
                # 普通表格，只提取文本
                cell_text = extract_cell_text(cell)
                row_data.append(cell_text)
        if row_data:
            table_data.append(row_data)
    return table_data

def extract_cell_text(cell):
    """提取单元格文本，包括链接文本"""
    # 查找链接
    links = cell.find_all('a')
    if links:
        # 如果有链接，返回链接文本
        link_texts = [link.get_text(strip=True) for link in links]
        return ' | '.join(link_texts)
    else:
        # 否则返回普通文本
        return cell.get_text(strip=True)

def extract_cell_with_links(cell):
    """提取单元格文本和链接信息"""
    result = {
        'text': cell.get_text(strip=True),
        'links': []
    }
    
    # 查找链接
    links = cell.find_all('a')
    for link in links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        # 处理相对链接
        if href.startswith('//'):
            href = 'https:' + href
        elif href.startswith('/'):
            href = 'https://www.sse.com.cn' + href
        
        result['links'].append({
            'text': text,
            'url': href
        })
    
    return result

def save_table_to_csv(table_info, base_dir):
    """保存单个表格到CSV文件，公告表格缺失时间向前填充"""
    if not table_info['data']:
        print(f"  表格 {table_info['index']} 没有数据，跳过保存")
        return None
    
    # 生成文件名
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', table_info['title'])
    filename = f"{table_info['index']:02d}_{safe_title[:50]}.csv"
    filepath = os.path.join(base_dir, filename)
    
    try:
        # 创建DataFrame
        df = pd.DataFrame(table_info['data'])
        
        # 如果第一行看起来像标题，使用它作为列名
        if df.shape[0] > 0 and df.shape[1] > 0:
            first_row = df.iloc[0]
            if all(isinstance(cell, str) and len(cell) < 50 for cell in first_row):
                df.columns = first_row
                df = df.iloc[1:]  # 删除第一行
        
        # 对公司公告表格做公告时间的向前填充
        if '公告' in table_info['title'] and '公告时间' in df.columns:
            df['公告时间'] = df['公告时间'].replace('', pd.NA).fillna(method='ffill')
        
        # 保存为CSV
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"  已保存: {filename}")
        
        return filepath
        
    except Exception as e:
        print(f"  保存表格 {table_info['index']} 失败: {e}")
        return None

def save_tables_summary(tables_info, base_dir):
    """保存表格信息摘要"""
    summary = {
        'total_tables': len(tables_info),
        'extraction_time': datetime.now().isoformat(),
        'tables': []
    }
    
    for table in tables_info:
        summary['tables'].append({
            'index': table['index'],
            'title': table['title'],
            'rows': table['rows'],
            'columns': table['columns'],
            'filename': f"table_{table['index']:02d}_{re.sub(r'[<>:\"/\\|?*]', '_', table['title'][:50])}.csv"
        })
    
    summary_file = os.path.join(base_dir, "tables_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n表格摘要已保存: {summary_file}")
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("表格提取摘要")
    print("=" * 60)
    print(f"总表格数: {len(tables_info)}")
    print("\n各表格信息:")
    for table in summary['tables']:
        print(f"  表格 {table['index']:2d}: {table['title']} ({table['rows']} 行 x {table['columns']} 列)")
    print("=" * 60)

def analyze_page_content(html_content):
    """分析页面内容结构"""
    print("分析页面内容结构...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 保存完整的HTML
    base_dir = "financial/600519"
    ensure_dir(base_dir)
    
    html_file = os.path.join(base_dir, "sse_600519_complete_page.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"完整页面已保存: {html_file}")
    
    # 分析页面结构
    analysis = {
        'title': soup.title.get_text() if soup.title else '无标题',
        'meta_description': '',
        'links_count': len(soup.find_all('a')),
        'tables_count': len(soup.find_all('table')),
        'forms_count': len(soup.find_all('form')),
        'scripts_count': len(soup.find_all('script')),
        'divs_count': len(soup.find_all('div')),
        'contains_600519': '600519' in html_content,
        'contains_茅台': '茅台' in html_content,
        'contains_公告': '公告' in html_content,
        'contains_company': 'company' in html_content.lower(),
        'contains_announcement': 'announcement' in html_content.lower()
    }
    
    # 获取meta描述
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        analysis['meta_description'] = meta_desc.get('content', '')
    
    # 查找所有包含600519的文本
    text_elements = soup.find_all(text=re.compile(r'600519|茅台|贵州茅台'))
    analysis['600519_mentions'] = len(text_elements)
    
    # 查找所有链接
    all_links = soup.find_all('a', href=True)
    analysis['all_links'] = []
    
    for link in all_links[:20]:  # 只保存前20个链接
        href = link.get('href', '')
        text = link.get_text(strip=True)
        analysis['all_links'].append({
            'href': href,
            'text': text
        })
    
    # 保存分析结果
    analysis_file = os.path.join(base_dir, "page_analysis.json")
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"页面分析已保存: {analysis_file}")
    
    # 打印分析结果
    print("\n页面分析结果:")
    print(f"标题: {analysis['title']}")
    print(f"链接数量: {analysis['links_count']}")
    print(f"表格数量: {analysis['tables_count']}")
    print(f"脚本数量: {analysis['scripts_count']}")
    print(f"包含600519: {analysis['contains_600519']}")
    print(f"包含茅台: {analysis['contains_茅台']}")
    print(f"包含公告: {analysis['contains_公告']}")
    print(f"600519提及次数: {analysis['600519_mentions']}")
    
    return analysis

def extract_announcements_from_content(html_content):
    """从页面内容中提取公告信息"""
    print("提取公告信息...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    announcements = []
    
    # 方法1: 查找包含公告关键词的链接
    announcement_keywords = ['公告', '年报', '季报', '半年报', '报告', '通知', '披露']
    
    all_links = soup.find_all('a', href=True)
    for link in all_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        # 检查是否包含公告关键词
        if any(keyword in text for keyword in announcement_keywords):
            # 构建完整URL
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                full_url = f"https://www.sse.com.cn{href}"
            else:
                full_url = f"https://www.sse.com.cn/{href}"
            
            # 提取日期
            date = extract_date_from_text(text)
            
            announcements.append({
                'date': date,
                'title': text,
                'url': full_url,
                'source': '上交所官网',
                'extraction_method': '关键词匹配'
            })
    
    # 方法2: 查找表格中的公告信息
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            for cell in cells:
                cell_text = cell.get_text(strip=True)
                if any(keyword in cell_text for keyword in announcement_keywords):
                    # 查找同一行中的链接
                    links = row.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        if href.startswith('http'):
                            full_url = href
                        elif href.startswith('/'):
                            full_url = f"https://www.sse.com.cn{href}"
                        else:
                            full_url = f"https://www.sse.com.cn/{href}"
                        
                        date = extract_date_from_text(cell_text)
                        
                        announcements.append({
                            'date': date,
                            'title': text,
                            'url': full_url,
                            'source': '上交所官网',
                            'extraction_method': '表格解析'
                        })
    
    # 方法3: 查找包含600519的特定内容
    text_elements = soup.find_all(text=re.compile(r'600519|茅台|贵州茅台'))
    for element in text_elements:
        parent = element.parent
        if parent and parent.name == 'a':
            href = parent.get('href', '')
            text = parent.get_text(strip=True)
            
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                full_url = f"https://www.sse.com.cn{href}"
            else:
                full_url = f"https://www.sse.com.cn/{href}"
            
            date = extract_date_from_text(text)
            
            announcements.append({
                'date': date,
                'title': text,
                'url': full_url,
                'source': '上交所官网',
                'extraction_method': '600519相关'
            })
    
    # 去重
    unique_announcements = []
    seen_titles = set()
    for announcement in announcements:
        if announcement['title'] not in seen_titles:
            unique_announcements.append(announcement)
            seen_titles.add(announcement['title'])
    
    return unique_announcements

def extract_date_from_text(text):
    """从文本中提取日期"""
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{4}/\d{2}/\d{2})',
        r'(\d{4}年\d{2}月\d{2}日)',
        r'(\d{2}-\d{2})',
        r'(\d{2}/\d{2})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return ""

def fill_missing_dates(announcements):
    """填充缺失的日期"""
    print("填充缺失的日期...")
    
    last_date = ""
    for announcement in announcements:
        if announcement['date']:
            last_date = announcement['date']
        elif last_date:
            announcement['date'] = last_date
    
    return announcements

def save_to_csv(announcements, filename):
    """保存为CSV文件"""
    if not announcements:
        print("没有公告数据可保存")
        return
    
    # 创建DataFrame
    df = pd.DataFrame(announcements)
    
    # 重新排列列顺序
    columns = ['date', 'title', 'url', 'source', 'extraction_method']
    df = df[columns]
    
    # 保存为CSV
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"公告数据已保存到: {filename}")
    
    # 显示前几行数据
    print("\n前5条公告数据:")
    print(df.head().to_string(index=False))

def crawl_sse(stock_code, logger=None, max_tables=None, save_analysis=True):
    """
    爬取上交所指定股票代码的表格数据
    
    Args:
        stock_code (str): 股票代码，如 '600519'
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
        log_info(f"开始爬取上交所 {stock_code} 的表格数据...")
        
        # 构建URL
        url = f"https://www.sse.com.cn/assortment/stock/list/info/company/index.shtml?COMPANY_CODE={stock_code}"
        
        # 获取页面内容
        html_content = get_page_with_selenium(url, stock_code)
        if not html_content:
            error_msg = f"获取上交所 {stock_code} 页面失败"
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

def crawl_sse_multiple(stock_codes, logger=None, max_tables=None, save_analysis=True):
    """
    批量爬取多个股票代码的上交所表格数据
    
    Args:
        stock_codes (list): 股票代码列表，如 ['600519', '000001']
        logger: 日志记录器，可选
        max_tables (int): 每个股票最大提取表格数量
        save_analysis (bool): 是否保存页面分析结果
    
    Returns:
        list: 每个股票的爬取结果列表
    """
    results = []
    
    for stock_code in stock_codes:
        if len(stock_code) != 6 or stock_code[0] != '6':
            continue
        result = crawl_sse(stock_code, logger, max_tables, save_analysis)
        results.append(result)
        
        # 添加延迟，避免请求过于频繁
        import time
        time.sleep(2)
    
    return results

# 使用示例
if __name__ == "__main__":
    # 单个股票爬取
    # result = crawl_sse('600519')
    # print(f"爬取结果: {result}")
    
    # 批量爬取
    code_list = ['002594', '300474', '600036', '688981']
    results = crawl_sse_multiple(code_list)
    for result in results:
        print(f"{result['stock_code']}: {'成功' if result['success'] else '失败'}") 