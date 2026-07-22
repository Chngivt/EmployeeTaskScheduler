import os
from flask import Flask, render_template # <--- Thêm render_template ở đây
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

    # --- ĐĂNG KÝ CÁC BLUEPRINT TẠI ĐÂY ---
    from app.routes.employee import employee_bp
    app.register_blueprint(employee_bp)
    
    from app.routes.task import task_bp
    app.register_blueprint(task_bp)

    from app.routes.schedule import schedule_bp
    app.register_blueprint(schedule_bp)

    # --- ROUTE TRANG CHỦ (DASHBOARD) ---
    @app.route('/')
    def dashboard():
        # Đếm tổng số lượng dữ liệu
        total_emp = Employee.query.count()
        total_task = Task.query.count()
        total_schedule = Schedule.query.count()
        
        # Lấy toàn bộ lịch phân công để đổ ra bảng tuần
        schedules_list = Schedule.query.all()
        
        return render_template('dashboard.html', 
                               total_emp=total_emp, 
                               total_task=total_task, 
                               total_schedule=total_schedule,
                               schedules=schedules_list)

    return app