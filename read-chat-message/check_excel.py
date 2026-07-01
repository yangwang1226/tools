import pandas as pd

df = pd.read_excel(r'D:\旭小姐阳台\客户聊天记录\客户列表.xlsx', header=None)
print("总行数:", len(df))
print("总列数:", len(df.columns))
print()
print("前5行原始数据:")
for i in range(min(5, len(df))):
    print(f"第{i}行: {df.iloc[i].tolist()}")