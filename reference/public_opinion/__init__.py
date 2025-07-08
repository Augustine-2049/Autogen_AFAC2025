# -*- coding: utf-8 -*-
"""
爬虫模块
包含东方财富新闻爬虫和日志管理功能
"""

from .eastmoney_crawler import crawl_eastmoney_news
from .logger_config import create_logger, CrawlerLogger

__version__ = "1.0.0"
__author__ = "Your Name"

__all__ = [
    'crawl_eastmoney_news',
    'create_logger', 
    'CrawlerLogger'
] 