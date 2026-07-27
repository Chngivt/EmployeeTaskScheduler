import json
import random
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app import db
from app.models.schedule import Schedule
from app.models.employee import Employee
from app.models.task import Task
from app.routes.auth import login_required

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

def get_non_admin_employees():
    # Lọc bỏ tài khoản Admin theo cả role, email và phòng ban
    return Employee.query.filter(
        Employee.role != 'admin',
        Employee.email != 'caohoangviet738@gmail.com',
        Employee.department != 'Quản trị'
    ).all()

def cleanup_admin_schedules():
    # Tự động xóa sạch các lịch phân công lỡ gán cho admin trước đó
    admin_employees = Employee.query.filter(
        (Employee.role == 'admin') | 
        (Employee.email == 'caohoangviet738@gmail.com') | 
        (Employee.department == 'Quản trị')
    ).all()
    admin_ids = [emp.id for emp in admin_employees]
    if admin_ids:
        Schedule.query.filter(Schedule.employee_id.in_(admin_ids)).delete(synchronize_session=False)
        db.session.commit()

# --- 1. TRANG DANH SÁCH PHÂN CÔNG ---
@schedule_bp.route('/')
@login_required
def index():
    cleanup_admin_schedules()
    schedules = Schedule.query.order_by(Schedule.date.desc()).all()
    employees = get_non_admin_employees()
    tasks = Task.query.all()
    return render_template('schedule/index.html', schedules=schedules, employees=employees, tasks=tasks)

# --- 2. TRANG BẢNG LỊCH TUẦN ---
@schedule_bp.route('/weekly')
@login_required
def weekly():
    cleanup_admin_schedules()
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    employees = get_non_admin_employees()
    schedules = Schedule.query.all()
    tasks = Task.query.all()
    
    schedule_dict = {}
    for s in schedules:
        if s.date:
            date_key = s.date.strftime('%Y-%m-%d') if hasattr(s.date, 'strftime') else str(s.date)
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
            emp = Employee.query.get(int(employee_id))
            if not emp or emp.role == 'admin' or emp.email == 'caohoangviet738@gmail.com' or emp.department == 'Quản trị':
                flash("Quản trị viên (Admin) không tham gia ca làm việc trực tiếp!", "danger")
                return redirect(url_for('schedule.weekly'))

            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

            conflict = Schedule.query.filter_by(
                employee_id=int(employee_id), 
                date=date_obj, 
                shift=shift
            ).first()
            
            if conflict:
                conflict.task_id = int(task_id)
            else:
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
            print(f"Lỗi khi thêm/cập nhật phân công: {e}")

        return redirect(request.referrer or url_for('schedule.weekly'))

    employees = get_non_admin_employees()
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

# --- 5. PHÂN CÔNG TỰ ĐỘNG ---
@schedule_bp.route('/auto_assign', methods=['POST'])
@login_required
def auto_assign():
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    employees = get_non_admin_employees()
    tasks = Task.query.all()
    
    if not employees or not tasks:
        flash("Lỗi: Cần có ít nhất 1 nhân viên và 1 công việc trong hệ thống để thực hiện phân công tự động!", "danger")
        return redirect(url_for('schedule.weekly'))
        
    shifts = ['Sáng', 'Chiều'] 
    assigned_count = 0
    
    for d in week_dates:
        for emp in employees:
            for shift in shifts:
                existing_schedule = Schedule.query.filter_by(employee_id=emp.id, date=d, shift=shift).first()
                if not existing_schedule:
                    random_task = random.choice(tasks)
                    new_schedule = Schedule(
                        employee_id=emp.id,
                        task_id=random_task.id,
                        date=d,
                        shift=shift
                    )
                    db.session.add(new_schedule)
                    assigned_count += 1
                    
    try:
        db.session.commit()
        if assigned_count > 0:
            flash(f"Thành công: Đã tự động điền {assigned_count} ca làm việc trống cho nhân viên trong tuần này!", "success")
        else:
            flash("Tuần này nhân viên đã được phân công kín lịch, không có ca trống nào cần điền thêm.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Đã xảy ra lỗi khi phân công tự động: {e}", "danger")
        
    return redirect(url_for('schedule.weekly'))
