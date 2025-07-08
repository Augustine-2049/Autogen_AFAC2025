import logging
import logging.handlers
import os
from datetime import datetime

class CrawlerLogger:
    """
    爬虫日志管理类
    支持日志轮转、不同级别日志分离、格式化输出
    """
    
    def __init__(self, name='crawler', log_dir='logs', max_bytes=10*1024*1024, backup_count=5, console_level=logging.WARNING):
        """
        初始化日志管理器
        :param name: 日志器名称
        :param log_dir: 日志目录
        :param max_bytes: 单个日志文件最大大小（字节）
        :param backup_count: 保留的日志文件数量
        :param console_level: 控制台输出级别（默认WARNING，只显示警告及以上级别）
        """
        self.name = name
        self.log_dir = log_dir
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.console_level = console_level
        
        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 创建logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 设置处理器
        self._setup_handlers()
    
    def _setup_handlers(self):
        """设置各种日志处理器"""
        
        # 1. 信息日志处理器（INFO及以上级别）
        info_formatter = logging.Formatter(
            '%(levelname)s - %(message)s - %(asctime)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        info_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_dir, f'{self.name}_info.log'),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(info_formatter)
        self.logger.addHandler(info_handler)
        
        # 2. 错误日志处理器（ERROR及以上级别）
        error_formatter = logging.Formatter(
            '%(levelname)s - %(filename)s:%(lineno)d - %(message)s - %(asctime)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_dir, f'{self.name}_error.log'),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)
        
        # 3. 调试日志处理器（DEBUG及以上级别）
        debug_formatter = logging.Formatter(
            '%(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s - %(asctime)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        debug_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_dir, f'{self.name}_debug.log'),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(debug_formatter)
        self.logger.addHandler(debug_handler)
        
        # 4. 控制台处理器（根据console_level设置）
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s - %(asctime)s',
            datefmt='%H:%M:%S'
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.console_level)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """记录信息日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告日志"""
        self.logger.warning(message)
    
    def error(self, message):
        """记录错误日志"""
        self.logger.error(message)
    
    def debug(self, message):
        """记录调试日志"""
        self.logger.debug(message)
    
    def critical(self, message):
        """记录严重错误日志"""
        self.logger.critical(message)
    
    def exception(self, message):
        """记录异常日志（包含堆栈跟踪）"""
        self.logger.exception(message)
    
    def log_request(self, url, status_code, response_time=None):
        """记录请求日志"""
        if response_time:
            self.info(f"请求: {url} | 状态: {status_code} | 耗时: {response_time:.2f}s")
        else:
            self.info(f"请求: {url} | 状态: {status_code}")
    
    def log_crawl_result(self, stock_code, news_count, page_count):
        """记录爬取结果日志"""
        self.info(f"股票 {stock_code} 爬取完成 | 页数: {page_count} | 新闻数: {news_count}")
    
    def log_parse_error(self, error_msg, item_info=""):
        """记录解析错误日志"""
        self.error(f"解析错误: {error_msg} {item_info}")
    
    def get_logger(self):
        """获取原始logger对象"""
        return self.logger

def create_logger(name='crawler', log_dir='logs', console_level=logging.WARNING):
    """
    创建日志管理器的便捷函数
    :param name: 日志器名称
    :param log_dir: 日志目录
    :param console_level: 控制台输出级别
        - logging.ERROR: 只显示错误
        - logging.WARNING: 显示警告和错误（默认）
        - logging.DEBUG: 显示调试、警告和错误
        - logging.INFO: 显示所有信息
    :return: CrawlerLogger实例
    """
    return CrawlerLogger(name, log_dir, console_level=console_level)

# 使用示例
if __name__ == "__main__":
    # 创建日志管理器（控制台只显示警告及以上级别）
    logger = create_logger('test_crawler', console_level=logging.WARNING)
    
    # 测试各种日志级别
    logger.info("这是一条信息日志（不会显示在控制台）")
    logger.warning("这是一条警告日志（会显示在控制台）")
    logger.error("这是一条错误日志（会显示在控制台）")
    logger.debug("这是一条调试日志（不会显示在控制台）")
    
    # 测试特殊日志方法
    logger.log_request("http://example.com", 200, 1.5)  # INFO级别，不会显示在控制台
    logger.log_crawl_result("600519", 100, 5)  # INFO级别，不会显示在控制台
    logger.log_parse_error("解析标题失败", "第3个新闻项")  # ERROR级别，会显示在控制台
    
    print("日志测试完成，请查看logs目录下的日志文件") 