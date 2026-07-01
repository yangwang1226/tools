import os
import qrcode
from PIL import Image

def generate_qr_with_logo(url, logo_path="logo.png", output_path="qrcode_output.png"):
    # 1. 配置二维码参数
    # 使用最高容错率 (ERROR_CORRECT_H)，因为中间要放 logo，需要保证边缘部分仍能被识别
    qr = qrcode.QRCode(
        version=5,  # 基础大小，5表示 37x37 模块
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10, # 每个二维码模块的像素大小
        border=4,    # 边框的格子数（标准是4）
    )
    
    # 添加数据
    qr.add_data(url)
    qr.make(fit=True)

    # 生成基础二维码图片，并转换为 RGB 模式（为了方便贴图）
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # 2. 处理 Logo
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        
        # 计算 logo 的大小：通常 logo 的边长不超过二维码边长的 1/4 到 1/3
        img_w, img_h = img.size
        factor = 4
        size_w = int(img_w / factor)
        size_h = int(img_h / factor)
        
        # 缩放 logo
        logo = logo.resize((size_w, size_h), Image.Resampling.LANCZOS)
        
        # 考虑到某些 logo 可能是带透明通道的 PNG (RGBA)，我们用它自身的 alpha 作为遮罩
        mask = logo if logo.mode == 'RGBA' else None

        # 计算 logo 放置的坐标 (居中)
        w = int((img_w - size_w) / 2)
        h = int((img_h - size_h) / 2)
        
        # 将 logo 贴到二维码上
        img.paste(logo, (w, h), mask)
        print(f"[成功] Logo '{logo_path}' 已成功融合到二维码中。")
    else:
        print(f"[警告] 未找到 logo 文件 '{logo_path}'，将生成不带 logo 的普通二维码。")

    # 3. 保存最终图片
    # 将 RGBA 转回 RGB 保存为 PNG 或 JPG
    final_img = img.convert("RGB")
    final_img.save(output_path)
    print(f"[成功] 二维码已生成并保存为: {output_path}")

if __name__ == "__main__":
    print("="*40)
    print("   永久链接二维码生成器 (带Logo版)   ")
    print("="*40)
    
    # 提示输入链接
    input_url = input("请输入你想生成二维码的链接: ").strip()
    
    if not input_url:
        print("[错误] 链接不能为空！")
    else:
        # 生成带logo的二维码
        generate_qr_with_logo(input_url, logo_path="logo.png", output_path="qrcode_output.png")