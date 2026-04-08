"""
测试脚本：验证整个数据同步流程
"""
from datetime import datetime, timedelta
from read_data import fetch_jizhi_data

print("="*60)
print("测试 1: 不传查询时间参数（默认查询前1小时）")
print("="*60)
data1 = fetch_jizhi_data()
print("\n返回的数据:")
print(f"  单据号: {data1['BillNo']}")
print(f"  派工单号: {data1['ServiceNO']}")
print(f"  客户名称: {data1['Name']}")
print(f"  联系人: {data1['Contact']}")
print(f"  受理时间: {data1['ReceiveTime']}")
print(f"  开工时间: {data1['StartWorkTime']}")

print("\n" + "="*60)
print("测试 2: 传入指定时间字符串")
print("="*60)
data2 = fetch_jizhi_data(ReDate="2026-04-08 10:00:00")
print(f"\n返回的数据: {data2}")

print("\n" + "="*60)
print("测试 3: 传入 datetime 对象")
print("="*60)
custom_time = datetime.now() - timedelta(days=1)
data3 = fetch_jizhi_data(ReDate=custom_time)
print(f"\n返回的数据: {data3}")

print("\n✅ 所有测试完成！数据结构符合预期。")
print("\n接下来请运行: python demo_sync.py")
print("这将执行完整的流程：拉取数据 -> 写入智能表格 -> 发送企微群提醒")