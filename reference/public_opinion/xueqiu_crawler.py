import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
import os
import logging
import json
import re

# 添加父目录到路径，支持相对导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from crawler.logger_config import create_logger
except ImportError:
    # 如果相对导入失败，尝试直接导入
    from logger_config import create_logger

def parse_xueqiu_time(time_str):
    """
    解析雪球网时间字符串，返回datetime对象
    :param time_str: 时间字符串，如 '2小时前', '昨天 14:30', '2024-12-01 10:30'
    :return: datetime对象
    """
    try:
        now = datetime.now()
        
        if '分钟前' in time_str:
            minutes = int(time_str.replace('分钟前', ''))
            return now - timedelta(minutes=minutes)
        elif '小时前' in time_str:
            hours = int(time_str.replace('小时前', ''))
            return now - timedelta(hours=hours)
        elif '天前' in time_str:
            days = int(time_str.replace('天前', ''))
            return now - timedelta(days=days)
        elif '昨天' in time_str:
            time_part = time_str.replace('昨天 ', '')
            hour, minute = map(int, time_part.split(':'))
            yesterday = now - timedelta(days=1)
            return yesterday.replace(hour=hour, minute=minute, second=0, microsecond=0)
        elif '前天' in time_str:
            time_part = time_str.replace('前天 ', '')
            hour, minute = map(int, time_part.split(':'))
            day_before_yesterday = now - timedelta(days=2)
            return day_before_yesterday.replace(hour=hour, minute=minute, second=0, microsecond=0)
        elif re.match(r'\d{4}-\d{2}-\d{2}', time_str):
            # 格式: '2024-12-01 10:30' 或 '2024-12-01'
            if ' ' in time_str:
                date_part, time_part = time_str.split(' ')
                year, month, day = map(int, date_part.split('-'))
                hour, minute = map(int, time_part.split(':'))
                return datetime(year, month, day, hour, minute)
            else:
                year, month, day = map(int, time_str.split('-'))
                return datetime(year, month, day, 0, 0)
        else:
            # 其他格式，尝试解析
            return None
            
    except Exception as e:
        return None

def crawl_xueqiu_discussions(stock_code, logger=None, max_pages=5, days_limit=7):
    """
    爬取雪球网个股讨论
    :param stock_code: 股票代码，如 '600519'
    :param logger: 日志对象，如果为None则自动创建
    :param max_pages: 最大爬取页数
    :param days_limit: 时间限制，只保留指定天数以内的数据（默认7天）
    :return: DataFrame格式的讨论数据
    """
    if logger is None:
        # 创建日志管理器，控制台只显示警告及以上级别
        logger = create_logger('xueqiu_crawler', console_level=logging.WARNING)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://xueqiu.com/',
        'Origin': 'https://xueqiu.com'
    }
    
    # 雪球网API URL
    base_url = 'https://xueqiu.com/v4/statuses/stock_timeline.json'
    
    discussions_list = []
    successful_pages = 0
    filtered_count = 0
    
    # 计算时间限制
    time_limit = datetime.now() - timedelta(days=days_limit)
    logger.info(f"开始爬取股票 {stock_code} 的雪球讨论，最大页数: {max_pages}，时间限制: {days_limit}天以内")
    logger.info(f"时间限制点: {time_limit.strftime('%Y-%m-%d %H:%M:%S')}")
    
    for page in range(1, max_pages + 1):
        try:
            # 雪球网API参数
            params = {
                'symbol_id': stock_code,
                'count': 20,  # 每页20条
                'source': 'all',
                'page': page
            }
            
            logger.info(f"正在爬取第 {page} 页: {base_url}")
            
            # 记录请求开始时间
            start_time = time.time()
            response = requests.get(base_url, headers=headers, params=params, timeout=10)
            response_time = time.time() - start_time
            
            response.raise_for_status()
            
            # 记录请求日志
            logger.log_request(f"{base_url}?page={page}", response.status_code, response_time)
            logger.debug(f"响应内容长度: {len(response.text)}")
            
            # 解析JSON响应
            try:
                data = response.json()
                discussions = data.get('list', [])
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                break
            
            logger.info(f"第 {page} 页找到 {len(discussions)} 个讨论项")
            
            if len(discussions) > 0:
                page_discussions_count = 0
                page_filtered_count = 0
                
                for i, discussion in enumerate(discussions):
                    try:
                        # 提取基本信息
                        title = discussion.get('title', '')
                        text = discussion.get('text', '')
                        content = title if title else text[:100] + '...' if len(text) > 100 else text
                        
                        # 提取作者信息
                        user = discussion.get('user', {})
                        author = user.get('screen_name', '未知作者')
                        author_id = user.get('id', '')
                        
                        # 提取时间
                        created_at = discussion.get('created_at', 0)
                        if created_at:
                            # 雪球网时间戳是毫秒级的
                            parsed_time = datetime.fromtimestamp(created_at / 1000)
                        else:
                            parsed_time = None
                        
                        # 检查时间是否在限制内
                        if parsed_time and parsed_time < time_limit:
                            logger.debug(f"时间过滤: {parsed_time} 超出 {days_limit} 天限制")
                            page_filtered_count += 1
                            filtered_count += 1
                            continue
                        
                        # 提取其他信息
                        source = discussion.get('source', '雪球')
                        retweet_count = discussion.get('retweet_count', 0)
                        reply_count = discussion.get('reply_count', 0)
                        fav_count = discussion.get('fav_count', 0)
                        
                        # 构建链接
                        discussion_id = discussion.get('id', '')
                        if discussion_id:
                            full_link = f'https://xueqiu.com{user.get("profile_image_url", "")}'
                        else:
                            full_link = ''
                        
                        # 记录调试信息
                        logger.debug(f"解析成功: {content[:50]}... | 作者: {author} | 时间: {parsed_time}")
                        
                        discussions_list.append({
                            'stock_code': stock_code,
                            'title': title,
                            'content': text,
                            'author': author,
                            'author_id': author_id,
                            'time': parsed_time.strftime('%Y-%m-%d %H:%M:%S') if parsed_time else '未知时间',
                            'parsed_time': parsed_time.strftime('%Y-%m-%d %H:%M:%S') if parsed_time else '',
                            'retweet_count': retweet_count,
                            'reply_count': reply_count,
                            'fav_count': fav_count,
                            'source': source,
                            'url': full_link,
                            'page': page,
                            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        page_discussions_count += 1
                        
                    except Exception as e:
                        logger.log_parse_error(str(e), f"第 {page} 页第 {i+1} 项")
                        continue
                
                logger.info(f"第 {page} 页成功解析 {page_discussions_count} 条讨论，过滤 {page_filtered_count} 条过期讨论")
                successful_pages += 1
                
                # 如果当前页过滤的讨论数量很多，可能后面的页都是过期数据
                if page_filtered_count > len(discussions) * 0.8:  # 如果80%以上都是过期数据
                    logger.info(f"第 {page} 页大部分讨论已过期，停止爬取后续页面")
                    break
                
            else:
                logger.warning(f"第 {page} 页未找到任何讨论项")
                # 如果连续两页都没有讨论，可能已经到最后一页
                if page > 1:
                    logger.info(f"第 {page} 页无数据，可能已到最后一页，停止爬取")
                    break
            
            # 添加延迟，避免请求过于频繁
            if page < max_pages:
                time.sleep(2)  # 雪球网需要更长的延迟
                
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败 (第 {page} 页): {e}")
            break
        except Exception as e:
            logger.exception(f"爬取第 {page} 页时发生未知错误: {e}")
            break
    
    # 记录最终结果
    logger.log_crawl_result(stock_code, len(discussions_list), successful_pages)
    logger.info(f"时间过滤统计: 总共过滤 {filtered_count} 条过期讨论")
    
    return pd.DataFrame(discussions_list)

def crawl_xueqiu_news(stock_code, logger=None, max_pages=5, days_limit=7):
    """
    爬取雪球网个股新闻
    :param stock_code: 股票代码，如 '600519'
    :param logger: 日志对象，如果为None则自动创建
    :param max_pages: 最大爬取页数
    :param days_limit: 时间限制，只保留指定天数以内的数据（默认7天）
    :return: DataFrame格式的新闻数据
    """
    if logger is None:
        logger = create_logger('xueqiu_news_crawler', console_level=logging.WARNING)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://xueqiu.com/',
        'Origin': 'https://xueqiu.com'
    }
    
    # 雪球网新闻API URL
    base_url = 'https://xueqiu.com/v4/statuses/stock_timeline.json'
    
    news_list = []
    successful_pages = 0
    filtered_count = 0
    
    # 计算时间限制
    time_limit = datetime.now() - timedelta(days=days_limit)
    logger.info(f"开始爬取股票 {stock_code} 的雪球新闻，最大页数: {max_pages}，时间限制: {days_limit}天以内")
    
    for page in range(1, max_pages + 1):
        try:
            # 雪球网API参数（只获取新闻）
            params = {
                'symbol_id': stock_code,
                'count': 20,
                'source': 'news',  # 只获取新闻
                'page': page
            }
            
            logger.info(f"正在爬取第 {page} 页新闻")
            
            response = requests.get(base_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            try:
                data = response.json()
                news_items = data.get('list', [])
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                break
            
            if len(news_items) > 0:
                page_news_count = 0
                page_filtered_count = 0
                
                for i, news in enumerate(news_items):
                    try:
                        title = news.get('title', '')
                        text = news.get('text', '')
                        content = title if title else text
                        
                        # 提取时间
                        created_at = news.get('created_at', 0)
                        if created_at:
                            parsed_time = datetime.fromtimestamp(created_at / 1000)
                        else:
                            parsed_time = None
                        
                        # 检查时间是否在限制内
                        if parsed_time and parsed_time < time_limit:
                            page_filtered_count += 1
                            filtered_count += 1
                            continue
                        
                        # 提取其他信息
                        source = news.get('source', '雪球')
                        url = news.get('url', '')
                        
                        news_list.append({
                            'stock_code': stock_code,
                            'title': title,
                            'content': text,
                            'time': parsed_time.strftime('%Y-%m-%d %H:%M:%S') if parsed_time else '未知时间',
                            'parsed_time': parsed_time.strftime('%Y-%m-%d %H:%M:%S') if parsed_time else '',
                            'source': source,
                            'url': url,
                            'page': page,
                            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        page_news_count += 1
                        
                    except Exception as e:
                        logger.log_parse_error(str(e), f"第 {page} 页第 {i+1} 项")
                        continue
                
                logger.info(f"第 {page} 页成功解析 {page_news_count} 条新闻，过滤 {page_filtered_count} 条过期新闻")
                successful_pages += 1
                
                if page_filtered_count > len(news_items) * 0.8:
                    logger.info(f"第 {page} 页大部分新闻已过期，停止爬取后续页面")
                    break
                
            else:
                logger.warning(f"第 {page} 页未找到任何新闻项")
                if page > 1:
                    break
            
            if page < max_pages:
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"爬取第 {page} 页时发生错误: {e}")
            break
    
    logger.log_crawl_result(stock_code, len(news_list), successful_pages)
    logger.info(f"时间过滤统计: 总共过滤 {filtered_count} 条过期新闻")
    
    return pd.DataFrame(news_list)

# 示例使用
if __name__ == "__main__":
    # 创建日志管理器（控制台只显示警告及以上级别）
    logger = create_logger('xueqiu_crawler', console_level=logging.WARNING)
    logger.info("开始爬取雪球网数据")
    
    code_list = ['002594', '300474', '600036']
    for code in code_list:
        # 爬取讨论数据（只保留7天内的数据）
        df_discussions = crawl_xueqiu_discussions(code, logger, max_pages=5, days_limit=7)
        
        logger.info(f"讨论结果: DataFrame形状: {df_discussions.shape}")
        if not df_discussions.empty:
            # 保存讨论结果
            csv_file = f'logs/xueqiu_discussions_{code}.csv'
            df_discussions.to_csv(csv_file, index=False, encoding='utf-8-sig')
            logger.info(f"讨论结果已保存到: {csv_file}")
        
        # 爬取新闻数据
        df_news = crawl_xueqiu_news(code, logger, max_pages=3, days_limit=7)
        
        logger.info(f"新闻结果: DataFrame形状: {df_news.shape}")
        if not df_news.empty:
            # 保存新闻结果
            csv_file = f'logs/xueqiu_news_{code}.csv'
            df_news.to_csv(csv_file, index=False, encoding='utf-8-sig')
            logger.info(f"新闻结果已保存到: {csv_file}")
    
    logger.info("雪球网爬取完成") 