"""
绿植花卉知识库提取工具
从微信聊天记录JSON文件中提取问答对，生成Cherry Studio友好的Markdown知识库
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
import re
from datetime import datetime

class KnowledgeExtractor:
    def __init__(self, json_folder: str, output_folder: str = "knowledge_base"):
        self.json_folder = Path(json_folder)
        self.output_folder = Path(output_folder)
        self.agent_name = "旭小姐的阳台花园（本人号）"
        
        # 统计信息
        self.stats = {
            'total_files': 0,
            'total_conversations': 0,
            'total_messages': 0,
            'total_qa_pairs': 0,
            'products_found': set(),
            'categories': defaultdict(int)
        }
        
        # 分类关键词
        self.category_keywords = {
            '产品知识': ['花箱', '花盆', '规格', '尺寸', '材质', '特点', '设计', '容器', '种植', '介绍一下'],
            '产品价格': ['多少钱', '价格', '费用', '优惠', '便宜', '贵', '成本'],
            '销售话术': ['小贵', '考虑', '不买', '再看看', '贵了'],
            '物流配送': ['包邮', '快递', '物流', '发货', '配送', '多久到', '运费'],
            '售后服务': ['退货', '换货', '质量问题', '坏了', '售后', '保修']
        }
        
        # 存储提取的数据
        self.qa_pairs = defaultdict(list)
        self.products = defaultdict(dict)
        
    def read_json_file(self, filepath: Path) -> Dict:
        """读取单个JSON文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            try:
                print(f"[ERROR] 读取文件失败 {filepath.name}: {e}")
            except UnicodeEncodeError:
                print(f"[ERROR] 读取文件失败: {e}")
            return None
    
    def is_question(self, content: str) -> bool:
        """判断是否为问题"""
        if not content:
            return False
        question_patterns = [
            r'.*[？?]$',  # 以问号结尾
            r'^(什么|怎么|如何|为什么|多少|哪里|能不能|可以|有没有)',  # 疑问词开头
            r'.*(吗|呢|啊)$',  # 疑问语气词结尾
            r'.*(介绍|说明|解释)',  # 询问说明
        ]
        return any(re.search(pattern, content) for pattern in question_patterns)
    
    def classify_content(self, content: str) -> List[str]:
        """根据内容分类"""
        categories = []
        for category, keywords in self.category_keywords.items():
            if any(keyword in content for keyword in keywords):
                categories.append(category)
        
        # 如果没有匹配到任何分类，默认为产品知识
        if not categories:
            categories.append('产品知识')
        
        return categories
    
    def extract_product_info(self, content: str) -> Dict:
        """提取产品信息（规格、价格等）"""
        info = {}
        
        # 提取尺寸信息
        size_pattern = r'(\d+)\s*[cC][mM]?'
        sizes = re.findall(size_pattern, content)
        if sizes:
            info['尺寸提及'] = sizes
        
        # 提取价格信息
        price_pattern = r'(\d+)\s*元'
        prices = re.findall(price_pattern, content)
        if prices:
            info['价格'] = prices[0] + '元'
        
        # 提取特点关键词
        features = []
        feature_keywords = ['内胆', '滑轮', '树脂', '包邮', '厚实', '耐用', '室内', '室外']
        for keyword in feature_keywords:
            if keyword in content:
                features.append(keyword)
        if features:
            info['特点'] = features
        
        return info
    
    def extract_qa_pairs(self, messages: List[Dict]) -> List[Dict]:
        """从消息列表中提取问答对"""
        qa_pairs = []
        
        i = 0
        while i < len(messages):
            msg = messages[i]
            
            # 跳过系统消息
            if msg.get('type') == '系统消息' or msg.get('localType') == 10000:
                i += 1
                continue
            
            # 跳过非文本消息
            if msg.get('type') != '文本消息':
                i += 1
                continue
            
            content = msg.get('content', '').strip()
            sender = msg.get('senderDisplayName', '')
            
            # 如果是客户的问题
            if sender != self.agent_name and self.is_question(content):
                question = content
                question_time = msg.get('formattedTime', '')
                
                # 查找下一条博主的回复
                answer = None
                answer_time = None
                for j in range(i + 1, min(i + 5, len(messages))):  # 向后查找最多5条消息
                    next_msg = messages[j]
                    if next_msg.get('senderDisplayName') == self.agent_name:
                        if next_msg.get('type') == '文本消息':
                            answer = next_msg.get('content', '').strip()
                            answer_time = next_msg.get('formattedTime', '')
                            break
                
                if answer:
                    # 分类
                    categories = self.classify_content(question + ' ' + answer)
                    
                    # 提取产品信息
                    product_info = self.extract_product_info(answer)
                    
                    qa_pair = {
                        'question': question,
                        'answer': answer,
                        'categories': categories,
                        'time': question_time,
                        'product_info': product_info
                    }
                    
                    qa_pairs.append(qa_pair)
                    self.stats['total_qa_pairs'] += 1
            
            i += 1
        
        return qa_pairs
    
    def process_all_files(self):
        """处理所有JSON文件"""
        print("[INFO] 开始处理JSON文件...")
        
        json_files = list(self.json_folder.glob('*.json'))
        self.stats['total_files'] = len(json_files)
        
        print(f"[INFO] 找到 {self.stats['total_files']} 个JSON文件")
        
        for idx, filepath in enumerate(json_files, 1):
            try:
                print(f"[{idx}/{self.stats['total_files']}] 处理中: {filepath.name}")
            except UnicodeEncodeError:
                print(f"[{idx}/{self.stats['total_files']}] 处理中: [文件名包含特殊字符]")
            
            data = self.read_json_file(filepath)
            if not data:
                continue
            
            self.stats['total_conversations'] += 1
            
            messages = data.get('messages', [])
            self.stats['total_messages'] += len(messages)
            
            # 提取问答对
            qa_pairs = self.extract_qa_pairs(messages)
            
            # 按分类存储
            for qa in qa_pairs:
                for category in qa['categories']:
                    self.qa_pairs[category].append(qa)
                    self.stats['categories'][category] += 1
        
        print(f"\n[SUCCESS] 处理完成！")
        print(f"   - 处理文件数: {self.stats['total_files']}")
        print(f"   - 对话总数: {self.stats['total_conversations']}")
        print(f"   - 消息总数: {self.stats['total_messages']}")
        print(f"   - 提取问答对: {self.stats['total_qa_pairs']}")
        print(f"\n[INFO] 分类统计:")
        for category, count in self.stats['categories'].items():
            print(f"   - {category}: {count} 条")
    
    def generate_markdown(self):
        """生成Markdown文件"""
        print("\n[INFO] 开始生成Markdown文件...")
        
        # 创建输出目录
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # 为每个分类生成文件
        category_folders = {
            '产品知识': '01_产品知识',
            '产品价格': '02_产品价格',
            '销售话术': '03_销售话术',
            '物流配送': '04_物流配送',
            '售后服务': '05_售后服务'
        }
        
        for category, folder_name in category_folders.items():
            if category not in self.qa_pairs or not self.qa_pairs[category]:
                continue
            
            # 创建分类文件夹
            category_folder = self.output_folder / folder_name
            category_folder.mkdir(exist_ok=True)
            
            # 生成Markdown内容
            md_content = self.generate_category_markdown(category, self.qa_pairs[category])
            
            # 保存文件
            filename = f"{category}.md"
            filepath = category_folder / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"[OK] 生成: {folder_name}/{filename} ({len(self.qa_pairs[category])} 条问答)")
        
        # 生成汇总文档
        self.generate_summary_markdown()
        
        # 生成统计报告
        self.generate_stats_report()
        
        print(f"\n[SUCCESS] 所有Markdown文件已生成到: {self.output_folder}")
    
    def generate_category_markdown(self, category: str, qa_list: List[Dict]) -> str:
        """生成分类Markdown内容"""
        md = f"# {category}\n\n"
        md += f"> 本文档包含 {len(qa_list)} 条相关问答\n"
        md += f"> 数据来源：微信聊天记录提取\n"
        md += f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md += "---\n\n"
        
        # 去重和分组
        unique_qa = self.deduplicate_qa(qa_list)
        
        # 按问题类型分组
        grouped = self.group_qa_by_topic(unique_qa)
        
        for topic, qas in grouped.items():
            md += f"## {topic}\n\n"
            
            for idx, qa in enumerate(qas, 1):
                question = qa['question'].replace('\n', ' ')
                answer = qa['answer']
                
                md += f"### Q{idx}: {question}\n\n"
                md += f"**回答：**\n\n{answer}\n\n"
                
                # 如果有产品信息，添加备注
                if qa.get('product_info'):
                    info = qa['product_info']
                    md += "**关键信息：**\n"
                    if '价格' in info:
                        md += f"- 价格：{info['价格']}\n"
                    if '特点' in info:
                        md += f"- 特点：{', '.join(info['特点'])}\n"
                    md += "\n"
                
                md += "---\n\n"
        
        md += f"\n*文档版本：v1.0*  \n"
        md += f"*最后更新：{datetime.now().strftime('%Y-%m-%d')}*\n"
        
        return md
    
    def deduplicate_qa(self, qa_list: List[Dict]) -> List[Dict]:
        """去重相似问答"""
        unique = []
        seen_questions = set()
        
        for qa in qa_list:
            # 简单去重：基于问题文本
            q_normalized = re.sub(r'\s+', '', qa['question'].lower())
            if q_normalized not in seen_questions:
                seen_questions.add(q_normalized)
                unique.append(qa)
        
        return unique
    
    def group_qa_by_topic(self, qa_list: List[Dict]) -> Dict[str, List[Dict]]:
        """按话题分组"""
        groups = defaultdict(list)
        
        for qa in qa_list:
            question = qa['question']
            
            # 简单分组逻辑
            if any(kw in question for kw in ['规格', '尺寸', '大小', '介绍']):
                topic = '产品规格介绍'
            elif any(kw in question for kw in ['价格', '多少钱', '费用']):
                topic = '价格相关'
            elif any(kw in question for kw in ['材质', '材料', '什么做的']):
                topic = '材质相关'
            elif any(kw in question for kw in ['包邮', '快递', '配送', '发货']):
                topic = '物流配送'
            elif any(kw in question for kw in ['耐用', '质量', '能用多久']):
                topic = '产品质量'
            elif any(kw in question for kw in ['贵', '便宜', '优惠']):
                topic = '价格异议'
            else:
                topic = '其他问题'
            
            groups[topic].append(qa)
        
        return dict(groups)
    
    def generate_summary_markdown(self):
        """生成快速查询汇总文档"""
        summary_folder = self.output_folder / '00_快速查询'
        summary_folder.mkdir(exist_ok=True)
        
        md = "# 绿植花卉销售 - 常见问答汇总\n\n"
        md += f"> 本文档汇总了最常见的客户问题和标准答案\n"
        md += f"> 问答总数：{self.stats['total_qa_pairs']} 条\n"
        md += f"> 数据来源：{self.stats['total_files']} 个客户对话\n"
        md += f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md += "---\n\n"
        
        # 从每个分类中选取代表性问答
        for category in ['产品知识', '产品价格', '物流配送', '销售话术']:
            if category in self.qa_pairs and self.qa_pairs[category]:
                md += f"## {category}\n\n"
                
                # 取前5个问答
                for qa in self.qa_pairs[category][:5]:
                    question = qa['question'].replace('\n', ' ')
                    answer = qa['answer'].replace('\n', ' ')
                    
                    md += f"**Q: {question}**  \n"
                    md += f"A: {answer}\n\n"
        
        md += "---\n\n"
        md += f"*文档版本：v1.0*  \n"
        md += f"*最后更新：{datetime.now().strftime('%Y-%m-%d')}*\n"
        
        filepath = summary_folder / '常见问答汇总.md'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"[OK] 生成: 00_快速查询/常见问答汇总.md")
    
    def generate_stats_report(self):
        """生成统计报告"""
        report = "# 知识库提取统计报告\n\n"
        report += f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += "## 数据概览\n\n"
        report += f"- 处理JSON文件数：{self.stats['total_files']}\n"
        report += f"- 客户对话总数：{self.stats['total_conversations']}\n"
        report += f"- 消息总数：{self.stats['total_messages']}\n"
        report += f"- 提取问答对：{self.stats['total_qa_pairs']}\n\n"
        report += "## 分类统计\n\n"
        
        for category, count in sorted(self.stats['categories'].items(), key=lambda x: x[1], reverse=True):
            report += f"- **{category}**：{count} 条\n"
        
        report += "\n## 文件清单\n\n"
        
        for folder in self.output_folder.iterdir():
            if folder.is_dir():
                report += f"### {folder.name}\n\n"
                for file in folder.glob('*.md'):
                    report += f"- {file.name}\n"
                report += "\n"
        
        filepath = self.output_folder / '统计报告.md'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"[OK] 生成: 统计报告.md")


def main():
    """主函数"""
    print("=" * 60)
    print("     绿植花卉知识库提取工具 v1.0")
    print("=" * 60)
    print()
    
    # 配置路径
    json_folder = r"C:\Users\Administrator\Documents\chat\绿植花卉知识库"
    output_folder = "knowledge_base"
    
    # 创建提取器实例
    extractor = KnowledgeExtractor(json_folder, output_folder)
    
    # 处理所有文件
    extractor.process_all_files()
    
    # 生成Markdown文件
    extractor.generate_markdown()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] 知识库生成完成！")
    print(f"[INFO] 输出目录: {output_folder}")
    print("=" * 60)


if __name__ == "__main__":
    main()