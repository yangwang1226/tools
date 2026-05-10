import os
import re

def remove_duplicate_files(directory):
    if not os.path.exists(directory):
        print(f"错误: 找不到文件夹 '{directory}'")
        return

    # 用于将文件分组的字典，格式为 { "前缀": [(时间戳数字, "完整文件路径"), ...] }
    file_groups = {}
    
    # 正则表达式：匹配 "任意内容_数字.json"
    pattern = re.compile(r'^(.*)_(\d+)\.json$')

    print(f"正在扫描文件夹: {directory} ...")
    
    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            prefix = match.group(1)
            timestamp = int(match.group(2))
            filepath = os.path.join(directory, filename)
            
            if prefix not in file_groups:
                file_groups[prefix] = []
            file_groups[prefix].append((timestamp, filepath))

    deleted_count = 0
    
    # 开始处理每一个分组
    for prefix, files in file_groups.items():
        if len(files) > 1:
            # 按照数字（时间戳）从小到大排序
            files.sort(key=lambda x: x[0])
            
            # files[0] 是数字最小的，保留它
            # files[1:] 都是数字较大的，需要删除
            files_to_delete = files[1:]
            
            for ts, filepath in files_to_delete:
                try:
                    os.remove(filepath)
                    print(f"已删除重复文件 (数字较大): {os.path.basename(filepath)}")
                    deleted_count += 1
                except Exception as e:
                    print(f"删除失败 {filepath}: {e}")

    print(f"\n✅ 清理完成！共检测并删除了 {deleted_count} 个重复文件。")

if __name__ == "__main__":
    # 目标文件夹路径
    target_dir = "20260509"
    remove_duplicate_files(target_dir)