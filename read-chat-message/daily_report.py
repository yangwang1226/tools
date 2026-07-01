import os
import json
import re
from datetime import datetime, timedelta
from calendar import monthrange
from collections import defaultdict
import pandas as pd

# ==========================================
# 日报统计程序
# ==========================================

class DailyReportAnalyzer:
    def __init__(self, base_dir, start_date, end_date):
        self.base_dir = base_dir
        self.start_date = start_date
        self.end_date = end_date
        self.my_wxid = "wxid_vkvdpam2hubc22"
        
        # 统计数据
        self.new_contacts_count = 0  # 今天添加的人数（个人微信）
        self.wechat_work_count = 0  # 企业微信添加人数（从Excel读取）
        self.platform_stats = defaultdict(int)  # 各平台新增人数
        self.high_intent_count = 0  # 高意向人数
        self.old_unpaid_count = 0  # 未成单老客户回访数
        self.old_paid_count = 0  # 成单老客户回访数
        
        # 今日成单统计
        self.today_paid_count = 0
        self.today_paid_amount = 0.0
        self.paid_under_500 = 0
        self.paid_500_to_1000 = 0
        self.paid_over_1000 = 0
        
        # 详细列表
        self.new_contacts_list = []  # 新增联系人详情（个人微信）
        self.wechat_work_list = []  # 企业微信新增客户详情
        self.platform_details = defaultdict(list)  # 各平台新增详情
        self.high_intent_list = []  # 高意向客户列表
        self.old_unpaid_list = []  # 未成单老客户回访列表
        self.old_paid_list = []  # 成单老客户回访列表
    
    def extract_platform(self, remark=""):
        """个人微信来源平台固定为抖音庭院"""
        return "抖音庭院"
    
    def map_wechat_work_source(self, source=""):
        """映射企业微信来源到平台
        通过获客链接添加 -> 小红书
        客户通过扫一扫添加 -> 抖音主账号
        """
        if "获客链接" in source:
            return "小红书"
        elif "扫一扫" in source:
            return "抖音主账号"
        else:
            return "企业微信其他"
    
    def is_high_intent(self, remark=""):
        """判断是否为高意向客户（从备注中识别）"""
        # 从备注中识别（格式：省份|性别|意向|产品|平台）
        if remark and "|" in remark:
            parts = remark.split("|")
            if len(parts) >= 3:
                intent = parts[2].strip()
                if intent == "高":
                    return True
        return False
    
    def parse_deal_amount_from_remark(self, remark=""):
        """从备注中解析成单金额
        格式示例：北京|男|成单|花箱|299
        返回：成单金额（float），如果没有找到则返回0
        """
        if not remark or "成单" not in remark:
            return 0.0
        
        # 分割备注
        parts = remark.split("|")
        
        # 从成单后面的部分查找数字
        for i, part in enumerate(parts):
            if "成单" in part:
                # 检查后续的部分
                for j in range(i + 1, len(parts)):
                    # 使用正则提取数字（支持整数和小数）
                    numbers = re.findall(r'\d+\.?\d*', parts[j])
                    if numbers:
                        try:
                            # 取最后一个数字作为金额
                            amount = float(numbers[-1])
                            return amount
                        except ValueError:
                            continue
        return 0.0
    
    def has_chat_on_date(self, messages):
        """检查统计日期范围内是否有聊天记录"""
        for msg in messages:
            time_str = msg.get("formattedTime", "")
            if time_str:
                msg_date = time_str.split(" ")[0]
                if self.start_date <= msg_date <= self.end_date:
                    return True
        return False
    
    def get_first_chat_date(self, messages):
        """获取第一次聊天日期"""
        if messages:
            first_time = messages[0].get("formattedTime", "")
            if first_time:
                return first_time.split(" ")[0]
        return None
        
    def get_today_payments(self, messages):
        """获取统计日期范围内的转账金额列表"""
        amounts = []
        for msg in messages:
            # 检查日期是否在范围内
            time_str = msg.get("formattedTime", "")
            if not time_str:
                continue
            msg_date = time_str.split(" ")[0]
            if not (self.start_date <= msg_date <= self.end_date):
                continue
                
            msg_type = msg.get("type")
            is_send = msg.get("isSend", 0)
            
            # 接收到的转账卡片
            if msg_type == "转账卡片" and is_send == 0:
                content = msg.get("content", "")
                # 从转账卡片xml中提取金额 (形如 <fee>1000.00</fee> 或者 ￥1000.00 等)
                # 这里尝试用正则提取数字
                import re
                match = re.search(r'(?:fee>|￥|转账金额|金额).*?(\d+(?:\.\d+)?)', content)
                if match:
                    try:
                        amount = float(match.group(1))
                        amounts.append(amount)
                    except ValueError:
                        pass
        return amounts
    
    def process_single_file(self, file_path, contacts_map):
        """处理单个聊天记录文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session = data.get("session", {})
            client_wxid = session.get("wxid", "")
            client_name = session.get("nickname", "未知")
            messages = data.get("messages", [])
            
            # 过滤群聊
            if "@chatroom" in client_wxid:
                return
            
            # 过滤指定账号
            excluded_nicknames = [
                "钢镚爸爸", "爱德文老斯", "旭_fang", "旭_F", 
                "史旭", "庭院设计师-旭小姐", "REN", "旭小姐的阳台花园（本人号）"
            ]
            if client_name in excluded_nicknames:
                return
            
            if not messages:
                return
            
            # 获取通讯录信息
            user_info = contacts_map.get(client_wxid, {})
            nickname = user_info.get('nickname', client_name)
            remark = user_info.get('remark', '')
            
            # 获取第一次聊天日期
            first_chat_date = self.get_first_chat_date(messages)
            
            # 检查统计区间内是否有聊天
            has_chat_today = self.has_chat_on_date(messages)
            
            # 是否已成单(根据备注判断)
            is_paid = "成单" in remark if remark else False
            
            # 从备注中解析成单金额
            remark_deal_amount = self.parse_deal_amount_from_remark(remark)
            
            # 获取区间内转账成单金额
            today_payments = self.get_today_payments(messages)
            
            # 如果有转账记录，使用转账金额
            if today_payments:
                for amount in today_payments:
                    self.today_paid_count += 1
                    self.today_paid_amount += amount
                    if amount < 500:
                        self.paid_under_500 += 1
                    elif amount <= 1000:
                        self.paid_500_to_1000 += 1
                    else:
                        self.paid_over_1000 += 1
            # 如果没有转账记录但备注显示成单，且备注中有金额，使用备注金额
            elif is_paid and remark_deal_amount > 0 and has_chat_today:
                self.today_paid_count += 1
                self.today_paid_amount += remark_deal_amount
                if remark_deal_amount < 500:
                    self.paid_under_500 += 1
                elif remark_deal_amount <= 1000:
                    self.paid_500_to_1000 += 1
                else:
                    self.paid_over_1000 += 1
            
            # 统计1：指定区间内添加的人数
            if first_chat_date and self.start_date <= first_chat_date <= self.end_date:
                self.new_contacts_count += 1
                platform = self.extract_platform(remark)
                self.platform_stats[platform] += 1
                
                self.new_contacts_list.append({
                    "客户名称": nickname,
                    "来源平台": platform,
                    "微信ID": client_wxid
                })
                self.platform_details[platform].append(nickname)
            
            # 统计2：高意向人数（通过备注第三段标识）
            if self.is_high_intent(remark):
                self.high_intent_count += 1
                self.high_intent_list.append({
                    "客户名称": nickname,
                    "备注": remark,
                    "微信ID": client_wxid
                })
            
            # 统计3：未成单老客户回访 (区间内有聊天 + 首次聊天在统计区间之前 + 备注未成单)
            if has_chat_today and first_chat_date and first_chat_date < self.start_date and not is_paid:
                self.old_unpaid_count += 1
                self.old_unpaid_list.append({
                    "客户名称": nickname,
                    "备注": remark,
                    "微信ID": client_wxid
                })
            
            # 统计4：成单回访 (今天有聊天 + 备注标识成单)
            if has_chat_today and is_paid:
                self.old_paid_count += 1
                self.old_paid_list.append({
                    "客户名称": nickname,
                    "备注": remark,
                    "微信ID": client_wxid
                })
        
        except Exception as e:
            print(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
    
    def load_wechat_work_customers(self):
        """加载企业微信客户列表"""
        customer_file = os.path.join(self.base_dir, "客户列表.xlsx")
        
        if not os.path.exists(customer_file):
            print(f"[警告] 未找到企业微信客户列表文件: {customer_file}")
            return
        
        try:
            # 跳过前3行说明文字，第4行（索引3）才是真正的表头
            df = pd.read_excel(customer_file, header=3)
            print(f"[成功] 加载企业微信客户列表，共 {len(df)} 条记录")
            
            # 过滤条件：添加人为"旭_F"
            df_filtered = df[df['添加人'] == '旭_F'].copy()
            print(f"[过滤] 添加人为'旭_F'的记录: {len(df_filtered)} 条")
            
            # 转换添加时间格式
            df_filtered['添加时间'] = pd.to_datetime(df_filtered['添加时间'], errors='coerce')
            
            # 筛选统计日期范围内的数据
            start_dt = datetime.strptime(self.start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(self.end_date, "%Y-%m-%d") + timedelta(days=1)  # 包含结束日期
            
            df_period = df_filtered[
                (df_filtered['添加时间'] >= start_dt) & 
                (df_filtered['添加时间'] < end_dt)
            ]
            
            self.wechat_work_count = len(df_period)
            print(f"[统计] {self.start_date} 至 {self.end_date} 企业微信新增: {self.wechat_work_count} 人")
            
            # 统计各平台来源
            for _, row in df_period.iterrows():
                customer_name = str(row.get('客户名称', '未知')).strip()
                source = str(row.get('来源', '')).strip()
                add_time = row.get('添加时间')
                
                # 映射来源到平台
                platform = self.map_wechat_work_source(source)
                self.platform_stats[platform] += 1
                
                # 记录详细信息
                self.wechat_work_list.append({
                    "客户名称": customer_name,
                    "来源平台": platform,
                    "添加时间": add_time.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(add_time) else "",
                    "原始来源": source
                })
                
                # 添加到平台详情
                self.platform_details[platform].append(customer_name)
            
        except Exception as e:
            print(f"[错误] 加载企业微信客户列表失败: {e}")
            import traceback
            traceback.print_exc()
    
    def analyze(self, contacts_map):
        """分析所有聊天记录"""
        # 先加载企业微信客户数据
        self.load_wechat_work_customers()
        
        json_files = [
            os.path.join(self.base_dir, f)
            for f in os.listdir(self.base_dir)
            if f.endswith('.json')
        ]
        
        print(f"\n[分析中] 正在分析 {self.start_date} 至 {self.end_date} 的个人微信聊天记录...")
        print(f"共发现 {len(json_files)} 个聊天记录文件")
        
        for file_path in json_files:
            self.process_single_file(file_path, contacts_map)
        
        print("[完成] 分析完成！\n")
    
    def print_report(self, show_details=False):
        """打印日报
        Args:
            show_details: 是否显示明细，默认False
        """
        print("=" * 60)
        print(f"[统计报告] 统计日期: {self.start_date} 至 {self.end_date}")
        print("=" * 60)
        
        # 计算总添加人数
        total_new_users = self.new_contacts_count + self.wechat_work_count
        
        # 格式化日期显示
        if self.start_date == self.end_date:
            date_display = self.start_date
        else:
            date_display = f"{self.start_date} 至 {self.end_date}"
        
        # 1. 新增添加人数（系统统计）
        print(f"\n[1] 个人微信新增用户: {self.new_contacts_count} 人")
        if show_details and self.new_contacts_list:
            print(f"   明细: {', '.join([c['客户名称'] for c in self.new_contacts_list])}")
        
        print(f"\n    企业微信新增用户: {self.wechat_work_count} 人")
        if show_details and self.wechat_work_list:
            print(f"   明细: {', '.join([c['客户名称'] for c in self.wechat_work_list])}")
        
        print(f"\n    {date_display} 总添加用户数: {total_new_users} 人")
        
        # 2. 各平台新增人数（包含个人微信和企业微信）
        print(f"\n[2] 新增人数来源平台统计:")
        for platform, count in sorted(self.platform_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {platform}: {count} 人")
            # 显示详细名单
            if show_details and platform in self.platform_details:
                names = self.platform_details[platform]
                # 限制显示长度，避免输出过长
                if len(names) <= 10:
                    print(f"     ({', '.join(names)})")
                else:
                    print(f"     ({', '.join(names[:10])} ... 等{len(names)}人)")
        
        # 3. 成单统计（提到高意向客户前面）
        if self.today_paid_count > 0:
            print(f"\n[3] 成单数量: {self.today_paid_count} 单 (总金额: {self.today_paid_amount:.2f} 元)")
            print(f"   - 500以下: {self.paid_under_500} 单")
            print(f"   - 500-1000: {self.paid_500_to_1000} 单")
            print(f"   - 1000以上: {self.paid_over_1000} 单")
        else:
            print(f"\n[3] 成单数量: 0 单")
        
        # 4. 高意向人数
        print(f"\n[4] 高意向客户数: {self.high_intent_count} 人")
        if show_details and self.high_intent_list:
            for c in self.high_intent_list:
                print(f"   - 备注: {c['备注']} | 昵称: {c['客户名称']}")
        
        # 5. 未成单老客户回访
        print(f"\n[5] 未成单老客户回访: {self.old_unpaid_count} 人")
        if show_details and self.old_unpaid_list:
            for c in self.old_unpaid_list:
                print(f"   - 备注: {c['备注']} | 昵称: {c['客户名称']}")
        
        # 6. 成单老客户回访
        print(f"\n[6] 成单老客户回访: {self.old_paid_count} 人")
        if show_details and self.old_paid_list:
            for c in self.old_paid_list:
                print(f"   - 备注: {c['备注']} | 昵称: {c['客户名称']}")
        
        print("\n" + "=" * 60)
    
    def export_to_excel(self, output_file):
        """导出详细数据到Excel"""
        total_new_users = self.new_contacts_count + self.wechat_work_count
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet1: 日报汇总
            summary_data = {
                "统计项目": [
                    "个人微信新增用户",
                    "企业微信新增用户",
                    "统计期间总添加用户",
                    "抖音庭院新增",
                    "抖音主账号新增",
                    "小红书新增",
                    "其他平台新增",
                    "高意向客户数",
                    "未成单老客户回访",
                    "成单老客户回访",
                    "成单数量",
                    "成单金额",
                    "成单(500以下)",
                    "成单(500-1000)",
                    "成单(1000以上)"
                ],
                "数量": [
                    self.new_contacts_count,
                    self.wechat_work_count,
                    total_new_users,
                    self.platform_stats.get("抖音庭院", 0),
                    self.platform_stats.get("抖音主账号", 0),
                    self.platform_stats.get("小红书", 0),
                    self.platform_stats.get("企业微信其他", 0),
                    self.high_intent_count,
                    self.old_unpaid_count,
                    self.old_paid_count,
                    self.today_paid_count,
                    self.today_paid_amount,
                    self.paid_under_500,
                    self.paid_500_to_1000,
                    self.paid_over_1000
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name="日报汇总", index=False)
            
            # Sheet2: 个人微信新增客户明细
            if self.new_contacts_list:
                df_new = pd.DataFrame(self.new_contacts_list)
                df_new.to_excel(writer, sheet_name="个人微信新增明细", index=False)
            
            # Sheet3: 企业微信新增客户明细
            if self.wechat_work_list:
                df_work = pd.DataFrame(self.wechat_work_list)
                df_work.to_excel(writer, sheet_name="企业微信新增明细", index=False)
            
            # Sheet4: 高意向客户
            if self.high_intent_list:
                df_high = pd.DataFrame(self.high_intent_list)
                df_high.to_excel(writer, sheet_name="高意向客户", index=False)
            
            # Sheet5: 未成单老客户回访
            if self.old_unpaid_list:
                df_unpaid = pd.DataFrame(self.old_unpaid_list)
                df_unpaid.to_excel(writer, sheet_name="未成单老客户回访", index=False)
            
            # Sheet6: 成单老客户回访
            if self.old_paid_list:
                df_paid = pd.DataFrame(self.old_paid_list)
                df_paid.to_excel(writer, sheet_name="成单老客户回访", index=False)
        
        print(f"[导出] 详细数据已保存到: {output_file}")

# ==========================================
# 主程序
# ==========================================
def main():
    print("=" * 60)
    print("[日报统计] 客户日报统计系统")
    print("=" * 60)
    
    # 输入统计日期
    date_input = input("\n请输入统计日期（单日如: YYYY-MM-DD, 范围如: 20260601-20260602，直接回车默认昨天）: ").strip()
    
    if not date_input:
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = start_date
        print(f"使用默认日期: {start_date} (昨天)")
    elif "-" in date_input and len(date_input.replace("-", "")) == 16:  # 匹配 20260601-20260602
        parts = date_input.split("-")
        try:
            start_date = datetime.strptime(parts[0], "%Y%m%d").strftime("%Y-%m-%d")
            end_date = datetime.strptime(parts[1], "%Y%m%d").strftime("%Y-%m-%d")
            if start_date > end_date:
                start_date, end_date = end_date, start_date
        except ValueError:
            print("[错误] 日期范围格式错误，请使用 YYYYMMDD-YYYYMMDD 格式")
            return
    else:
        # 验证单日期格式
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            start_date = date_input
            end_date = date_input
        except ValueError:
            print("[错误] 日期格式错误，请使用 YYYY-MM-DD 或 YYYYMMDD-YYYYMMDD 格式")
            return
    
    # 配置
    base_dir = r"D:\旭小姐阳台\客户聊天记录"
    
    # 读取通讯录
    contacts_map = {}
    contacts_file = None
    
    if os.path.exists(base_dir):
        for f in os.listdir(base_dir):
            if f.startswith("通讯录_") and f.endswith((".xlsx", ".xls")):
                contacts_file = os.path.join(base_dir, f)
                break
    
    if contacts_file and os.path.exists(contacts_file):
        try:
            df_contacts = pd.read_excel(contacts_file)
            for _, row in df_contacts.iterrows():
                wxid = str(row.get('微信ID', '')).strip()
                nickname = str(row.get('昵称', '')).strip()
                remark = str(row.get('备注', '')).strip()
                
                if wxid and wxid != 'nan':
                    contacts_map[wxid] = {'nickname': nickname, 'remark': remark}
            print(f"[成功] 加载通讯录，共 {len(contacts_map)} 个联系人")
        except Exception as e:
            print(f"[警告] 读取通讯录失败: {e}")
    else:
        print("[警告] 未找到通讯录文件，将使用聊天记录中的昵称")
    
    # 创建分析器并执行分析
    analyzer = DailyReportAnalyzer(base_dir, start_date, end_date)
    analyzer.analyze(contacts_map)
    
    # 打印报告（不显示明细）
    analyzer.print_report(show_details=False)
    
    print("\n[完成] 日报统计完成！")
    
    # 询问是否查看明细
    view_details = input("\n是否查看明细？(输入'是'查看，直接回车跳过): ").strip()
    
    if view_details in ['是', 'yes', 'y', 'Y', '1']:
        print("\n" + "=" * 60)
        print("[详细报告]")
        print("=" * 60)
        # 重新打印带明细的报告
        analyzer.print_report(show_details=True)
    
    # ==========================================
    # 月度目标统计
    # ==========================================
    print("\n" + "=" * 60)
    print("[月度目标统计]")
    print("=" * 60)
    
    # 输入统计周期（默认当前自然月）
    current_year = datetime.now().year
    current_month = datetime.now().month
    default_month = f"{current_year}-{current_month:02d}"
    
    month_input = input(f"\n请输入统计月份（格式：YYYY-MM，直接回车默认 {default_month}）: ").strip()
    
    if not month_input:
        target_year = current_year
        target_month = current_month
        print(f"使用默认月份: {default_month}")
    else:
        try:
            target_year, target_month = map(int, month_input.split('-'))
            if target_month < 1 or target_month > 12:
                print("[错误] 月份必须在1-12之间")
                return
        except ValueError:
            print("[错误] 月份格式错误，请使用 YYYY-MM 格式")
            return
    
    # 输入目标人数（默认400）
    target_input = input("\n请输入本月目标人数（直接回车默认 400）: ").strip()
    
    if not target_input:
        target_count = 400
        print("使用默认目标: 400人")
    else:
        try:
            target_count = int(target_input)
            if target_count <= 0:
                print("[错误] 目标人数必须大于0")
                return
        except ValueError:
            print("[错误] 请输入有效的数字")
            return
    
    # 计算统计周期的起止日期
    _, last_day = monthrange(target_year, target_month)
    period_start = f"{target_year}-{target_month:02d}-01"
    period_end = f"{target_year}-{target_month:02d}-{last_day:02d}"
    
    print(f"\n[分析中] 正在统计 {target_year}年{target_month}月 的数据...")
    
    # 创建月度分析器
    month_analyzer = DailyReportAnalyzer(base_dir, period_start, period_end)
    month_analyzer.analyze(contacts_map)
    
    # 计算总添加人数
    total_added = month_analyzer.new_contacts_count + month_analyzer.wechat_work_count
    remaining = target_count - total_added
    
    # 输出结果
    print("\n" + "=" * 60)
    print(f"[月度目标进度] {target_year}年{target_month}月")
    print("=" * 60)
    print(f"\n当前目标: {target_count}人，已经完成: {total_added}人")
    
    if remaining > 0:
        print(f"距离目标还差: {remaining}人")
        # 计算剩余天数
        today = datetime.now()
        if target_year == today.year and target_month == today.month:
            remaining_days = last_day - today.day + 1
            if remaining_days > 0:
                print(f"本月剩余天数: {remaining_days}天")
    elif remaining < 0:
        print(f"已超额完成: {abs(remaining)}人 🎉")
    else:
        print(f"恭喜！已完成本月目标！🎉")
    
    # 显示平台分布（按抖音主账号、抖音庭院、小红书三个维度）
    print(f"\n[平台分布]")
    print(f"  抖音主账号: {month_analyzer.platform_stats.get('抖音主账号', 0)}人")
    print(f"  抖音庭院: {month_analyzer.platform_stats.get('抖音庭院', 0)}人")
    print(f"  小红书: {month_analyzer.platform_stats.get('小红书', 0)}人")
    
    # 如果有其他平台，也显示
    other_count = month_analyzer.platform_stats.get('企业微信其他', 0)
    if other_count > 0:
        print(f"  其他平台: {other_count}人")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()