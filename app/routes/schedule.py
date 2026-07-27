import json
import random
import re
import pandas as pd
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app import db
from app.models.schedule import Schedule
from app.models.employee import Employee
from app.models.task import Task
from app.routes.auth import login_required

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

def get_non_admin_employees():
    return Employee.query.filter(
        Employee.role != 'admin',
        Employee.email != 'caohoangviet738@gmail.com',
        Employee.department != 'Quản trị'
    ).all()

def cleanup_admin_schedules():
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
    
    # Lưu toàn bộ object Schedule vào dictionary để template có thể gọi và hiển thị nút xóa trực tiếp
    schedule_objs = {}
    for s in schedules:
        if s.date:
            date_key = s.date.strftime('%Y-%m-%d') if hasattr(s.date, 'strftime') else str(s.date)
            schedule_objs[(s.employee_id, date_key, s.shift)] = s
            
    return render_template('schedule/weekly.html', 
                           employees=employees,
                           week_dates=week_dates,
                           schedule_objs=schedule_objs,
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

# --- 4. XÓA PHÂN CÔNG THEO ID ---
@schedule_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    s = Schedule.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return redirect(request.referrer or url_for('schedule.weekly'))

# --- 5. XÓA CA TRỰC TIẾP TRÊN BẢNG LỊCH TUẦN ---
@schedule_bp.route('/delete_info', methods=['GET'])
@login_required
def delete_by_info():
    employee_id = request.args.get('employee_id')
    date_str = request.args.get('date')
    shift = request.args.get('shift')
    
    if employee_id and date_str and shift:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            schedule_item = Schedule.query.filter_by(
                employee_id=int(employee_id),
                date=date_obj,
                shift=shift
            ).first()
            
            if schedule_item:
                db.session.delete(schedule_item)
                db.session.commit()
                flash("Đã hủy ca làm việc thành công!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi khi hủy ca: {e}", "danger")
            
    return redirect(url_for('schedule.weekly'))

# --- 6. PHÂN CÔNG TỰ ĐỘNG ---
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
        
    shifts = ['Sáng', 'Chiều', 'Tối'] 
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

# --- 7. XÓA TẤT CẢ LỊCH (KHÔNG RANDOM) ---
@schedule_bp.route('/reset', methods=['POST'])
@login_required
def reset_schedule():
    try:
        Schedule.query.delete()
        db.session.commit()
        flash("Đã xóa toàn bộ lịch phân công thành công!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi khi xóa lịch: {e}", "danger")
        
    return redirect(url_for('schedule.weekly'))

# --- 8. NẠP EXCEL TỰ ĐỘNG PHÂN CÔNG ---
@schedule_bp.route('/import_excel', methods=['POST'])
@login_required
def import_excel():
    if 'excel_file' not in request.files:
        flash("Không tìm thấy file tải lên!", "danger")
        return redirect(url_for('schedule.weekly'))
        
    file = request.files['excel_file']
    if file.filename == '':
        flash("Bạn chưa chọn file Excel nào!", "danger")
        return redirect(url_for('schedule.weekly'))
        
    if file and file.filename.endswith(('.xlsx', '.xls')):
        try:
            df = pd.read_excel(file, sheet_name=0, skiprows=1)
            if len(df.columns) < 4:
                flash("Cấu trúc file Excel không hợp lệ! Cần có các cột: Thứ, Buổi, Công việc phân công, Người thực hiện.", "danger")
                return redirect(url_for('schedule.weekly'))
                
            df.columns = ['Thứ', 'Buổi', 'Công việc', 'Nhân viên']
            df['Thứ'] = df['Thứ'].ffill()
            df['Buổi'] = df['Buổi'].ffill()
            
            imported_count = 0
            for _, row in df.iterrows():
                thu_str = str(row['Thứ'])
                buoi_str = str(row['Buổi']).strip()
                task_name_str = str(row['Công việc']).strip()
                emp_name_str = str(row['Nhân viên']).strip()
                
                match = re.search(r'(\d{2}/\d{2})', thu_str)
                if not match:
                    continue
                
                current_year = datetime.now().year
                date_obj = datetime.strptime(f"{match.group(1)}/{current_year}", '%d/%m/%Y').date()
                
                emp = Employee.query.filter(db.func.trim(Employee.fullname) == emp_name_str).first()
                if not emp or emp.role == 'admin' or emp.email == 'caohoangviet738@gmail.com' or emp.department == 'Quản trị':
                    continue
                    
                task = Task.query.filter(db.func.trim(Task.task_name) == task_name_str).first()
                
                if not task:
                    task = Task(task_name=task_name_str)
                    db.session.add(task)
                    db.session.commit()
                    
                existing_schedule = Schedule.query.filter_by(
                    employee_id=emp.id,
                    date=date_obj,
                    shift=buoi_str
                ).first()
                
                if existing_schedule:
                    existing_schedule.task_id = task.id
                else:
                    new_sched = Schedule(
                        employee_id=emp.id,
                        task_id=task.id,
                        date=date_obj,
                        shift=buoi_str
                    )
                    db.session.add(new_sched)
                
                imported_count += 1
                
            db.session.commit()
            flash(f"Nạp file Excel thành công! Đã cập nhật {imported_count} phân công ca làm việc.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi khi xử lý file Excel: {e}", "danger")
    else:
        flash("Chỉ hỗ trợ định dạng file Excel (.xlsx, .xls)!", "warning")
        
    return redirect(url_for('schedule.weekly'))
