from autogen import ConversableAgent
import os
import pandas as pd

class DataLoaderAgent(ConversableAgent):
    def run(self, code: str) -> dict:
        base_dir = os.path.join("data", code, "financial_reports")
        result = {}
        for name in ["利润表", "资产负债表", "现金流量表"]:
            path = os.path.join(base_dir, f"{name}.csv")
            if os.path.exists(path):
                result[name] = pd.read_csv(path)
        return result

from autogen import ConversableAgent
import pandas as pd

class FinancialAnalyzerAgent(ConversableAgent):
    def run(self, financial_reports: dict) -> dict:
        result = {}
        income = financial_reports.get("利润表")
        if income is not None:
            result["营业收入均值"] = income["营业收入"].mean() if "营业收入" in income.columns else None
            result["净利润均值"] = income["净利润"].mean() if "净利润" in income.columns else None
        return result

from autogen import ConversableAgent

class ReportWriterAgent(ConversableAgent):
    def run(self, analysis: dict) -> str:
        lines = ["# 财务分析摘要"]
        for k, v in analysis.items():
            lines.append(f"{k}: {v}")
        return "\n".join(lines)

from autogen import ConversableAgent

class ReviewAgent(ConversableAgent):
    def run(self, text: str) -> str:
        feedback = "[自动审查] 内容格式合规，建议补充更多行业对比分析。"
        return text + "\n\n" + feedback

from autogen import ConversableAgent
import os

class OutputAgent(ConversableAgent):
    def run(self, text: str, code: str) -> str:
        out_dir = "output"
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{code}_report.txt")
        with open(path, "w", encoding="utf-8-sig") as f:
            f.write(text)
        return f"已保存: {path}"

def main(code: str):
    # 实例化各Agent
    data_loader = DataLoaderAgent("DataLoader")
    analyzer = FinancialAnalyzerAgent("Analyzer")
    writer = ReportWriterAgent("Writer")
    reviewer = ReviewAgent("Reviewer")
    outputter = OutputAgent("Outputter")

    # Agent链式调用（模拟Autogen消息流）
    financial_reports = data_loader.run(code)
    analysis = analyzer.run(financial_reports)
    report_text = writer.run(analysis)
    reviewed_text = reviewer.run(report_text)
    result = outputter.run(reviewed_text, code)
    print(result)

if __name__ == "__main__":
    main("002594") 