import hashlib
import json
import time
import requests
from datetime import datetime, timedelta

def generate_sign(data: dict, api_secret: str) -> str:
    """
    根据规则生成 MD5 签名
    """
    # 1. 过滤掉字典中的 sign 参数
    filtered_data = {k: v for k, v in data.items() if k != 'sign'}
    
    # 2. 按照参数名 ASCII 码从小到大排序 (字典序)
    sorted_keys = sorted(filtered_data.keys())
    
    query_parts = []
    for key in sorted_keys:
        val = filtered_data[key]
        
        # 针对逻辑型字段处理：“0”代表“否”，“1”代表“是”
        if isinstance(val, bool):
            val_str = "1" if val else "0"
        # 针对数组/字典（如 Parms），通常转为无空格的 JSON 字符串参与签名
        elif isinstance(val, (list, dict)):
            val_str = json.dumps(val, ensure_ascii=False, separators=(',', ':'))
        else:
            val_str = str(val)
            
        # 拼接键值对
        query_parts.append(f"{key}={val_str}")
        
    stringA = "&".join(query_parts)
    
    # 3. 在 stringA 最后拼接上 apiSecret
    # 注意: 大多数接口规定形如 "&apiSecret=密钥"，若贵司接口是直接拼接密钥本身，请改为：stringSignTemp = stringA + api_secret
    stringSignTemp = f"{stringA}api_secret={api_secret}"
    
    print("--- 签名拼接过程 ---")
    print("stringSignTemp: ", stringSignTemp)
    
    # 4. MD5 运算并转为大写
    md5_hash = hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest()
    return md5_hash.upper()


def fetch_jizhi_data(ReDate=None):
    url = "http://cloud11.jeez.cn:8201/openwy/api/ReportData/GetReportData"
    apiSecret = "dfad565d6f456da45f6ad454"
    
        # 确定查询时间
    if ReDate is None:
        query_time = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"ℹ️ 未指定查询时间，默认拉取前 1 小时的数据，时间起点: {query_time}")
    elif isinstance(ReDate, datetime):
        query_time = ReDate.strftime('%Y-%m-%d %H:%M:%S')
        print(f"ℹ️ 根据指定时间拉取数据，时间起点: {query_time}")
    else:
        query_time = str(ReDate)
        print(f"ℹ️ 根据指定时间拉取数据，时间起点: {query_time}") 

    timeStamp = str(int(time.time()))
    # 完整的请求参数（发给服务器的完整 payload）
    base_payload = {
        "requestId": timeStamp,
        "appId": "jeezhtwy",
        "timeStamp": timeStamp,
        "nonceStr": "123",
        "dbNumber": "htwywy",
        "ReportType": "CustomerService",
        "Parms" : [
             {"ParmName": "orgid", "ParmValue": 0}, 
             {"ParmName": "ReDate", "ParmValue": f"{query_time}.000"}
             ]
    }

    # 文档明确指出的公共参数（只有这些参与签名）
    public_params_keys = ["appId", "requestId", "timeStamp", "dbNumber", "nonceStr"]
    
    # 1. 仅提取公共参数用于计算签名
    sign_dict = {k: base_payload[k] for k in public_params_keys if k in base_payload}
    
    # 2. 按照参数名 ASCII 码从小到大排序 (字典序)
    sorted_keys = sorted(sign_dict.keys())
    
    # 3. 拼接 key=value
    query_parts = []
    for key in sorted_keys:
        query_parts.append(f"{key}={sign_dict[key]}")
    stringA = "&".join(query_parts)
    
    
    headers = {"Content-Type": "application/json; charset=utf-8"}

    stringSignTemp = f"{stringA}{apiSecret}"
    # MD5 运算并转为大写
    sign = hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest().upper()

    base_payload["sign"] = sign
    
    try:
        resp = requests.post(url, json=base_payload, headers=headers)
        resp_json = resp.json()
                # 解析返回的数据
        if str(resp_json.get("code")) == '0000':
            data_list = resp_json.get("data", [])
            if data_list and len(data_list) > 0:
                print(f"✅ 成功拉取到 {len(data_list)} 条工单数据！")
                                # 批量处理并格式化数据
                result_data = []
                for idx, raw_data in enumerate(data_list, 1):
                    try:
                        parsed_data = {
                            "BillNo": raw_data.get("BillNo") or f"DJ-{datetime.now().strftime('%Y%m%d')}-{idx:03d}",
                            "ServiceNO": raw_data.get("ServiceNO") or "PG-UNKNOWN",
                            "Name": raw_data.get("Name") or "未知客户",
                            "Contact": raw_data.get("Contact") or "未知联系人",
                            "ReceiveTime": parse_time_to_ms(raw_data.get("ReceiveTime")),
                            "StartWorkTime": parse_time_to_ms(raw_data.get("StartWorkTime")),
                            "_raw_index": idx  # 保留原始索引便于追溯
                        }
                        result_data.append(parsed_data)
                    except Exception as e:
                        print(f"⚠️ 处理第 {idx} 条数据时出错: {e}，跳过该条数据")
                        continue
                
                print(f"✅ 成功格式化 {len(result_data)}/{len(data_list)} 条数据")
                return result_data
            else:
                print("⚠️ 接口调用成功，但返回数据为空，将使用模拟数据。")
        else:
            print(f"❌ 接口报错 (code: {resp_json.get('code')}): {resp.text}")
                
    except Exception as e:
        print(f"❌ 请求异常，使用模拟数据: {e}")
    
        # 如果请求失败或没数据，返回模拟数据用于演示流程继续
    print("⚠️ 使用模拟数据作为后备...")
    now_ms = int(time.time() * 1000)
    return [{
        "BillNo": f"DJ-{datetime.now().strftime('%Y%m%d')}-MOCK",
        "ServiceNO": "PG-MOCK-123",
        "Name": "测试星辰科技",
        "Contact": "王经理",
        "ReceiveTime": now_ms,
        "StartWorkTime": now_ms + 3600000,
        "_raw_index": 1
    }]

def parse_time_to_ms(time_str):
    """
    尝试将返回的时间字符串转换为毫秒时间戳
    支持多种时间格式，如果解析失败则使用当前时间
    
    Args:
        time_str: 时间字符串，支持格式如 '2024-01-01 12:00:00' 或 '2024-01-01T12:00:00.000'
    
    Returns:
        int: 毫秒时间戳
    """
    if not time_str:
        return int(time.time() * 1000)
    
    try:
        # 移除毫秒部分和T分隔符
        time_str_clean = str(time_str).split('.')[0].replace('T', ' ')
        dt = datetime.strptime(time_str_clean, '%Y-%m-%d %H:%M:%S')
        return int(dt.timestamp() * 1000)
    except Exception as e:
        print(f"⚠️ 时间解析失败 ('{time_str}'): {e}，使用当前时间")
        return int(time.time() * 1000)
    
if __name__ == "__main__":
    # 测试：不传参数，默认查询前1小时
    data = fetch_jizhi_data()
    print("\n返回的数据结构:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"\n共获取 {len(data)} 条数据")