import os

# Lấy đường dẫn thư mục hiện tại của dự án
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Key bảo mật cho Form và Session
    SECRET_KEY = 'chuoi-bao-mat-kho-doan-nhat'
    
    # Cấu hình đường dẫn cho SQLite (Lưu trong thư mục instance)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')
    
    # Tắt tính năng theo dõi thay đổi để tiết kiệm bộ nhớ
    SQLALCHEMY_TRACK_MODIFICATIONS = False