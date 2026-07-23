import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import db
from app.models.schedule import Schedule
from app.models.employee import Employee
from app.models.task import Task
from app.routes.auth import login_required

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

# --- 1. TRANG QUẢN LÝ PHÂN CÔNG (DẠNG DANH SÁCH / BẢNG CHI TIẾT) ---
@schedule_bp.route('/')
@login_required
def index():
    schedules = Schedule.query.order_by(Schedule.date.desc()).all()
    employees = Employee.query.all()
    tasks = Task.query.all()
    return render_template('schedule/index.html', schedules=schedules, employees=employees, tasks=tasks)

# --- 2. TRANG LỊCH TUẦN (DẠNG MA TRẬN CLICK ĐĂNG KÝ) ---
@schedule_bp.route('/weekly')
@login_required
def weekly():
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    employees = Employee.query.all()
    schedules = Schedule.query.all()
    tasks = Task.query.all()
    
    schedule_dict = {}
    for s in schedules:
        schedule_dict[(s.employee_id, s.date, s.shift)] = s.task.task_name if s.task else ''
            
    return render_template('schedule/weekly.html', 
                           employees=employees,
                           week_dates=week_dates,
                           schedule_dict=schedule_dict,
                           tasks=tasks)

@schedule_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        task_id = request.form.get('task_id')
        date_str = request.form.get('date')
        shift = request.form.get('shift')

        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        conflict = Schedule.query.filter_by(
            employee_id=employee_id, 
            date=date_obj, 
            shift=shift
        ).first()
        
        if conflict:
            error_msg = f"Lỗi: Nhân viên này đã được đăng ký ca {shift} vào ngày {date_str} rồi!"
            employees = Employee.query.all()
            tasks = Task.query.all()
            return render_template('schedule/add.html', employees=employees, tasks=tasks, error=error_msg)

        new_schedule = Schedule(
            employee_id=employee_id, 
            task_id=task_id, 
            date=date_obj, 
            shift=shift
        )
        db.session.add(new_schedule)
        db.session.commit()
        
        return redirect(request.referrer or url_for('schedule.index'))

    employees = Employee.query.all()
    tasks = Task.query.all()
    return render_template('schedule/add.html', employees=employees, tasks=tasks)

@schedule_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    s = Schedule.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return redirect(request.referrer or url_for('schedule.index'))
