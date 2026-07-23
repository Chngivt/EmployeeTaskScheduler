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

    from app.routes.export import export_bp
    app.register_blueprint(export_bp)

    # --- ROUTE TRANG CHỦ (DASHBOARD) ---
    @app.route('/')
    def dashboard():
        from datetime import datetime, timedelta
        
        total_emp = Employee.query.count()
        total_task = Task.query.count()
        total_schedule = Schedule.query.count()
        
        employees = Employee.query.all()
        schedules = Schedule.query.all()
        
        # --- BỔ SUNG LẤY DANH SÁCH CÔNG VIỆC TỪ DATABASE ---
        tasks = Task.query.all()
        # ---------------------------------------------------
        
        today = datetime.now().date()
        # Tính từ Thứ Hai đầu tuần
        start_of_week = today - timedelta(days=today.weekday())
        
        # Tạo danh sách 7 ngày trong tuần (Thứ 2 đến Chủ Nhật)
        week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
        
        # Tạo dictionary lưu trữ lịch: key là (employee_id, date, shift) -> value là tên task
        schedule_dict = {}
        for s in schedules:
            schedule_dict[(s.employee_id, s.date, s.shift)] = s.task.task_name if s.task else "Có lịch"
            
        return render_template('dashboard.html', 
                               total_emp=total_emp, 
                               total_task=total_task, 
                               total_schedule=total_schedule,
                               employees=employees,
                               tasks=tasks,  # <--- ĐÃ TRUYỀN TASKS SANG DASHBOARD.HTML
                               week_dates=week_dates,
                               schedule_dict=schedule_dict)

    # --- API THỐNG KÊ CHO DASHBOARD ---
    @app.route('/api/dashboard-stats')
    def dashboard_stats():
        from datetime import datetime, timedelta
        from sqlalchemy import func
        import json
        
        # Thống kê cơ bản
        total_employees = Employee.query.count()
        total_tasks = Task.query.count()
        total_schedules = Schedule.query.count()
        
        # Lấy dữ liệu phân công theo ngày (7 ngày gần nhất)
        today = datetime.now().date()
        date_7_days_ago = today - timedelta(days=7)
        
        schedule_by_date = db.session.query(
            Schedule.date, 
            func.count(Schedule.id).label('count')
        ).filter(
            Schedule.date >= date_7_days_ago
        ).group_by(Schedule.date).all()
        
        # Thống kê theo task (top 5)
        top_tasks = db.session.query(
            Task.task_name,
            func.count(Schedule.id).label('count')
        ).join(Schedule).group_by(Task.id).order_by(func.count(Schedule.id).desc()).limit(5).all()
        
        # Thống kê ca làm
        shift_stats = db.session.query(
            Schedule.shift,
            func.count(Schedule.id).label('count')
        ).group_by(Schedule.shift).all()
        
        return {
            'total_employees': total_employees,
            'total_tasks': total_tasks,
            'total_schedules': total_schedules,
            'schedule_by_date': [
                {'date': s[0].strftime('%d/%m'), 'count': s[1]}
                for s in schedule_by_date
            ],
            'top_tasks': [
                {'name': t[0], 'count': t[1]}
                for t in top_tasks
            ],
            'shift_stats': [
                {'shift': s[0], 'count': s[1]}
                for s in shift_stats
            ]
        }

    return app
