import requests

def get_access_token(corpid: str, corpsecret: str) -> str:
    """
    获取企业微信的 Access Token
    """
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}"
    response = requests.get(url)
    data = response.json()
    
    if data.get('errcode') == 0:
        return data.get('access_token')
    else:
        raise Exception(f"获取 Access Token 失败: {data.get('errmsg')} (errcode: {data.get('errcode')})")

def send_template_card(access_token: str, agentid: int, touser: str, task_id: str) -> dict:
    """
    发送交互式任务卡片（按钮交互型）
    """
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
    
    payload = {
        "touser": touser,
        "msgtype": "template_card",
        "agentid": agentid,
        "template_card": {
            "card_type": "button_interaction",
            "source": {
                "icon_url": "https://wework.qpic.cn/wwpic/252813_jOfDFte2RQOEdqe_1628238102/0", # 示例企业微信图标
                "desc": "交互助手"
            },
            "main_title": {
                "title": "您有一个新的待办任务",
                "desc": "请及时处理"
            },
            "sub_title_text": "任务详情：请确认是否审批通过。",
            "task_id": task_id, # 必须全局唯一，用于回调区分
            "button_selection": {
                "question_key": "task_action",
                "title": "请选择操作",
                "button_list": [
                    {
                        "text": "同意",
                        "style": 1,
                        "key": "agree"
                    },
                    {
                        "text": "拒绝",
                        "style": 2,
                        "key": "reject"
                    }
                ]
            }
        }
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    if data.get('errcode') == 0:
        print("✅ 交互式任务卡片发送成功！")
        return data
    else:
        raise Exception(f"发送卡片失败: {data.get('errmsg')} (errcode: {data.get('errcode')})")


if __name__ == "__main__":
    import time
    
    corpid = "wwf91b2ae32f1286c9"
    corpsecret = "_tKtlg1YXACz7TGPCILjM5teSH_KzYhBLHS6tDpuDLk"
    
    # TODO: 替换为您的应用AgentId和要测试的企微用户账号（UserID）
    AGENT_ID = 1000003
    TO_USER = "WangChenYu" # 也可以是特定的 UserId，如 "ZhangSan"
    
    try:
        # 1. 获取 Token
        token = get_access_token(corpid, corpsecret)
        print(f"成功获取 Access Token: {token[:15]}...\n")
        
        # 2. 发送卡片 (由于task_id要求唯一，这里使用时间戳生成)
        unique_task_id = f"task_{int(time.time())}"
        send_template_card(token, AGENT_ID, TO_USER, unique_task_id)
        
    except Exception as e:
        print(e)