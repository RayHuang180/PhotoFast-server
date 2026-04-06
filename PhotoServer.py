import os
import socket
import sys
from flask import Flask, request, jsonify
from pathlib import Path
from werkzeug.utils import secure_filename

# 💡 新增：匯入 mDNS 需要的套件
from zeroconf import ServiceInfo, Zeroconf

app = Flask(__name__)

# BASE_DIR = Path(__file__).parent
# 修改後 (確保在 .exe 環境也能抓到正確位置)
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent


# 【修改】資料夾名稱改為通用名稱
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'received_files')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 💡 新增：自動取得這台 Windows 電腦目前的區網 IP
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 連線到一個外部 IP 來強制系統分配區網 IP
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# 💡 新增：啟動 Bonjour / mDNS 廣播
def start_mdns_broadcast(port):
    ip = get_local_ip()
    print(f"📡 啟動 mDNS 廣播... 告訴手機我的 IP 是 {ip}:{port}")
    
    # 注意：這裡的 "_photofast._tcp.local." 必須跟 iOS 端設定完全一樣
    info = ServiceInfo(
        "_photofast._tcp.local.",
        "PhotoFast Server._photofast._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=port,
        server="photofast.local."
    )
    
    zc = Zeroconf()
    zc.register_service(info)
    return zc

@app.route('/upload', methods=['POST']) # type: ignore
def upload_file():
    # 【修改】欄位名稱改為 'file'
    if 'file' not in request.files:
        return jsonify({'error': '請求中沒有找到檔案'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': '沒有選擇任何檔案'}), 400

    # 【修改】移除副檔名限制，接收所有檔案
    if file:
        safe_filename = secure_filename(file.filename) # type: ignore
        save_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        file.save(save_path)
        print(f"✅ 成功接收並儲存檔案：{safe_filename}")
        return jsonify({'message': '檔案上傳成功！', 'filename': safe_filename}), 200

if __name__ == '__main__':
    PORT = 5000
    # 💡 啟動伺服器前，先開始廣播自己
    zeroconf_instance = start_mdns_broadcast(PORT)
    
    try:
        # 💡 重要修改：加上 use_reloader=False。
        # 因為 debug=True 預設會啟動兩次程式來監聽檔案變更，這會導致 mDNS 註冊發生命名衝突
        app.run(host='0.0.0.0', port=PORT, debug=True, use_reloader=False)
    finally:
        # 當你在終端機按下 Ctrl+C 關閉伺服器時，優雅地停止廣播
        zeroconf_instance.unregister_all_services()
        zeroconf_instance.close()
        print("🛑 伺服器與廣播已成功關閉")