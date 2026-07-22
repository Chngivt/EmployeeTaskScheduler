import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Đảm bảo thư mục 'instance' tồn tại để chứa file CSDL
    os.makedirs(app.instance_path, exist_ok=True)

    # Import các models vào hệ thống
    from app.models.employee import Employee
    from app.models.task import Task
    from app.models.schedule import Schedule

    # Tự động tạo file database.db nếu nó chưa tồn tại
    with app.app_context():
        db.create_all()

    @app.route('/')
    def dashboard():
        return "<h1>Hệ thống Employee Task Scheduler đã chạy thành công!</h1>"

    return app