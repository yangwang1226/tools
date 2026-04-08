import requests
import json
import time
from datetime import datetime
from read_data import fetch_jizhi_data
# ================= 配置区 =================
# 智能表格 Webhook
SMARTSHEET_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/wedoc/smartsheet/webhook?key=2gW9ljV6mXWEMBZt972cNp0xcaJzB8s5SKyo18KTX3RkjOqs60TNJkqSK3Wk2iODeQRyxVXdypeW24z7ECJ1sZuYY1r1QWjrAXeGGK2D0DGg"
# 企微群机器人 Webhook
GROUP_BOT_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=3f7d2957-9f18-47c1-9ead-ea0674390361"


    

def add_to_smartsheet(order_data):
    """
    步骤 2：将数据追加到企业微信智能表格
    """
    print("\n⏳ 正在将数据写入企业微信智能表格...")
    
    # 构造符合智能表格要求的 payload
    payload = {
        "schema": {
            "f04Gwj": "单据号",
            "ftQMc5": "派工单号",
            "ftk5Tx": "客户名称",
            "ffFwIh": "联系人",
            "fn8TJd": "受理时间",
            "fCSN6i": "开工时间"
        },
        "add_records": [
            {
                "values": {
                    "f04Gwj": order_data["BillNo"],
                    "ftQMc5": order_data["ServiceNO"],
                    "ftk5Tx": order_data["Name"],
                    "ffFwIh": order_data["Contact"],
                    "fn8TJd": str(order_data["ReceiveTime"]), # 表格要求通常是字符串格式的毫秒时间戳
                    "fCSN6i": str(order_data["StartWorkTime"])
                }
            }
        ]
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(SMARTSHEET_WEBHOOK, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200 and response.json().get("errcode") == 0:
        print("✅ 数据已成功写入智能表格！")
    else:
        print(f"❌ 写入智能表格失败: {response.text}")

def send_wechat_notification(order_data):
    """
    步骤 3：发送企微群机器人卡片/Markdown提醒
    """
    print("\n⏳ 正在发送企微群消息提醒...")
    
        # 将时间戳转换为可读时间，用于展示
    accept_time_str = datetime.fromtimestamp(order_data["ReceiveTime"]/1000).strftime('%Y-%m-%d %H:%M:%S')
    
    # 构造 Markdown 格式的推送文本，展示得更漂亮，适合给领导演示
    markdown_content = f"""<font color=\"warning\">**🚨 新工单派发提醒**</font>
请相关同事注意，系统已自动同步一条最新工单记录。

> **单据编号：**<font color=\"info\">{order_data['BillNo']}</font>
> **派工单号：**{order_data['ServiceNO']}
> **客户名称：**{order_data['Name']}
> **联  系  人：**{order_data['Contact']}
> **受理时间：**{accept_time_str}

工单数据已同步至智能表格，请及时跟进处理进度。
<@all>"""

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": markdown_content
        }
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(GROUP_BOT_WEBHOOK, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200 and response.json().get("errcode") == 0:
        print("✅ 群消息提醒已成功发送！")
    else:
        print(f"❌ 发送群消息失败: {response.text}")

if __name__ == "__main__":
    print("================ 演示流程开始 ================")
    
    # 1. 获取数据（不传参数，默认查询前1小时数据）
    print("\n--- 测试：默认查询前1小时数据 ---")
    new_order_list = fetch_jizhi_data(ReDate="2026-04-07 10:00:00")
    
    if new_order_list:
        print(f"\n📋 获取到 {len(new_order_list)} 条工单，开始处理...")
        
        # 2. 循环写入智能表格和发送通知
        for index, order in enumerate(new_order_list, 1):
            print(f"\n[{index}/{len(new_order_list)}] 处理工单: {order.get('BillNo', 'N/A')} - {order.get('ServiceNO', 'N/A')}")
            
            # 写入智能表格
            add_to_smartsheet(order)
            
            # 发送群通知
            send_wechat_notification(order)
            
            print(f"✅ 工单 {order.get('BillNo', 'N/A')} 处理完成")
            
            # 避免请求过快，稍作延迟
            if index < len(new_order_list):
                time.sleep(1)
        
        print(f"\n🎉 所有工单处理完成！共处理 {len(new_order_list)} 条")
    else:
        print("❌ 未能获取到工单数据，流程终止。")
    
    print("\n================ 演示流程结束 ================")