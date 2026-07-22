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

    os.makedirs(app.instance_path, exist_ok=True)

    from app.models.employee import Employee
    from app.models.task import Task
    from app.models.schedule import Schedule

    with app.app_context():
        db.create_all()

    # --- ĐĂNG KÝ CÁC BLUEPRINT TẠI ĐÂY (Chỉ đăng ký mỗi cái 1 lần) ---
    from app.routes.employee import employee_bp
    app.register_blueprint(employee_bp)
    
    from app.routes.task import task_bp
    app.register_blueprint(task_bp)

    from app.routes.schedule import schedule_bp
    app.register_blueprint(schedule_bp)

    @app.route('/')
    def dashboard():
        return "<h1>Hệ thống Employee Task Scheduler đã chạy thành công!</h1><a href='/employee'>Nhân viên</a> | <a href='/task'>Công việc</a> | <a href='/schedule'>Phân công</a>"

    return app