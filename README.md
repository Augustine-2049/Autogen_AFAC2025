# Autogen_AFAC2025
a demo for AFAC2025 using autogen as the framework
这首先是一个基于以下网站的学习文档：
- https://microsoft.github.io/autogen
- 1 - https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/components/model-clients.html
    - 1.5没跑通
- 

## 部署环境
```bash
uv init
.\.venv\Script\activate
uv add autogenstudio autogen-agentchat autogen-ext


```



## 目录结构说明（补充）
- `crawler/`：爬虫相关代码，按数据类别分文件（如company_announcements.py、financial_reports.py、stock_prices.py、news.py等），每个文件可包含多个数据源的爬虫函数，便于后续扩展和鲁棒性提升。

## 环境与依赖管理
- 推荐使用 [uv](https://github.com/astral-sh/uv) 进行Python虚拟环境和依赖管理。
- 安装uv：`pip install uv`
- 创建/激活环境：`uv venv .venv && uv pip install -r requirements.txt`
- 后续开发、运行、测试建议在uv虚拟环境下进行。



