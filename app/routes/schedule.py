import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import db
from app.models.schedule import Schedule
from app.models.employee import Employee
from app.models.task import Task
from app.routes.auth import login_required

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

# --- 1. TRANG DANH SÁCH PHÂN CÔNG ---
@schedule_bp.route('/')
@login_required
def index():
    schedules = Schedule.query.order_by(Schedule.date.desc()).all()
    employees = Employee.query.all()
    tasks = Task.query.all()
    return render_template('schedule/index.html', schedules=schedules, employees=employees, tasks=tasks)

# --- 2. TRANG BẢNG LỊCH TUẦN ---
@schedule_bp.route('/weekly')
@login_required
def weekly():
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    employees = Employee.query.all()
    schedules = Schedule.query.all()
    tasks = Task.query.all()
    
    # Chuẩn hóa Key định dạng Chuỗi 'YYYY-MM-DD' để khớp 100% với giao diện
    schedule_dict = {}
    for s in schedules:
        if s.date:
            date_key = s.date.strftime('%Y-%m-%d') if hasattr(s.date, 'strftime') else str(s.date)
            # Lấy tên công việc linh hoạt
            t_name = "Có lịch"
            if s.task:
                t_name = getattr(s.task, 'task_name', None) or getattr(s.task, 'name', None) or "Có lịch"
            schedule_dict[(s.employee_id, date_key, s.shift)] = t_name
            
    return render_template('schedule/weekly.html', 
                           employees=employees,
                           week_dates=week_dates,
                           schedule_dict=schedule_dict,
                           tasks=tasks)

# --- 3. XỬ LÝ THÊM/ĐĂNG KÝ PHÂN CÔNG ---
@schedule_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        task_id = request.form.get('task_id')
        date_str = request.form.get('date')
        shift = request.form.get('shift')

        if not employee_id or not task_id or not date_str or not shift:
            return redirect(request.referrer or url_for('schedule.weekly'))

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

            conflict = Schedule.query.filter_by(
                employee_id=int(employee_id), 
                date=date_obj, 
                shift=shift
            ).first()
            
            if not conflict:
                new_schedule = Schedule(
                    employee_id=int(employee_id), 
                    task_id=int(task_id), 
                    date=date_obj, 
                    shift=shift
                )
                db.session.add(new_schedule)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi thêm phân công: {e}")

        return redirect(request.referrer or url_for('schedule.weekly'))

    employees = Employee.query.all()
    tasks = Task.query.all()
    return render_template('schedule/add.html', employees=employees, tasks=tasks)

# --- 4. XÓA PHÂN CÔNG ---
@schedule_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    s = Schedule.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return redirect(request.referrer or url_for('schedule.weekly'))
