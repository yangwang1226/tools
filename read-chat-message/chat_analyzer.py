import os
import json
import random
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# ==========================================
# 1. 定义大模型输出的数据结构 (Pydantic Model)
# ==========================================
class CustomerProfile(BaseModel):
    is_paid: str = Field(description="是否付费，输出：是/否/未知", alias="是否付费")
    amount: str = Field(description="金额，如果是数字提取数字，无则输出0", alias="金额")
    order_time: str = Field(description="成单时间，如果已付费或已确认成单，请结合聊天记录提取出成单的时间（可到天或具体时间），无则输出未知", alias="成单时间")
    gender: str = Field(description="客户性别，根据聊天语气推断，输出：男/女/未知", alias="性别")
    province_city: str = Field(description="省市，无则输出未知", alias="省市")
    district_county: str = Field(description="区县，无则输出未知", alias="区县")
    product_needs: str = Field(description="产品需求，具体想买什么，如花箱（含尺寸）等，无则输出未知", alias="产品需求")
    emotional_needs: str = Field(description="情感需求，无则输出未知", alias="情感需求")
    indoor_outdoor: str = Field(description="户内户外，无则输出未知", alias="户内户外")
    specific_area: str = Field(description="具体面积，无则输出未知", alias="具体面积")
    placement_orientation: str = Field(description="摆放位置朝向，无则输出未知", alias="摆放位置朝向")
    family_members: str = Field(description="家组成员，无则输出未知", alias="家组成员")
    plant_needs: str = Field(description="植物需求，无则输出未知", alias="植物需求")
    maintenance_time: str = Field(description="日常养护时长，无则输出未知", alias="日常养护时长")
    mailing_address: str = Field(description="邮寄地址，无则输出未知", alias="邮寄地址")
    contact_phone: str = Field(description="联系电话，无则输出未知", alias="联系电话")
    first_communication: str = Field(description="一次沟通具体情况，总结内容", alias="一次沟通具体情况")
    first_pain_point: str = Field(description="一次沟通的需求或卡点（如觉得贵、还在考虑等），无则输出无", alias="需求或卡点")
    second_communication: str = Field(description="二次沟通具体情况（如果多次沟通），无则输出无", alias="二次沟通具体情况")
    second_pain_point: str = Field(description="二次沟通的需求或卡点，无则输出无", alias="二次沟通需求或卡点")

# ==========================================
# 2. 初始化 Azure OpenAI 大模型
# ==========================================
def get_llm():
    return AzureChatOpenAI(
        azure_endpoint="https://menshen.test.xdf.cn/",
        openai_api_key="c8575027653b42b1b47747f0b4ab135b",
        azure_deployment="gpt-4o",
        openai_api_version="2024-12-01-preview",
        temperature=0.1,  # 降低温度，提高信息提取的稳定性和事实性
        max_tokens=4000,
        request_timeout=60
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
        
    return "\n".join(chat_text), client_wxid, client_name

# ==========================================
# 4. 单个文件处理逻辑
# ==========================================
def process_single_file(file_path, prompt_chain):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        chat_str, wxid, name = parse_chat_history(data)
        
        # 如果没有文本对话，直接返回基础信息
        if not chat_str.strip():
            return None
            
        # 调用大模型提取结构化数据
        result = prompt_chain.invoke({"chat_text": chat_str})
        
        # 将 Pydantic 模型转化为字典，使用我们在 alias 中定义的中文列名
        result_dict = result.model_dump(by_alias=True)
        
        # 手动插入那些不需要大模型分析，直接从 json 获取的固定字段
        result_dict["客户微信"] = wxid
        result_dict["客户姓名"] = name
        
        return result_dict
        
    except Exception as e:
        print(f"\n[错误] 处理文件 {os.path.basename(file_path)} 时出错: {str(e)}")
        return None

# ==========================================
# 5. 主程序入口
# ==========================================
def main():
    base_dir = r"D:\旭小姐阳台\客户档案聊天记录"
    
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
    structured_llm = llm.with_structured_output(CustomerProfile)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的销售数据分析师。你的任务是阅读我方销售与客户的微信聊天记录，并从中提取出客户的关键画像数据。
请严格按照要求的数据结构输出，如果没有提到相关信息，请一律输出“未知”或“无”，不要自行捏造数据。"""),
        ("user", "聊天记录如下：\n{chat_text}")
    ])
    
    chain = prompt | structured_llm

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
            "客户微信", "客户姓名", "性别", "是否付费", "金额", "成单时间", "省市", "区县", 
            "产品需求", "情感需求", "户内户外", "具体面积", "摆放位置朝向", 
            "家组成员", "植物需求", "日常养护时长", "邮寄地址", "联系电话", 
            "一次沟通具体情况", "需求或卡点", "二次沟通具体情况", "二次沟通需求或卡点"
        ]
        
        # 过滤并排序存在的列
        final_cols = [col for col in columns_order if col in df.columns]
        df = df[final_cols]
        
        # 添加序号列
        df.insert(0, '序号', range(1, len(df) + 1)) 
        
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