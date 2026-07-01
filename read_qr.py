import os
from PIL import Image
try:
    import cv2
except ImportError:
    print("[错误] 未安装 opencv-python 库。请先运行: pip install opencv-python")
    exit(1)

def extract_link_from_qr(image_path="qrcode_output.png"):
    if not os.path.exists(image_path):
        print(f"[错误] 找不到图片文件: {image_path}")
        return None
    
    try:
        # 使用 OpenCV 读取图片
        img = cv2.imread(image_path)
        if img is None:
            print(f"[错误] 无法读取图片，请检查文件是否损坏: {image_path}")
            return None

        # 初始化 OpenCV 的二维码检测器
        detector = cv2.QRCodeDetector()
        
        # 检测并解码
        data, bbox, _ = detector.detectAndDecode(img)
        
        if not data:
            print("[提示] 未能从图片中识别到二维码。可能是图片不清晰、Logo过大遮挡了定位点，或图片中确实没有二维码。")
            return None
        
        # 打印提取内容
        print("\n--- 提取结果 ---")
        print(f"内容: {data}")
        print("----------------\n")
            
    except Exception as e:
        print(f"[错误] 读取或解析二维码时发生异常: {e}")
        return None

if __name__ == "__main__":
    print("="*40)
    print("       二维码内容提取工具       ")
    print("="*40)
    
    # 提示输入图片路径
    img_path = "6540c9f3918dd7f92fb072cbb2d172a1.png"
    
    # 如果用户直接按回车，就使用默认路径
    if not img_path:
        img_path = "qrcode_output.png"
        
    extract_link_from_qr(img_path)