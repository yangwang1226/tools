import os
import json
import random
import re
import pandas as pd
from datetime import datetime, timedelta
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
    
        # 过滤掉指定账号和群聊
    excluded_nicknames = ["钢镚爸爸", "爱德文老斯", "旭_fang", "史旭", "庭院设计师-旭小姐", "REN"]
    if client_name in excluded_nicknames:
        return None, None, None, None, None, 0, set(), 0, False, False, False, {}
    
    # 过滤掉群聊（群聊的wxid通常包含@chatroom）
    if "@chatroom" in client_wxid:
        return None, None, None, None, None, 0, set(), 0, False, False, False, {}
    
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
        
        client_msg_count = 0
    client_active_days = set()
    mentioned_renovation = False
    mentioned_next_week = False
    mentioned_next_month = False
    turns = 0
    last_sender_is_client = None
    delivery_info = {}

    for msg in messages:
        msg_type = msg.get("type")
        sender_wxid = msg.get("senderUsername")
        is_from_client = (sender_wxid != my_wxid)
        content = msg.get("content", "")
        time_str = msg.get("formattedTime", "")
        
        # 场景1：处理转账卡片消息（最可靠的付款证据）
        if msg_type == "转账卡片":
            is_send = msg.get("isSend", 0)  # 0表示接收，1表示发送
            
            # 只统计客户转给旭小姐的转账（isSend=0）
            if is_send == 0:
                # 提取转账金额，例如："转账[500.00元]"
                amount_match = re.search(r"转账\[(\d+\.?\d*)元\]", content)
                if amount_match:
                    transfer_amount = float(amount_match.group(1))
                    # 累加多笔转账金额
                    existing_amount = delivery_info.get("金额原始", 0.0)
                    delivery_info["金额原始"] = existing_amount + transfer_amount
                    delivery_info["金额"] = str(delivery_info["金额原始"])
                    delivery_info["is_paid"] = "是"
                    # 使用最后一笔客户转账时间作为成单日期
                    if time_str:
                        delivery_info["成单日期"] = time_str.split(" ")[0]
            continue
        
                # 处理文本消息
        if msg_type != "文本消息":
            continue
        
        # 场景2：旭小姐发送交付单（明确的成单证据）
        if not is_from_client and "旭小姐产品交付单" in content:
            delivery_info["is_paid"] = "是"
            if time_str:
                delivery_info["成单日期"] = time_str.split(" ")[0]
            
            # 提取交付单信息
            name_match = re.search(r"客户姓名：([^\n]+)", content)
            if name_match: delivery_info["客户姓名"] = name_match.group(1).strip()
            
            phone_match = re.search(r"电话：([^\n]+)", content)
            if phone_match: delivery_info["电话"] = phone_match.group(1).strip()
            
            addr_match = re.search(r"地址：([^\n]+)", content)
            if addr_match: delivery_info["快递地址"] = addr_match.group(1).strip()
            
            price_match = re.search(r"价格：([^\n]+)", content)
            if price_match: delivery_info["金额"] = price_match.group(1).strip()
            
            track_match = re.search(r"快递单号：([^\n]+)", content)
            if track_match:
                track_num = track_match.group(1).strip()
                delivery_info["快递单号"] = track_num
                if track_num.startswith("SF"):
                    delivery_info["快递公司"] = "顺丰"
                elif track_num.startswith("JD"):
                    delivery_info["快递公司"] = "京东"
                else:
                    delivery_info["快递公司"] = "其他"
        
        # 场景3：旭小姐发送快递单号（成单证据）
        if not is_from_client and "快递单号" in content:
            track_match = re.search(r"快递单号[：:](\S+)", content)
            if track_match:
                delivery_info["is_paid"] = "是"
                if time_str:
                    delivery_info["成单日期"] = time_str.split(" ")[0]
                track_num = track_match.group(1).strip()
                delivery_info["快递单号"] = track_num
        
        # 场景4：客户表达已付款
        if is_from_client:
            payment_keywords = ["已付款", "已支付", "付款了", "支付了", "已转账", "已经付", "付过了", 
                              "扫码付", "扫码支付", "支付宝付", "微信付", "刚付"]
            if any(kw in content for kw in payment_keywords):
                delivery_info["is_paid"] = "是"
                if time_str:
                    delivery_info["成单日期"] = time_str.split(" ")[0]
        
                # 场景5：客户发送完整收货信息（仅记录，不自动判定为已付款）
        # 注意：仅提供收货信息不能判定为付款，必须配合其他明确的付款证据
        if is_from_client:
            has_phone = bool(re.search(r"1[3-9]\d{9}", content))  # 手机号
            has_address = any(kw in content for kw in ["市", "区", "县", "街道", "小区", "号楼", "单元", "室"])
            
            if has_phone and has_address:
                # 仅记录收货信息，不判定为已付款
                delivery_info["收货信息已提供"] = "是"
                # 不设置 is_paid 和成单日期
        
        # 组装聊天文本（用于大模型分析）
        if sender_wxid == my_wxid:
            sender = "我方(销售)"
        else:
            sender = f"客户({client_name})"

                # 统计客户活跃度
        if is_from_client:
            client_msg_count += 1
            if time_str:
                client_active_days.add(time_str.split(" ")[0])
            if "装修" in content:
                mentioned_renovation = True
            if "下周" in content:
                mentioned_next_week = True
            if "下个月" in content:
                mentioned_next_month = True
        
        # 统计对话轮次
        if last_sender_is_client is not None and last_sender_is_client != is_from_client:
            turns += 1
        last_sender_is_client = is_from_client
        
        chat_text.append(f"[{time_str}] {sender}: {content}")
        
    actual_turns = turns // 2
        
    return "\n".join(chat_text), client_wxid, client_name, first_time, last_time, client_msg_count, client_active_days, actual_turns, mentioned_renovation, mentioned_next_week, mentioned_next_month, delivery_info

# ==========================================
# 4. 单个文件处理逻辑
# ==========================================
def process_single_file(file_path, prompt_chain, contacts_map, amount_map):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
            
        chat_str, wxid, name, first_time, last_time, client_msg_count, client_active_days, turns, mentioned_renovation, mentioned_next_week, mentioned_next_month, delivery_info = parse_chat_history(data)
        
        # 如果返回None，说明被过滤了
        if chat_str is None:
            return None
        
                # 如果没有文本对话，直接返回基础信息
        if not chat_str.strip():
            return None
            
        # 根据 wxid 获取通讯录信息
        user_info_dict = contacts_map.get(wxid, {})
        nickname = user_info_dict.get('nickname', name)
        remark = user_info_dict.get('remark', '无')
        user_info_str = f"微信ID: {wxid}\n昵称: {nickname}\n备注: {remark}"
            
        # 调用大模型提取结构化数据（增加防抖重试机制）
        import time
        max_retries = 3
        content = ""
        for attempt in range(max_retries):
            try:
                content = prompt_chain.invoke({"chat_text": chat_str, "user_info": user_info_str})
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
                    "is_paid": "是否成单",
                                        "amount": "金额",
                    "order_time": "成单日期",
                    "gender": "性别",
                    "province_city": "省份",
                    "product_needs": "产品需求",
                    "shipping_address": "快递地址",
                    "remark": "备注"
                }
        
                                # 重新组装为中文键名的字典
        result_dict = {key_mapping[k]: v for k, v in raw_dict.items() if k in key_mapping}
        
        # 如果金额是"需人工确认"，尝试从金额明细表中查找
        if result_dict.get("金额") == "需人工确认":
            # 先尝试通过昵称查找
            if name in amount_map:
                result_dict["金额"] = amount_map[name]
            # 如果通讯录中有昵称，也尝试查找
            elif nickname in amount_map:
                result_dict["金额"] = amount_map[nickname]
            # 如果还是找不到，保持"需人工确认"
        
                # 解析备注: 北京|男|中|花箱组摆
        # 只有当备注是标准格式（至少包含4个|分隔的字段）时才解析
        remark_parts = remark.split('|')
        if len(remark_parts) >= 4:
            r_province = remark_parts[0].strip() if remark_parts[0].strip() else "未知"
            r_gender = remark_parts[1].strip() if remark_parts[1].strip() else "未知"
            r_intent = remark_parts[2].strip() if remark_parts[2].strip() else "未知"
            r_product = remark_parts[3].strip() if remark_parts[3].strip() else "未知"
        else:
            # 备注格式不标准，全部设为未知
            r_province = "未知"
            r_gender = "未知"
            r_intent = "未知"
            r_product = "未知"

        # 产品标准化分类
        std_product = "未知"
        if r_product != "未知":
            if "花箱" in r_product:
                std_product = "花箱"
            elif "阳台" in r_product:
                std_product = "阳台组摆"
            elif "庭院" in r_product or "院" in r_product or "花园" in r_product:
                std_product = "庭院组摆"
            else:
                std_product = "其他"

                # 结合备注的提取优先填充
        if r_province != "未知": result_dict["省份"] = r_province
        if r_gender != "未知": result_dict["性别"] = r_gender
        result_dict["咨询产品"] = std_product

        # 意向判断
        final_intent = "中"
        if client_msg_count == 0:
            final_intent = "低"
        elif "高" in r_intent or len(client_active_days) >= 2 or turns >= 20:
            final_intent = "高"
        elif "低" in r_intent:
            final_intent = "低"
            
        # 下次跟进时间
        try:
            last_date_obj = datetime.strptime(last_time, "%Y-%m-%d").date() if last_time != "未知" else datetime.now().date()
        except:
            last_date_obj = datetime.now().date()
            
        if mentioned_renovation and mentioned_next_week:
            next_follow_up = (last_date_obj + timedelta(days=7)).strftime("%Y-%m-%d")
        elif mentioned_renovation and mentioned_next_month:
            next_follow_up = (last_date_obj + timedelta(days=30)).strftime("%Y-%m-%d")
        else:
            if final_intent == "高":
                next_follow_up = (last_date_obj + timedelta(days=2)).strftime("%Y-%m-%d")
            else:
                next_follow_up = (last_date_obj + timedelta(days=5)).strftime("%Y-%m-%d")

                # 成单周期和成单月份计算
        order_cycle = "未成单"
        order_month = "未知"
        order_time_val = result_dict.get("成单日期", "")
        if order_time_val and "未知" not in order_time_val and first_time != "未知":
            try:
                # 尝试提取成单时间的前10位YYYY-MM-DD
                o_date = datetime.strptime(order_time_val[:10].strip(), "%Y-%m-%d").date()
                f_date = datetime.strptime(first_time, "%Y-%m-%d").date()
                cycle_days = (o_date - f_date).days
                order_cycle = f"{cycle_days}天"
                # 提取成单月份
                order_month = order_time_val[:7]  # YYYY-MM格式
            except:
                pass

            # 手动插入固定字段
        result_dict["客户微信"] = wxid
        result_dict["客户名称"] = name
        result_dict["添加好友日期"] = first_time
        result_dict["上次聊天日期"] = last_time
        
                # 添加添加好友月份（格式：2026-05）
        if first_time != "未知":
            try:
                month_str = first_time[:7]  # 提取YYYY-MM部分
                result_dict["添加好友月份"] = month_str
            except:
                result_dict["添加好友月份"] = "未知"
        else:
            result_dict["添加好友月份"] = "未知"
            
        result_dict["聊天意向"] = final_intent
        result_dict["下次跟进日期"] = next_follow_up
        result_dict["成单周期"] = order_cycle
        result_dict["成单月份"] = order_month

                # 如果解析到了交付单或转账信息，执行覆盖和补充
        if delivery_info:
            # 只有当交付单中的客户姓名不为空时，才覆盖昵称
            if "客户姓名" in delivery_info and delivery_info["客户姓名"].strip():
                result_dict["客户名称"] = delivery_info["客户姓名"]
            if "电话" in delivery_info: result_dict["电话"] = delivery_info["电话"]
            if "快递地址" in delivery_info: result_dict["快递地址"] = delivery_info["快递地址"]
            # 金额优先使用转账卡片或交付单中的金额
            if "金额" in delivery_info: result_dict["金额"] = delivery_info["金额"]
            # 成单日期优先使用转账卡片或交付单中的日期
            if "成单日期" in delivery_info: result_dict["成单日期"] = delivery_info["成单日期"]
            if "快递单号" in delivery_info: result_dict["快递单号"] = delivery_info["快递单号"]
            if "快递公司" in delivery_info: result_dict["快递公司"] = delivery_info["快递公司"]
                        # 如果有明确的付款证据，标记为已成单
            if "is_paid" in delivery_info and delivery_info["is_paid"] == "是":
                result_dict["是否成单"] = "是"
                # 如果已成单但没有金额，尝试从金额明细表查找
                if "金额" not in delivery_info or not delivery_info["金额"]:
                    if name in amount_map:
                        result_dict["金额"] = amount_map[name]
                    elif nickname in amount_map:
                        result_dict["金额"] = amount_map[nickname]
                    else:
                        result_dict["金额"] = "需人工确认"

                # 最终成单月份：必须在 delivery_info 覆盖成单日期之后再计算
        final_order_date = result_dict.get("成单日期", "")
        if final_order_date and isinstance(final_order_date, str) and "未知" not in final_order_date and len(final_order_date) >= 7:
            # 统一只保留年月日部分 YYYY-MM-DD
            result_dict["成单日期"] = final_order_date[:10]
            result_dict["成单月份"] = final_order_date[:7]  # YYYY-MM格式
        else:
            result_dict["成单月份"] = "未知"

        # 增加用户类型判断逻辑：是否成单 为 是，则为老客户
        is_paid_val = str(result_dict.get("是否成单", "")).strip()
        if is_paid_val == "是":
            result_dict["客户类型"] = "老客户"
        else:
            result_dict["客户类型"] = "新客户"
        
        return result_dict
        
    except Exception as e:
        print(f"\n[错误] 处理文件 {os.path.basename(file_path)} 时出错: {str(e)}")
        return None

# ==========================================
# 5. 主程序入口
# ==========================================
def main():
    # 指向 chat_message 文件夹
    base_dir = "chat_message\\202605"
    
    # 动态查找通讯录文件
    contacts_file = None
    if os.path.exists(base_dir):
        for f in os.listdir(base_dir):
            if f.startswith("通讯录_") and f.endswith((".xlsx", ".xls", ".csv")):
                contacts_file = os.path.join(base_dir, f)
                break

        # 读取通讯录文件，构建映射字典
    contacts_map = {}
    if contacts_file and os.path.exists(contacts_file):
        try:
            df_contacts = pd.read_excel(contacts_file)
            for _, row in df_contacts.iterrows():
                wxid = str(row.get('微信ID', '')).strip()
                wechat_num = str(row.get('微信号', '')).strip()
                nickname = str(row.get('昵称', '')).strip()
                remark = str(row.get('备注', '')).strip()
                
                info = {'nickname': nickname, 'remark': remark}
                if wxid and wxid != 'nan':
                    contacts_map[wxid] = info
                if wechat_num and wechat_num != 'nan':
                    contacts_map[wechat_num] = info
            print(f"成功加载通讯录，共读取 {len(contacts_map)} 个独立微信账号信息。")
        except Exception as e:
            print(f"读取通讯录文件失败: {e}")
    else:
        print(f"警告：未在 {base_dir} 目录下找到以 '通讯录_' 开头的文件，请检查！")
    
    # 读取金额明细文件，构建昵称到金额的映射
    amount_map = {}
    amount_file = os.path.join(base_dir, "金额明细-20241015.xlsx")
    if os.path.exists(amount_file):
        try:
            df_amount = pd.read_excel(amount_file)
            # 假设金额明细表有"昵称"和"金额"两列
            for _, row in df_amount.iterrows():
                nickname = str(row.get('昵称', '')).strip()
                amount = str(row.get('金额', '')).strip()
                if nickname and amount and nickname != 'nan' and amount != 'nan':
                    amount_map[nickname] = amount
            print(f"成功加载金额明细，共读取 {len(amount_map)} 条金额信息。")
        except Exception as e:
            print(f"读取金额明细文件失败: {e}")
    else:
        print(f"提示：未找到金额明细文件 {amount_file}，将跳过金额自动匹配。")

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
3. 性别判定：必须结合【用户信息】(昵称、备注)进行判定。如果“备注”或“昵称”中包含明显的性别指示词（如姐、哥、先生、女士、妈、爸等），应优先作为判断性别的依据。然后再结合聊天记录中的语气词、话题偏好综合判断。

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
        ("user", "【用户信息】\n{user_info}\n\n【聊天记录如下】\n{chat_text}")
    ])
    
    from langchain_core.output_parsers import StrOutputParser
    # 加上 StrOutputParser 直接将返回转化为字符串
    chain = prompt | llm | StrOutputParser()

    results = []
    processed_files = set()  # 用于跟踪已处理的文件，防止重复
    
        # 使用线程池并发处理，加速大模型请求
    max_workers = min(10, total_files)  # 最多10个并发
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = {executor.submit(process_single_file, fp, chain, contacts_map, amount_map): fp for fp in json_files}
        
        # 配合 tqdm 显示进度条
        for future in tqdm(as_completed(futures), total=total_files, desc="数据提取进度"):
            file_path = futures[future]
            res = future.result()
            if res:
                # 防止同一文件被处理多次
                if file_path not in processed_files:
                    results.append(res)
                    processed_files.add(file_path)
                else:
                    print(f"\n⚠️ 警告：文件 {os.path.basename(file_path)} 被重复处理，已忽略重复结果")
                
        # ==========================================
        # 6. 数据整理与导出 Excel
        # ==========================================
        if results:
            df = pd.DataFrame(results)
        
            # 基于客户名称去重，优先保留有金额的记录
            if "客户名称" in df.columns:
                original_count = len(df)
            
                # 添加辅助列：判断金额是否有效
                df['_has_amount'] = df['金额'].apply(
                    lambda x: 0 if pd.isna(x) or str(x).strip() in ['', '0', '未知', '需人工确认'] else 1
                )
            
                # 按客户名称分组，先按是否有金额排序（有金额的排前面），再去重
                df = df.sort_values(by=['客户名称', '_has_amount'], ascending=[True, False])
                df = df.drop_duplicates(subset=['客户名称'], keep='first')
            
                # 删除辅助列
                df = df.drop(columns=['_has_amount'])
            
                duplicates_removed = original_count - len(df)
                if duplicates_removed > 0:
                    print(f"\n⚠️ 检测到 {duplicates_removed} 条重复记录（基于客户名称）已去除，优先保留有金额的记录")
        
                                                                # 整理所需的列顺序
        columns_order = [
                    "客户名称", "电话", "性别", "省份", "是否成单", "金额", "成单月份", "成单日期",
                    "客户类型", "聊天意向", "添加好友日期", "上次聊天日期", "下次跟进日期",
                    "咨询产品", "快递地址", "快递公司", "快递单号", "备注"
                ]
        
        # 过滤并排序存在的列
        final_cols = [col for col in columns_order if col in df.columns]
        df = df[final_cols]
        
                # 按照添加好友日期倒序排列
        if "添加好友日期" in df.columns:
            df = df.sort_values(by="添加好友日期", ascending=False).reset_index(drop=True) 
        
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
        # 7. 转化率统计功能
        # ==========================================
        print("\n" + "="*50)
        print("📊 转化率统计")
        print("="*50)
        print("请输入需要统计的时间范围：")
        print("  格式1（单月）：2026-05")
        print("  格式2（多月）：2026-05到2026-06")
        print("  输入 'q' 或 'quit' 退出")
        
        while True:
            time_input = input("\n请输入时间范围: ").strip()
            
            if time_input.lower() in ['q', 'quit', '']:
                print("\n👋 已退出统计功能。")
                break
            
            try:
                # 解析输入的时间范围
                if "到" in time_input:
                    # 多月格式：2026-05到2026-06
                    parts = time_input.split("到")
                    start_month = parts[0].strip()
                    end_month = parts[1].strip()
                else:
                    # 单月格式：2026-05
                    start_month = time_input
                    end_month = time_input
                
                # 验证时间格式
                datetime.strptime(start_month, "%Y-%m")
                datetime.strptime(end_month, "%Y-%m")

                # 筛选出添加好友日期在指定范围内的客户总数
                # 先检查列是否存在，如果不存在就从添加好友日期提取
                if "添加好友月份" not in df.columns:
                    df["添加好友月份"] = df["添加好友日期"].apply(
                        lambda x: x[:7] if isinstance(x, str) and x != "未知" and len(x) >= 7 else "未知"
                    )

                df_total = df[
                    (df["添加好友月份"] >= start_month) & 
                    (df["添加好友月份"] <= end_month)
                ]
                total_customers = len(df_total)
                
                                # 筛选出成单月份在指定范围内的成单客户数
                df_paid = df[
                    (df["成单月份"] >= start_month) & 
                    (df["成单月份"] <= end_month) &
                    (df["是否成单"] == "是")
                ]
                paid_customers = len(df_paid)
                
                # 计算转化率
                if total_customers > 0:
                    conversion_rate = (paid_customers / total_customers) * 100
                else:
                    conversion_rate = 0
                
                # 输出统计结果
                print("\n" + "-"*50)
                if start_month == end_month:
                    print(f"📅 统计时间范围: {start_month}")
                else:
                    print(f"📅 统计时间范围: {start_month} 到 {end_month}")
                print("-"*50)
                print(f"👥 客户总数（添加好友日期在范围内）: {total_customers} 人")
                print(f"💰 成单客户数（成单月份在范围内）: {paid_customers} 人")
                print(f"📈 转化率: {conversion_rate:.2f}%")
                print("-"*50)
                
            except ValueError as e:
                print(f"\n❌ 时间格式错误，请使用正确格式（例如：2026-05 或 2026-05到2026-06）")
            except Exception as e:
                print(f"\n❌ 统计出错: {str(e)}")
        else:
            print("\n未提取到任何有效数据。")

if __name__ == "__main__":
    main()