import pandas as pd
import os
from tqdm import tqdm
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor, as_completed

class MergedCategory(BaseModel):
    merged_descriptions: list[str] = Field(description="合并相同语义后的核心问题描述列表")

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

def merge_category(chain, category, descriptions):
    # 首先进行基础的字符串去重
    unique_desc = list(set(descriptions))
    if len(unique_desc) <= 1:
        return category, unique_desc
    
    # 使用大模型进行语义合并
    text = "\n".join([f"- {d}" for d in unique_desc])
    try:
        res = chain.invoke({"category": category, "questions": text})
        if hasattr(res, 'merged_descriptions'):
            return category, res.merged_descriptions
    except Exception as e:
        pass
    return category, unique_desc

def main():
    # 读取您刚才生成的 Excel 文件
    file_path = r"D:\旭小姐阳台\客户档案聊天记录\20260506\2026-05-06_客户核心问题归纳_9248.xlsx"
    if not os.path.exists(file_path):
        print(f"找不到文件: {file_path}")
        return

    df = pd.read_excel(file_path)
    
    # 按照“核心问题分类”进行分组，将同一个分类下的所有描述收集为列表
    grouped = df.groupby('核心问题分类')['问题具体描述'].apply(list).to_dict()
    
    llm = get_llm()
    structured_llm = llm.with_structured_output(MergedCategory)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的文本数据清理专家。你的任务是将属于同一个分类下的客户问题列表进行【语义去重和合并】。\n"
                   "要求：\n"
                   "1. 将表达相同意思或非常相近的问题合并为一条。\n"
                   "2. 保留不同的问题点，不要遗漏。\n"
                   "3. 语言简练，直接输出合并后的独立问题描述列表。"),
        ("user", "分类名称：{category}\n问题列表：\n{questions}")
    ])
    chain = prompt | structured_llm
    
    final_rows = []
    print(f"共发现 {len(grouped)} 个核心问题分类，开始进行大模型语义合并...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(merge_category, chain, cat, descs): cat for cat, descs in grouped.items()}
        for future in tqdm(as_completed(futures), total=len(futures), desc="分类合并进度"):
            cat, merged_list = future.result()
            for d in merged_list:
                final_rows.append({
                    "核心问题分类": cat,
                    "问题具体描述": d
                })
                
    final_df = pd.DataFrame(final_rows)
    # 重新生成序号
    final_df.insert(0, '序号', range(1, len(final_df) + 1))
    
    output_file = file_path.replace(".xlsx", "_去重合并最终版.xlsx")
    final_df.to_excel(output_file, index=False)
    print(f"\n[成功] 语义合并完成！原本 933 条数据被合并优化为 {len(final_df)} 条独立核心问题。")
    print(f"[文件] 最终结果已保存至: {output_file}")

if __name__ == "__main__":
    main()