# 爬虫Tool接口文档（标准模板）

## 1. Tool接口规范

### 1.1 Tool注册示例

```python
@tool("fetch_financial_reports")
def fetch_financial_reports_tool(code: str) -> str:
    """
    输入: 股票代码（如"002594"）
    输出: 保存的CSV文件路径（如"data/002594/financial_reports/利润表.csv"）
    说明: 爬取并保存三大会计报表，返回主表路径或全部路径列表
    """
    # ...爬虫逻辑...
    return "data/002594/financial_reports/利润表.csv"
```

### 1.2 Tool接口通用格式
- 输入参数：
  - `code`（str）：股票代码或唯一标识
  - 其他可选参数（如年份、季度、数据源等）
- 输出：
  - 返回数据文件的路径（str或List[str]），如CSV/JSON文件
  - 或直接返回标准化的dict/DataFrame（如Agent链路支持）
- 副作用：
  - 数据文件自动保存到`data/`目录下的标准位置

---

## 2. 各类爬虫Tool接口模板

### 2.1 财报爬虫Tool
```python
@tool("fetch_financial_reports")
def fetch_financial_reports_tool(code: str) -> List[str]:
    """
    输入: 股票代码
    输出: 三大会计报表CSV文件路径列表
    """
    return [
        f"data/{code}/financial_reports/利润表.csv",
        f"data/{code}/financial_reports/资产负债表.csv",
        f"data/{code}/financial_reports/现金流量表.csv"
    ]
```

### 2.2 股权结构爬虫Tool
```python
@tool("fetch_shareholder_data")
def fetch_shareholder_data_tool(code: str) -> str:
    """
    输入: 股票代码
    输出: 股东结构CSV文件路径
    """
    return f"data/{code}/shareholder/股东结构.csv"
```

### 2.3 行业数据爬虫Tool
```python
@tool("fetch_industry_data")
def fetch_industry_data_tool(code: str) -> str:
    """
    输入: 股票代码
    输出: 行业数据CSV文件路径
    """
    return f"data/{code}/industry/行业数据.csv"
```

### 2.4 舆论数据爬虫Tool
```python
@tool("fetch_public_opinion")
def fetch_public_opinion_tool(code: str) -> List[str]:
    """
    输入: 股票代码
    输出: 新闻/情感分析JSON文件路径列表
    """
    return [
        f"data/{code}/public_opinion/news.json",
        f"data/{code}/public_opinion/sentiment.json"
    ]
```

### 2.5 公司基础信息爬虫Tool
```python
@tool("fetch_company_profile")
def fetch_company_profile_tool(code: str) -> str:
    """
    输入: 股票代码
    输出: 公司基础信息JSON文件路径
    """
    return f"data/{code}/profile/company_profile.json"
```

---

## 3. 目录结构规范

详见《frame_design.md》第12节：data目录结构设计（爬虫与Agent协作标准）。 