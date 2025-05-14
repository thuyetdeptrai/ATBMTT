from flask import Flask, request, send_file, render_template_string
import os
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

app = Flask(__name__)

# Tạo thư mục result nếu chưa tồn tại
RESULT_DIR = 'result'
if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)

# Hàm mã hóa DES
def des_encrypt(data, key):
    # Đảm bảo khóa dài 8 byte (64-bit), cắt hoặc padding nếu cần
    key = key.encode()[:8].ljust(8, b'\0')
    cipher = DES.new(key, DES.MODE_ECB)
    padded_data = pad(data, DES.block_size)
    return cipher.encrypt(padded_data)

# Hàm giải mã DES
def des_decrypt(data, key):
    # Đảm bảo khóa dài 8 byte
    key = key.encode()[:8].ljust(8, b'\0')
    cipher = DES.new(key, DES.MODE_ECB)
    decrypted_data = cipher.decrypt(data)
    return unpad(decrypted_data, DES.block_size)

# Trang chủ với giao diện
@app.route('/', methods=['GET', 'POST'])
def index():
    result_file = None
    message = ""
    if request.method == 'POST':
        file = request.files.get('file')
        key = request.form.get('key')
        action = request.form.get('action')
        
        if file and key:
            # Kiểm tra độ dài khóa (DES yêu cầu 8 byte)
            if len(key.encode()) > 8:
                message = "Khóa không được vượt quá 8 ký tự!"
            else:
                # Kiểm tra định dạng file
                allowed_extensions = {'.txt', '.png', '.jpg', '.jpeg'}
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext not in allowed_extensions:
                    message = "Chỉ hỗ trợ file .txt, .png, .jpg, .jpeg!"
                else:
                    content = file.read()
                    try:
                        if action == "mã hóa":
                            result = des_encrypt(content, key)
                            message = f"Đã mã hóa thành công!. Tải file kết quả bên dưới."
                        else:
                            result = des_decrypt(content, key)
                            message = f"Đã giải mã thành công!"
                        output_filename = os.path.join(RESULT_DIR, 'output_' + file.filename)
                        with open(output_filename, 'wb') as f:
                            f.write(result)
                        result_file = output_filename
                    except Exception as e:
                        message = f"Lỗi: {str(e)} (Kiểm tra khóa hoặc file đầu vào!)"
        else:
            message = "Vui lòng chọn file và nhập khóa!"
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mã hóa & Giải mã DES</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            body {
                background: url('data:image/jpeg;base64,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') no-repeat center center fixed;
                background-size: cover;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
                font-family: 'Poppins', sans-serif;
            }
            .card {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 1.5rem;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                padding: 2rem;
                max-width: 500px;
                width: 90%;
                animation: fadeIn 0.5s ease-in-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: scale(0.9); }
                to { opacity: 1; transform: scale(1); }
            }
            .title {
                color: #2d3748;
                font-size: 2rem;
                font-weight: 700;
                text-align: center;
                margin-bottom: 1.5rem;
            }
            .note {
                color: #718096;
                font-size: 0.9rem;
                text-align: center;
                margin-bottom: 1.5rem;
            }
            .input-group {
                margin-bottom: 1rem;
            }
            input[type="file"], input[type="text"] {
                width: 100%;
                padding: 0.75rem;
                border: 2px solid #e2e8f0;
                border-radius: 0.5rem;
                font-size: 1rem;
                transition: border-color 0.3s, box-shadow 0.3s;
            }
            input[type="file"]:hover, input[type="text"]:hover {
                border-color: #4c51bf;
                box-shadow: 0 0 10px rgba(76, 81, 191, 0.2);
            }
            input[type="file"]:focus, input[type="text"]:focus {
                outline: none;
                border-color: #a3bffa;
                box-shadow: 0 0 15px rgba(163, 191, 250, 0.4);
            }
            .btn {
                padding: 0.75rem 1.5rem;
                border-radius: 0.5rem;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .btn-encrypt {
                background: linear-gradient(45deg, #4c51bf, #6b46c1);
                color: white;
            }
            .btn-decrypt {
                background: linear-gradient(45deg, #38b2ac, #319795);
                color: white;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            .btn:active {
                transform: translateY(0);
            }
            .download-btn {
                background: linear-gradient(45deg, #48bb78, #38a169);
                color: white;
                margin-top: 1rem;
            }
            .message {
                color: #e53e3e;
                font-weight: 500;
                text-align: center;
                margin-top: 1rem;
                animation: fadeIn 0.5s ease-in-out;
            }
            .icon {
                margin-right: 0.5rem;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1 class="title">Mã hóa & Giải mã DES</h1>
            <p class="note">Hỗ trợ file: .txt, .png, .jpg, .jpeg</p>
            <form method="post" enctype="multipart/form-data" class="space-y-4">
                <div class="input-group">
                    <label for="file" class="block text-sm font-medium text-gray-700">Chọn file</label>
                    <input type="file" name="file" id="file" accept=".txt,.png,.jpg,.jpeg" required class="mt-1">
                </div>
                <div class="input-group">
                    <label for="key" class="block text-sm font-medium text-gray-700">Nhập khóa (tối đa 8 ký tự)</label>
                    <input type="text" name="key" id="key" placeholder="Enter KeyCode (max 8 chars)" required class="mt-1">
                </div>
                <div class="flex justify-between">
                    <button type="submit" name="action" value="mã hóa" class="btn btn-encrypt">
                        <i class="fas fa-lock icon"></i> Mã hóa
                    </button>
                    <button type="submit" name="action" value="giải mã" class="btn btn-decrypt">
                        <i class="fas fa-unlock icon"></i> Giải mã
                    </button>
                </div>
            </form>
            {% if message %}
                <p class="message">{{ message }}</p>
            {% endif %}
            {% if result_file %}
                <a href="/download/{{ result_file }}" class="block">
                    <button class="btn download-btn w-full">
                        <i class="fas fa-download icon"></i> Tải file kết quả
                    </button>
                </a>
            {% endif %}
        </div>
    </body>
    </html>
    ''', result_file=result_file, message=message)

# Tải file kết quả
@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)