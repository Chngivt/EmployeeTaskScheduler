import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail  
from config import Config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()  

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)  

    os.makedirs(app.instance_path, exist_ok=True)

    from app.models.employee import Employee
    from app.models.task import Task
    from app.models.schedule import Schedule

    with app.app_context():
        db.create_all()

        # --- TỰ ĐỘNG TẠO TÀI KHOẢN ADMIN MẶC ĐỊNH ---
        admin_email = "caohoangviet738@gmail.com"
        existing_admin = Employee.query.filter(
            (Employee.email == admin_email) | (Employee.code == "AD001")
        ).first()
        if not existing_admin:
            admin_emp = Employee(
                code="AD001",
                fullname="Quản Trị Viên",
                email=admin_email,
                phone="0909123456",
                department="Quản trị",
                position="Admin",
                role="admin"
            )
            admin_emp.set_password("admin123")
            db.session.add(admin_emp)
            db.session.commit()
            print("--> Đã tự động tạo tài khoản Admin mặc định thành công!")

    # --- ĐĂNG KÝ CÁC BLUEPRINT ---
    from app.routes.employee import employee_bp
    app.register_blueprint(employee_bp)
    
    from app.routes.task import task_bp
    app.register_blueprint(task_bp)

    from app.routes.schedule import schedule_bp
    app.register_blueprint(schedule_bp)

    # Đăng ký Auth Blueprint
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # --- ROUTE TRANG CHỦ (DASHBOARD) ---
    @app.route('/')
    def dashboard():
        from datetime import datetime, timedelta
        
        total_emp = Employee.query.count()
        total_task = Task.query.count()
        total_schedule = Schedule.query.count()
        
        employees = Employee.query.all()
        schedules = Schedule.query.all()
        
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        week_dates = [start_of_week + timedelta(days=i) for i in range(6)]
        
        schedule_dict = {}
        for s in schedules:
            schedule_dict[(s.employee_id, s.date, s.shift)] = s.task.task_name
            
        return render_template('dashboard.html', 
                               total_emp=total_emp, 
                               total_task=total_task, 
                               total_schedule=total_schedule,
                               employees=employees,
                               week_dates=week_dates,
                               schedule_dict=schedule_dict)

    return app