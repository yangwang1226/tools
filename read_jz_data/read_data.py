import hashlib
import json
import time
import requests

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


def test_public_params_sign():
    url = "http://cloud11.jeez.cn:8201/openwy/api/ReportData/GetReportData"
    apiSecret = "dfad565d6f456da45f6ad454"
    
    timeStamp = str(int(time.time()))
    # 完整的请求参数（发给服务器的完整 payload）
    base_payload = {
        "requestId": timeStamp,
        "appId": "jeezhtwy",
        "timeStamp": timeStamp,
        "nonceStr": "123",
        "dbNumber": "htwywy",
        "ReportType": "CustomerService",
        "ReDate": "2025-12-31 23:59:59",
        "Parms" : [
             {"ParmName": "orgid", "ParmValue": 1}, 
             {"ParmName": "ReDate", "ParmValue": "2026-01-01 00:00:00.000"}
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
    
    # 4. 穷举文档中所谓“在stringA最后拼接上apiSecret”的几种可能含义
    strategies = {
        "直接无缝拼接 (常见于老接口)": f"{stringA}{apiSecret}"
        # "标准的 &apiSecret= (最规范)": f"{stringA}&apiSecret={apiSecret}",
        # "无 & 符的 apiSecret= (少见)": f"{stringA}apiSecret={apiSecret}",
        # "微信支付风格的 &key= ": f"{stringA}&key={apiSecret}",
        # "前面直接加个 & 符号": f"{stringA}&{apiSecret}"
    }

    print("=== 开始穷举测试公共参数验签 ===")
    print(f"参与签名的公共参数: {sorted_keys}\n")
    
    headers = {"Content-Type": "application/json; charset=utf-8"}
    attempt_count = 0

    for strategy_name, stringSignTemp in strategies.items():
        attempt_count += 1
        print(f"[{attempt_count}] 正在测试策略: {strategy_name}")
        print(f"拼接出的 stringSignTemp: {stringSignTemp}")
        
        # MD5 运算并转为大写
        sign = hashlib.md5(stringSignTemp.encode('utf-8')).hexdigest().upper()
        
        # 组装最终请求的 Payload（原参数 + sign）
        test_payload = base_payload.copy()
        test_payload["sign"] = sign
        
        try:
            resp = requests.post(url, json=test_payload, headers=headers)
            resp_json = resp.json()
            
            # 如果服务器返回的 code 不是 4002 (验签失败)，说明这套签名规则被服务器认可了！
            if str(resp_json.get("code")) != "4002":
                print("\n" + "="*60)
                print("🎉 恭喜！成功破解签名规则！")
                print(f"✅ 正确的拼接策略是：【{strategy_name}】")
                print(f"✅ 正确的 sign: {sign}")
                print(f"✅ 接口返回数据: {resp.text}")
                print("="*60 + "\n")
                return  # 找到正确规则就停止
            else:
                print(f"❌ 失败，返回: {resp.text}\n")
                
        except Exception as e:
            print(f"请求异常: {e}\n")

    print("所有组合已穷举完毕，仍然全部验签失败。请检查 appId 或 apiSecret 是否有误，或者是否有额外的隐藏规则。")

if __name__ == "__main__":
    test_public_params_sign()