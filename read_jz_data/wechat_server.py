from flask import Flask, request, abort
from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException

app = Flask(__name__)

# ================= 配置区 =================
CORP_ID = "wwf91b2ae32f1286c9" # 您的企业ID

# TODO: 等下在企业微信管理后台点击“随机获取”后，把这两个值粘贴到这里！
TOKEN = "PLEASE_REPLACE_ME_WITH_YOUR_TOKEN"
ENCODING_AES_KEY = "PLEASE_REPLACE_ME_WITH_YOUR_ENCODING_AES_KEY"
# ==========================================

@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    
    # 初始化加解密对象
    try:
        crypto = WeChatCrypto(TOKEN, ENCODING_AES_KEY, CORP_ID)
    except Exception as e:
        print("初始化加解密失败，请检查配置:", e)
        return "error", 500

    if request.method == 'GET':
        # 1. 用于企业微信后台配置 URL 时的握手验证
        echostr = request.args.get('echostr', '')
        try:
            # check_signature 会校验签名并自动解密返回真正的 echostr 原文
            decrypted_echostr = crypto.check_signature(signature, timestamp, nonce, echostr)
            print("✅ 验证成功！解密字符串为:", decrypted_echostr)
            return decrypted_echostr
        except InvalidSignatureException:
            print("❌ 签名验证失败！")
            abort(403)
            
    elif request.method == 'POST':
        # 2. 用于接收以后用户点击“交互卡片”的回调事件
        try:
            decrypted_msg = crypto.decrypt_message(
                request.data,
                signature,
                timestamp,
                nonce
            )
            print("收到卡片点击回调事件:\\n", decrypted_msg.decode('utf-8'))
            # 企业微信要求接收到消息后返回 success 或特定的 XML 响应
            return "success"
        except InvalidSignatureException:
            abort(403)

if __name__ == '__main__':
    print("🚀 正在启动企业微信回调服务器，端口: 5000...")
    app.run(host='0.0.0.0', port=5000)