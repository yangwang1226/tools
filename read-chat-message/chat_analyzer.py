import os
import json
import random
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Literal
from pydantic import BaseModel, Field

# ==========================================
# 1. 定义大模型输出的数据结构 (Pydantic Model)
# ==========================================
class CustomerProfile(BaseModel):
    is_paid: Literal["是", "否", "未知"] = Field(description="是否付费，严格输出：是或否或未知")
    amount: str = Field(description="金额，如果是数字提取数字，无则输出0")
    order_time: str = Field(description="成单时间，如果已付费或已确认成单，请结合聊天记录提取出成单的时间，无则输出未知")
    gender: Literal["男", "女", "未知"] = Field(description="客户性别，根据聊天语气推断，严格输出：男或女或未知")
    province_city: str = Field(description="省市，无则输出未知")
    district_county: str = Field(description="区县，无则输出未知")
    product_needs: str = Field(description="产品需求，具体想买什么，如花箱（含尺寸）等，无则输出未知")
    emotional_needs: str = Field(description="情感需求，无则输出未知")
    indoor_outdoor: str = Field(description="户内户外，无则输出未知")
    specific_area: str = Field(description="具体面积，无则输出未知")
    placement_orientation: str = Field(description="摆放位置朝向，无则输出未知")
    family_members: str = Field(description="家组成员，无则输出未知")
    plant_needs: str = Field(description="植物需求，无则输出未知")
    maintenance_time: str = Field(description="日常养护时长，无则输出未知")
    mailing_address: str = Field(description="邮寄地址，无则输出未知")
    contact_phone: str = Field(description="联系电话，无则输出未知")
    first_communication: str = Field(description="一次沟通具体情况，极简总结")
    first_pain_point: str = Field(description="一次沟通的需求或卡点，无则输出无")
    second_communication: str = Field(description="二次沟通具体情况，无则输出无")
    second_pain_point: str = Field(description="二次沟通的需求或卡点，无则输出无")

# ==========================================
# 2. 初始化 Azure OpenAI 大模型
# ==========================================
def get_llm():
    return AzureChatOpenAI(
        azure_endpoint="https://menshen.xdf.cn/",
        openai_api_key="f0a8d5bf6c8842d9828fc5264b895e18",
        azure_deployment="gpt-4o",
        openai_api_version="2024-12-01-preview",
        temperature=0.3,  # 降低温度，提高信息提取的稳定性和事实性
        max_tokens=4000,
        request_timeout=60,
        model_kwargs={"response_format": {"type": "json_object"}} # 强制原生 JSON 模式
    )

# ==========================================
# 3. 解析 JSON 文件，提取并组装为纯文本对话
# ==========================================
def parse_chat_history(json_data):
    my_wxid = "wxid_vkvdpam2hubc22"
    session = json_data.get("session", {})
    client_wxid = session.get("wxid", "未知微信")
    client_name = session.get("nickname", "未知姓名")
    
    chat_text = []
    messages = json_data.get("messages", [])
    
    first_time = "未知"
    last_time = "未知"
    if messages:
        # 取第一条和最后一条消息的时间作为聊天周期
        f_time_str = messages[0].get("formattedTime", "未知")
        l_time_str = messages[-1].get("formattedTime", "未知")
        # 截取年月日，去掉时分秒 (例如 2026-03-16 06:47:45 -> 2026-03-16)
        first_time = f_time_str.split(" ")[0] if f_time_str != "未知" else "未知"
        last_time = l_time_str.split(" ")[0] if l_time_str != "未知" else "未知"
        
    for msg in messages:
        # 仅处理文本消息，忽略系统消息、图片等干扰信息
        if msg.get("type") != "文本消息":
            continue
            
        # 区分发送者
        sender_wxid = msg.get("senderUsername")
        if sender_wxid == my_wxid:
            sender = "我方(销售)"
        else:
            sender = f"客户({client_name})"
            
        time_str = msg.get("formattedTime", "")
        content = msg.get("content", "")
        
        chat_text.append(f"[{time_str}] {sender}: {content}")
        
    return "\n".join(chat_text), client_wxid, client_name, first_time, last_time

# ==========================================
# 4. 单个文件处理逻辑
# ==========================================
def process_single_file(file_path, prompt_chain):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        chat_str, wxid, name, first_time, last_time = parse_chat_history(data)
        
                # 如果没有文本对话，直接返回基础信息
        if not chat_str.strip():
            return None
            
        # 调用大模型提取结构化数据（增加防抖重试机制）
        import time
        max_retries = 3
        content = ""
        for attempt in range(max_retries):
            try:
                content = prompt_chain.invoke({"chat_text": chat_str})
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"API请求失败: {str(e)}")
                time.sleep(2)  # 等待2秒后重试

        # 去除可能包含的 markdown json 标记
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
    
        # 解析 JSON
        raw_dict = json.loads(content.strip())
        
                # 英文 Key 到 中文 Key 的映射
        key_mapping = {
                    "is_paid": "是否付费",
                    "amount": "金额",
                    "order_time": "成单时间",
                    "gender": "性别",
                    "province_city": "省市",
                    "product_needs": "产品需求",
                    "shipping_address": "快递地址",
                    "remark": "备注"
                }
        
        # 重新组装为中文键名的字典
        result_dict = {key_mapping[k]: v for k, v in raw_dict.items() if k in key_mapping}
        
        # 手动插入固定字段
        result_dict["客户微信"] = wxid
        result_dict["客户姓名"] = name
        result_dict["第一次聊天时间"] = first_time
        result_dict["最后一次聊天时间"] = last_time
        
        # 增加用户类型判断逻辑：是否付费 为 是，则为老客户
        is_paid_val = str(result_dict.get("是否付费", "")).strip()
        if is_paid_val == "是":
            result_dict["用户类型"] = "老客户"
        else:
            result_dict["用户类型"] = "新客户"
        
        return result_dict
        
    except Exception as e:
        print(f"\n[错误] 处理文件 {os.path.basename(file_path)} 时出错: {str(e)}")
        return None

# ==========================================
# 5. 主程序入口
# ==========================================
def main():
    # 默认指向当前工作目录下的 20260509 文件夹
    base_dir = "20260509"
    
    print(f"正在扫描目录: {base_dir} ...")
    # 获取目录下所有的 .json 文件
    json_files = [
        os.path.join(base_dir, f) 
        for f in os.listdir(base_dir) 
        if f.endswith('.json')
    ]
    
    total_files = len(json_files)
    if total_files == 0:
        print("未找到任何 json 文件，请检查目录路径是否正确！")
        return
        
    print(f"共发现 {total_files} 个 JSON 文件，准备开始处理。")
    
        # 组装 LangChain 提取链
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个高度精确的销售数据分析师。你的任务是阅读我方销售与客户的微信聊天记录，提取关键数据，并严格输出为 JSON 对象。

【核心业务逻辑（极其重要）】：
1. 判定是否付费：如果客户仅提到省市（如“西安”），不代表已付费；只有客户发送了包含姓名、电话、具体街道的【完整快递地址】，或提到了“微信转账”、“支付宝扫码”、“闲鱼拍下”等且销售确认，才判定为“是”。
2. 金额提取：优先从聊天提取具体支付数字；如果根据上述逻辑明确已付费，但由于是扫码或链接支付导致找不到具体金额数字，金额必须填“需人工确认”。

【核心纪律要求】：
1. 必须输出纯 JSON 对象格式，不要带有 Markdown 标记，严格以左大括号开头。
2. 极简输出，不要长篇大论。
3. 如果没有明确提到信息，必须输出“未知”或“无”。

【JSON 字段结构及要求】：
"is_paid": "是否付费（严格填：是 或 否 或 未知）",
"amount": "金额（填具体数字，或填‘需人工确认’，无则填0）",
"order_time": "成单时间（无则填未知）",
"gender": "性别（严格填：男 或 女 或 未知）",
"province_city": "省市（仅保留省份或直辖市，如浙江省、上海市，无则填未知）",
"product_needs": "产品需求（严格填：花箱 或 设计 或 花箱租摆 或 庭院，如果都不符合填未知）",
"shipping_address": "快递地址（客户发送的完整收货地址，无则填未知）",
"remark": "备注（一段话总结客户的以下维度：情感需求、户内户外、具体面积、朝向、家组成员、植物需求、养护时长、联系电话、一二次沟通情况及卡点。请组织成通顺的一段话，没有提到的维度直接忽略不写，简明扼要）"
"""),
        ("user", "聊天记录如下：\n{chat_text}")
    ])
    
    from langchain_core.output_parsers import StrOutputParser
    # 加上 StrOutputParser 直接将返回转化为字符串
    chain = prompt | llm | StrOutputParser()

    results = []
    
    # 使用线程池并发处理，加速大模型请求
    max_workers = min(10, total_files)  # 最多10个并发
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = {executor.submit(process_single_file, fp, chain): fp for fp in json_files}
        
        # 配合 tqdm 显示进度条
        for future in tqdm(as_completed(futures), total=total_files, desc="数据提取进度"):
            res = future.result()
            if res:
                results.append(res)
                
    # ==========================================
    # 6. 数据整理与导出 Excel
    # ==========================================
    if results:
        df = pd.DataFrame(results)
        
        # 整理所需的列顺序
        columns_order = [
            "客户姓名", "用户类型", "第一次聊天时间", "最后一次聊天时间",
            "性别", "是否付费", "金额", "成单时间", "省市", 
            "产品需求", "快递地址", "备注"
        ]
        
        # 过滤并排序存在的列
        final_cols = [col for col in columns_order if col in df.columns]
        df = df[final_cols]
        
        # 按照添加时间（第一次聊天时间）倒序排列
        if "第一次聊天时间" in df.columns:
            df = df.sort_values(by="第一次聊天时间", ascending=False).reset_index(drop=True) 
        
        # 生成输出文件名
        date_str = datetime.now().strftime("%Y-%m-%d")
        random_suffix = random.randint(1000, 9999)  # 增加随机数后缀避免文件覆盖冲突
        output_file = os.path.join(base_dir, f"{date_str}_客户数据提取分析_{random_suffix}.xlsx")
        
        # 写入 Excel
        try:
            df.to_excel(output_file, index=False)
            print(f"\n✅ 提取完成！成功处理了 {len(results)} 条有效数据。")
            print(f"📄 结果已保存至: {output_file}")
        except Exception as e:
            print(f"\n❌ 保存 Excel 失败: {e}")
            # 如果原路径保存失败，尝试保存到当前运行目录
            fallback_path = f"{date_str}_客户数据提取分析_{random_suffix}.xlsx"
            df.to_excel(fallback_path, index=False)
            print(f"已备用保存至当前目录: {fallback_path}")
    else:
        print("\n未提取到任何有效数据。")

if __name__ == "__main__":
    main()