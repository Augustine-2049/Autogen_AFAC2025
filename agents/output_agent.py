def save_report(text: str, code: str, out_dir: str = "output"):
    """
    输入: 研报文本，股票代码
    输出: 保存txt文件
    """
    import os
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{code}_report.txt")
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write(text)
    print(f"已保存: {path}") 