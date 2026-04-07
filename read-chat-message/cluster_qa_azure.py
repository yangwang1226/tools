import pandas as pd
import json
import os
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
# os.environ["PYDEVD_USE_CYTHON"] = "NO"
# os.environ["PYDEVD_USE_FRAME_EVAL"] = "NO"


def init_llm():
    """初始化 Azure OpenAI 模型"""
    # 直接将模型参数明文配置到 AzureChatOpenAI 中
    llm = AzureChatOpenAI(
        azure_endpoint="https://menshen.test.xdf.cn/",
        openai_api_key="c8575027653b42b1b47747f0b4ab135b",
        azure_deployment="gpt-4o",
        openai_api_version="2024-12-01-preview",
        temperature=0.3,
        max_tokens=4000,        # 最大输出token数
        request_timeout=60      # 请求超时时间（秒）
    )
    return llm

def read_excel_data(file_path):
    """读取Excel文件并提取QA数据"""
    print(f"正在读取文件: {file_path}")
    df = pd.read_excel(file_path)
    
    # 假设你的Excel中有 '问题' 和 '答案' 两列
    # 如果列名不同，请根据实际情况修改 '问题' 和 '答案'
    qa_list = []
    for index, row in df.iterrows():
        question = str(row.get('问题', row.iloc[0]))
        answer = str(row.get('答案', row.iloc[1] if len(row) > 1 else ''))
        qa_list.append({"问题": question, "答案": answer})
        
    return qa_list

def cluster_and_summarize_with_llm(llm, qa_batch):
    """使用 Azure OpenAI 对一批QA进行聚类和汇总"""
    
    # 将批量数据转换为JSON字符串以传递给大模型
    qa_text = json.dumps(qa_batch, ensure_ascii=False, indent=2)
    
    system_prompt = "你是一个严谨且逻辑清晰的数据分析与知识整理专家。"
    user_prompt = f"""
    请你作为一名专业的产品知识库整理专家。以下是一批产品相关的问答（QA）数据。
    请根据问题的主题、意图或相关性，将这些问答进行“聚类”和“汇总”。
    
    要求：
    1. 提炼出几个核心类别（例如：产品功能、价格问题、售后服务、安装指南等）。
    2. 在每个类别下，生成一个汇总性的概述。
    3. 列出该类别下涵盖的具体问题。
    4. 尽量消除重复或相似度极高的表述。
    
    以下是待处理的QA数据：
    {qa_text}
    
    请以清晰的Markdown格式输出你的聚类汇总结果。
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        print(f"调用 Azure OpenAI 时发生错误: {e}")
        return ""

def main():
    file_path = "产品知识库_QA_去重版.xlsx"
    output_file = "聚类汇总结果.md"
    
    if not os.path.exists(file_path):
        print(f"错误: 找不到文件 {file_path}")
        return
        
    qa_list = read_excel_data(file_path)
    print(f"共读取到 {len(qa_list)} 条QA记录。")
    
    # 初始化 LLM
    llm = init_llm()
    
    # 因为大模型有上下文长度限制，如果数据量特别大，需要分批处理。
    # 这里设置每批处理 50 条记录
    batch_size = 50
    all_summaries = []
    
    print("开始调用大模型进行聚类汇总...")
    for i in range(0, len(qa_list), batch_size):
        batch = qa_list[i:i+batch_size]
        print(f"正在处理第 {i+1} 到 {min(i+batch_size, len(qa_list))} 条记录...")
        
        summary = cluster_and_summarize_with_llm(llm, batch)
        if summary:
            all_summaries.append(summary)
            
    # 将所有批次的汇总结果拼接写入文件
    final_output = "\n\n---\n\n".join(all_summaries)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 产品知识库QA聚类汇总\n\n")
        f.write(final_output)
        
    print(f"\n处理完成！聚类汇总结果已保存至 {output_file}")

if __name__ == "__main__":
    main()