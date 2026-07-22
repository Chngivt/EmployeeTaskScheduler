from app import create_app

# Khởi tạo ứng dụng
app = create_app()

if __name__ == '__main__':
    # Chạy server ở chế độ debug để dễ dàng tìm lỗi
    app.run(debug=True)