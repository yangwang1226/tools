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
# 1. 定义大模型输出的数据结构 (提取并合并的核心问题)
# ==========================================
class CoreQuestion(BaseModel):
    category: str = Field(description="核心问题分类，例如：'价格咨询'、'尺寸问题'、'材质问题'等，将语义相近的问题归为一类")
    description: str = Field(description="问题的具体描述，简要概括该分类下客户主要问了什么内容")

class CustomerQuestions(BaseModel):
    questions: list[CoreQuestion] = Field(
        description="客户在聊天记录中提出的所有核心问题列表。如果没有提问，返回空列表[]。"
    )

class MergedCategory(BaseModel):
    merged_descriptions: list[str] = Field(description="合并相同语义后的核心问题描述列表")

# ==========================================
# 2. 初始化 Azure OpenAI 大模型
# ==========================================
def get_llm():
    return AzureChatOpenAI(
        azure_endpoint="https://menshen.test.xdf.cn/",
        openai_api_key="c8575027653b42b1b47747f0b4ab135b",
        azure_deployment="gpt-4o",
        openai_api_version="2024-12-01-preview",
        temperature=0.1, 
        max_tokens=4000,
        request_timeout=60
    )

# ==========================================
# 3. 解析 JSON 文件，提取对话
# ==========================================
def parse_chat_history(json_data):
    my_wxid = "wxid_vkvdpam2hubc22"
    session = json_data.get("session", {})
    client_wxid = session.get("wxid", "未知微信")
    client_name = session.get("nickname", "未知姓名")
    
    chat_text = []
    messages = json_data.get("messages", [])
    
    for msg in messages:
        if msg.get("type") != "文本消息":
            continue
            
        sender_wxid = msg.get("senderUsername")
        if sender_wxid == my_wxid:
            sender = "我方(销售)"
        else:
            sender = f"客户({client_name})"
            
        content = msg.get("content", "")
        # 为了节约 token 和更直观，只传入关键文本
        chat_text.append(f"{sender}: {content}")
        
    return "\n".join(chat_text), client_wxid, client_name

# ==========================================
# 4. 单个文件处理逻辑
# ==========================================
def process_single_file(file_path, prompt_chain):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        chat_str, wxid, name = parse_chat_history(data)
        
        if not chat_str.strip():
            return None
            
        # 调用大模型提取并归纳问题
        result = prompt_chain.invoke({"chat_text": chat_str})
        
        extracted_data = []
        for q in result.questions:
            extracted_data.append({
                "核心问题分类": q.category,
                "问题具体描述": q.description
            })
            
        return extracted_data
        
    except Exception as e:
        print(f"\n[错误] 处理文件 {os.path.basename(file_path)} 时出错: {str(e)}")
        return None

# ==========================================
# 5. 主程序入口
# ==========================================
def main():
    base_dir = r"D:\旭小姐阳台\客户档案聊天记录\20260506"
    
    print(f"正在扫描目录: {base_dir} ...")
    if not os.path.exists(base_dir):
        print(f"目录不存在: {base_dir}")
        return

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
    
    llm = get_llm()
    structured_llm = llm.with_structured_output(CustomerQuestions)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的销售文本分析专家。你的任务是阅读我方销售与客户的聊天记录。
请找出**客户**（非我方销售）提出的所有疑问、咨询和问题，并且**将语义相近的问题进行归纳和合并**（不要输出繁琐的问题明细）。
例如：客户分别问了“这个多大？”、“长宽是多少？”，请将其合并归纳为一个核心问题，分类为“尺寸问题”，描述为“询问具体长宽和大小”。
注意：
1. 仅提取客户提出的问题，忽略销售的提问。
2. 尽可能地高度概括，提炼出核心。
3. 如果客户没有提出任何问题，请返回空列表。"""),
        ("user", "聊天记录如下：\n{chat_text}")
    ])
    
    chain = prompt | structured_llm

    results = []
    
    max_workers = min(10, total_files)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_file, fp, chain): fp for fp in json_files}
        
        for future in tqdm(as_completed(futures), total=total_files, desc="问题提取与归纳进度"):
            res_list = future.result()
            if res_list:
                results.extend(res_list)
                
    # ==========================================
    # 6. 全局语义合并与导出 Excel
    # ==========================================
    if results:
        df = pd.DataFrame(results)
        # 按分类分组汇总
        grouped = df.groupby('核心问题分类')['问题具体描述'].apply(list).to_dict()
        
        structured_merge_llm = llm.with_structured_output(MergedCategory)
        merge_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的文本数据清理专家。你的任务是将属于同一个分类下的客户问题列表进行【语义去重和合并】。\n"
                       "要求：\n"
                       "1. 将表达相同意思或非常相近的问题合并为一条。\n"
                       "2. 保留不同的问题点，不要遗漏。\n"
                       "3. 语言简练，直接输出合并后的独立问题描述列表。"),
            ("user", "分类名称：{category}\n问题列表：\n{questions}")
        ])
        merge_chain = merge_prompt | structured_merge_llm
        
        def merge_category(category, descriptions):
            unique_desc = list(set(descriptions))
            if len(unique_desc) <= 1:
                return category, unique_desc
            text = "\n".join([f"- {d}" for d in unique_desc])
            try:
                res = merge_chain.invoke({"category": category, "questions": text})
                if hasattr(res, 'merged_descriptions'):
                    return category, res.merged_descriptions
            except Exception:
                pass
            return category, unique_desc

        print(f"\n提取到 {len(results)} 条初始问题，开始按 {len(grouped)} 个分类进行全局语义合并...")
        final_rows = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(merge_category, cat, descs): cat for cat, descs in grouped.items()}
            for future in tqdm(as_completed(futures), total=len(futures), desc="全局合并进度"):
                cat, merged_list = future.result()
                for d in merged_list:
                    final_rows.append({
                        "核心问题分类": cat,
                        "问题具体描述": d
                    })
                    
        final_df = pd.DataFrame(final_rows)
        final_df.insert(0, '序号', range(1, len(final_df) + 1)) 
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        random_suffix = random.randint(1000, 9999)
        output_file = os.path.join(base_dir, f"{date_str}_客户核心问题归纳_{random_suffix}.xlsx")
        
        try:
            df.to_excel(output_file, index=False)


            print(f"\n[成功] 提取归纳完成！成功处理了 {len(results)} 条核心问题数据。")
            print(f"[文件] 结果已保存至: {output_file}")
        except Exception as e:

            print(f"\n[失败] 保存 Excel 失败: {e}")
            fallback_path = f"{date_str}_客户核心问题归纳_{random_suffix}.xlsx"
            df.to_excel(fallback_path, index=False)
            print(f"已备用保存至当前目录: {fallback_path}")
    else:
        print("\n未提取到任何客户问题数据。")

if __name__ == "__main__":
    main()