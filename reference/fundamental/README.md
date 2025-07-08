# 财务报告和研报爬虫工具

这个工具可以自动爬取A股上市公司的财务报告和研报，并保存到以股票代码命名的目录中。

## 功能特点

- 支持多种数据源：巨潮资讯网、新浪财经、东方财富网
- 自动识别财务报告（年报、半年报、季报）
- 自动下载PDF文件
- 智能文件命名和去重
- 支持批量处理

## 文件说明

### 1. `em_financial_and_research.py` (原始版本)
- 使用API接口爬取
- 可能因接口变化而失效

### 2. `em_financial_and_research_fixed.py` (修复版本)
- 修复了API接口问题
- 使用巨潮资讯网API
- 更稳定的实现

### 3. `simple_financial_crawler.py` (简单版本)
- 使用网页爬取方式
- 不依赖API接口
- 更稳定可靠

### 4. `selenium_financial_crawler.py` (Selenium版本)
- 使用Selenium模拟浏览器
- 可以处理动态加载的内容
- 最稳定但需要安装Chrome

## 安装依赖

### 基础依赖
```bash
pip install requests beautifulsoup4 tqdm
```

### Selenium版本额外依赖
```bash
pip install selenium
```

### Chrome浏览器
- 下载并安装Chrome浏览器
- 下载ChromeDriver并添加到PATH环境变量

## 使用方法

### 1. 简单版本（推荐）
```bash
python fundamental/simple_financial_crawler.py
```

### 2. Selenium版本（最稳定）
```bash
python fundamental/selenium_financial_crawler.py
```

### 3. 修复版本
```bash
python fundamental/em_financial_and_research_fixed.py
```

## 输入示例

运行脚本后，按提示输入股票代码：
```
请输入A股股票代码（如600519）: 600519
```

## 输出目录结构

```
reports/
  600519/
    01_2023年年度报告.pdf
    02_2023年第三季度报告.pdf
    03_2023年半年度报告.pdf
    ...

research/
  600519/
    em_01_贵州茅台深度研究报告.pdf
    em_02_贵州茅台投资价值分析.pdf
    ...
```

## 支持的股票代码格式

- 上海证券交易所：600xxx, 601xxx, 603xxx, 688xxx
- 深圳证券交易所：000xxx, 002xxx, 300xxx

## 注意事项

1. **网络连接**：确保网络连接稳定
2. **反爬限制**：避免频繁请求，脚本已内置延迟
3. **文件大小**：PDF文件可能较大，确保有足够磁盘空间
4. **Chrome浏览器**：Selenium版本需要Chrome浏览器
5. **法律合规**：请遵守相关网站的使用条款

## 故障排除

### 1. 下载失败
- 检查网络连接
- 确认股票代码正确
- 尝试不同的数据源

### 2. Selenium启动失败
- 确认已安装Chrome浏览器
- 确认ChromeDriver版本与Chrome版本匹配
- 检查PATH环境变量设置

### 3. 权限错误
- 确保有写入目录的权限
- 检查磁盘空间是否充足

## 数据源说明

### 巨潮资讯网
- 官方权威数据源
- 包含所有上市公司公告
- 数据最完整

### 新浪财经
- 数据更新及时
- 界面友好
- 包含详细财务数据

### 东方财富网
- 研报数据丰富
- 分析报告详细
- 适合投资研究

## 更新日志

- v1.0: 初始版本，支持基础爬取功能
- v1.1: 修复API接口问题
- v1.2: 添加Selenium版本，提高稳定性
- v1.3: 优化文件命名和错误处理

## 免责声明

本工具仅供学习和研究使用，请遵守相关网站的使用条款和法律法规。使用者需自行承担使用风险。 