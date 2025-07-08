import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
import os
import logging

# 添加父目录到路径，支持相对导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from crawler.logger_config import create_logger
except ImportError:
    # 如果相对导入失败，尝试直接导入
    from logger_config import create_logger

def parse_time_string(time_str):
    """
    解析时间字符串，返回datetime对象
    :param time_str: 时间字符串，如 '07-06 12:32' 或 '07-06'
    :return: datetime对象
    """
    try:
        # 处理不同格式的时间字符串
        if ' ' in time_str:
            # 格式: '07-06 12:32'
            date_part, time_part = time_str.split(' ')
            month, day = map(int, date_part.split('-'))
            hour, minute = map(int, time_part.split(':'))
        else:
            # 格式: '07-06'
            month, day = map(int, time_str.split('-'))
            hour, minute = 0, 0
        
        # 获取当前年份
        current_year = datetime.now().year
        
        # 创建datetime对象
        parsed_time = datetime(current_year, month, day, hour, minute)
        
        # 如果解析出的时间比当前时间还晚，说明是去年的数据
        if parsed_time > datetime.now():
            parsed_time = datetime(current_year - 1, month, day, hour, minute)
            
        return parsed_time
        
    except Exception as e:
        # 如果解析失败，返回None
        return None

def crawl_eastmoney(stock_code, logger=None, max_pages=5, days_limit=7):
    """
    爬取东方财富个股新闻
    :param stock_code: 股票代码，如 '600519'
    :param logger: 日志对象，如果为None则自动创建
    :param max_pages: 最大爬取页数
    :param days_limit: 时间限制，只保留指定天数以内的数据（默认7天）
    :return: DataFrame格式的新闻数据
    """
    if logger is None:
        # 创建日志管理器，控制台只显示警告及以上级别
        logger = create_logger('eastmoney_crawler', console_level=logging.WARNING)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    news_list = []
    successful_pages = 0
    filtered_count = 0
    
    # 计算时间限制
    time_limit = datetime.now() - timedelta(days=days_limit)
    logger.info(f"开始爬取股票 {stock_code} 的新闻，最大页数: {max_pages}，时间限制: {days_limit}天以内")
    logger.info(f"时间限制点: {time_limit.strftime('%Y-%m-%d %H:%M:%S')}")
    
    for page in range(1, max_pages + 1):
        try:
            url = f'http://guba.eastmoney.com/list,{stock_code}_{page}.html'
            logger.info(f"正在爬取第 {page} 页: {url}")
            
            # 记录请求开始时间
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=10)
            response_time = time.time() - start_time
            
            response.raise_for_status()
            
            # 记录请求日志
            logger.log_request(url, response.status_code, response_time)
            logger.debug(f"页面内容长度: {len(response.text)}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 检查页面标题
            title = soup.find('title')
            if title:
                logger.debug(f"页面标题: {title.get_text()}")
            
            # 查找新闻项
            news_items = soup.select('tbody.listbody tr.listitem')
            logger.info(f"第 {page} 页找到 {len(news_items)} 个新闻项")
            
            if len(news_items) > 0:
                page_news_count = 0
                page_filtered_count = 0
                
                for i, item in enumerate(news_items):
                    try:
                        # 提取标题
                        title_element = item.select_one('td:nth-child(3) .title a')
                        if not title_element:
                            logger.warning(f"第 {page} 页第 {i+1} 项未找到标题元素")
                            continue
                        
                        title_text = title_element.get_text(strip=True)
                        link = title_element.get('href', '')
                        
                        # 处理链接
                        if link.startswith('//'):
                            full_link = f'http:{link}'
                        elif link.startswith('/'):
                            full_link = f'http://guba.eastmoney.com{link}'
                        else:
                            full_link = link
                        
                        # 提取作者
                        author_element = item.select_one('td:nth-child(4) .author a')
                        author_text = author_element.get_text(strip=True) if author_element else "未知作者"
                        
                        # 提取时间
                        time_element = item.select_one('td:nth-child(5) .update')
                        time_text = time_element.get_text(strip=True) if time_element else "未知时间"
                        
                        # 解析时间并检查是否在时间限制内
                        parsed_time = parse_time_string(time_text)
                        if parsed_time is None:
                            logger.warning(f"无法解析时间: {time_text}，跳过此项")
                            continue
                        
                        # 检查时间是否在限制内
                        if parsed_time < time_limit:
                            logger.debug(f"时间过滤: {time_text} ({parsed_time}) 超出 {days_limit} 天限制")
                            page_filtered_count += 1
                            filtered_count += 1
                            continue
                        
                        # 提取阅读数
                        read_element = item.select_one('td:nth-child(1) .read')
                        read_count = read_element.get_text(strip=True) if read_element else "0"
                        
                        # 提取评论数
                        reply_element = item.select_one('td:nth-child(2) .reply')
                        reply_count = reply_element.get_text(strip=True) if reply_element else "0"
                        
                        # 记录调试信息
                        logger.debug(f"解析成功: {title_text[:50]}... | 作者: {author_text} | 时间: {time_text} ({parsed_time})")
                        
                        news_list.append({
                            'stock_code': stock_code,
                            'title': title_text,
                            'author': author_text,
                            'time': time_text,
                            'parsed_time': parsed_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'read_count': read_count,
                            'reply_count': reply_count,
                            'url': full_link,
                            'source': '东方财富',
                            'page': page,
                            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        page_news_count += 1
                        
                    except Exception as e:
                        logger.log_parse_error(str(e), f"第 {page} 页第 {i+1} 项")
                        continue
                
                logger.info(f"第 {page} 页成功解析 {page_news_count} 条新闻，过滤 {page_filtered_count} 条过期新闻")
                successful_pages += 1
                
                # 如果当前页过滤的新闻数量很多，可能后面的页都是过期数据
                if page_filtered_count > len(news_items) * 0.8:  # 如果80%以上都是过期数据
                    logger.info(f"第 {page} 页大部分新闻已过期，停止爬取后续页面")
                    break
                
            else:
                logger.warning(f"第 {page} 页未找到任何新闻项")
                # 如果连续两页都没有新闻，可能已经到最后一页
                if page > 1:
                    logger.info(f"第 {page} 页无数据，可能已到最后一页，停止爬取")
                    break
            
            # 添加延迟，避免请求过于频繁
            if page < max_pages:
                time.sleep(1)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败 (第 {page} 页): {e}")
            break
        except Exception as e:
            logger.exception(f"爬取第 {page} 页时发生未知错误: {e}")
            break
    
    # 记录最终结果
    logger.log_crawl_result(stock_code, len(news_list), successful_pages)
    logger.info(f"时间过滤统计: 总共过滤 {filtered_count} 条过期新闻")
    
    return pd.DataFrame(news_list)

# 示例使用
if __name__ == "__main__":
    # 创建日志管理器（控制台只显示警告及以上级别）
    logger = create_logger('eastmoney_crawler', console_level=logging.WARNING)
    logger.info("开始爬取东方财富新闻")
    
    code_list = ['002594', '300474', '600036', '688981']
    for code in code_list:
        # 爬取数据（只保留7天内的数据）
        df = crawl_eastmoney(code, logger, max_pages=10, days_limit=7)
        
        logger.info(f"最终结果: DataFrame形状: {df.shape}")
        if not df.empty:
            logger.info(f"前5行数据:\n{df.head()}")
            
            # 显示时间范围
            if 'parsed_time' in df.columns:
                earliest_time = df['parsed_time'].min()
                latest_time = df['parsed_time'].max()
                logger.info(f"数据时间范围: {earliest_time} 到 {latest_time}")
            
            # 保存结果
            csv_file = f'logs/eastmoney_news_{code}_link.csv'
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            logger.info(f"结果已保存到: {csv_file}")
        else:
            logger.warning("未获取到任何数据")
    
    logger.info("爬取完成")