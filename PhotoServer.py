import os
from flask import Flask, request, jsonify
from pathlib import Path


app = Flask(__name__)
filepath = Path(__file__).parent

# 設定用來存放接收照片的資料夾
UPLOAD_FOLDER = os.path.join(filepath,'received_photos')

# 如果資料夾不存在，就自動建立一個
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST']) # type: ignore
def upload_file():
    # 1. 檢查請求中是否包含名為 'photo' 的檔案資料
    if 'photo' not in request.files:
        return jsonify({'error': '請求中沒有找到照片'}), 400

    file = request.files['photo']

    # 2. 檢查檔案名稱是否為空（代表使用者沒有選擇檔案）
    if file.filename == '':
        return jsonify({'error': '沒有選擇任何檔案'}), 400

    # 3. 儲存檔案
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename) # type: ignore
        file.save(filepath)
        print(f"成功接收並儲存照片：{file.filename}")
        return jsonify({'message': '照片上傳成功！', 'filename': file.filename}), 200

if __name__ == '__main__':
    # host='0.0.0.0' 非常重要，這允許同一個 Wi-Fi 網路下的其他裝置連線到這台電腦
    # port=5000 是伺服器監聽的通訊埠
    app.run(host='0.0.0.0', port=5000, debug=True)