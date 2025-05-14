from flask import Flask, request, send_file, render_template_string
import os

app = Flask(__name__)

# Tạo thư mục result nếu chưa tồn tại
RESULT_DIR = 'result'
if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)

# Hàm mã hóa/giải mã XOR
def xor_cipher(data, key):
    key = key.encode() if isinstance(key, str) else key
    data = data.encode() if isinstance(data, str) else data
    key = key * (len(data) // len(key) + 1)
    return bytes(a ^ b for a, b in zip(data, key[:len(data)]))

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
            # Kiểm tra định dạng file
            allowed_extensions = {'.txt', '.png', '.jpg', '.jpeg'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                message = "Chỉ hỗ trợ file .txt, .png, .jpg, .jpeg!"
            else:
                content = file.read()
                result = xor_cipher(content, key)
                output_filename = os.path.join(RESULT_DIR, 'output_' + file.filename)
                with open(output_filename, 'wb') as f:
                    f.write(result)
                result_file = output_filename
                if action == "mã hóa":
                    message = f"Đã mã hóa thành công!. Tải file kết quả bên dưới."
                else:
                    message = f"Đã giải mã thành công!"
        else:
            message = "Vui lòng chọn file và nhập khóa!"
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mã hóa & Giải mã XOR</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
            body {
                background: linear-gradient(135deg, #4c51bf, #a3bffa);
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
            <h1 class="title">Mã hóa & Giải mã XOR</h1>
            <p class="note">Hỗ trợ file: .txt, .png, .jpg, .jpeg</p>
            <form method="post" enctype="multipart/form-data" class="space-y-4">
                <div class="input-group">
                    <label for="file" class="block text-sm font-medium text-gray-700">Chọn file</label>
                    <input type="file" name="file" id="file" accept=".txt,.png,.jpg,.jpeg" required class="mt-1">
                </div>
                <div class="input-group">
                    <label for="key" class="block text-sm font-medium text-gray-700">Nhập khóa</label>
                    <input type="text" name="key" id="key" placeholder="Enter KeyCode" required class="mt-1">
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