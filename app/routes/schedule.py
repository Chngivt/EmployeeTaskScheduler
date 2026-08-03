import random, re
import pandas as pd
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.schedule import Schedule
from app.models.employee import Employee
from app.models.task import Task
from app.routes.auth import login_required

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

def get_non_admin_employees():
    return Employee.query.filter(Employee.role != 'admin', Employee.email != 'caohoangviet738@gmail.com', Employee.department != 'Quản trị').all()

@schedule_bp.route('/')
@login_required
def index():
    schedules = Schedule.query.order_by(Schedule.date.desc()).all()
    employees = get_non_admin_employees()
    tasks = Task.query.all()
    return render_template('schedule/index.html', schedules=schedules, employees=employees, tasks=tasks)

@schedule_bp.route('/weekly')
@login_required
def weekly():
    # 1. Nhận tham số ngày từ URL (ĐỂ XEM CÁC TUẦN KHÁC)
    date_param = request.args.get('date')
    if date_param:
        try:
            base_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        except ValueError:
            base_date = datetime.now().date()
    else:
        base_date = datetime.now().date()

    # 2. Tính toán danh sách ngày của tuần đó
    start_of_week = base_date - timedelta(days=base_date.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    # 3. Truyền biến Tuần Trước / Tuần Sau ra giao diện HTML
    prev_week = (start_of_week - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week = (start_of_week + timedelta(days=7)).strftime('%Y-%m-%d')
    
    employees = get_non_admin_employees()
    
    # 4. CHỈ tải lịch của tuần đang xem (Giúp web tải nhanh hơn rất nhiều)
    schedules = Schedule.query.filter(
        Schedule.date >= start_of_week, 
        Schedule.date <= week_dates[-1]
    ).all()
    
    tasks = Task.query.all()
    
    schedule_objs = {(s.employee_id, s.date.strftime('%Y-%m-%d') if hasattr(s.date, 'strftime') else str(s.date), s.shift): s for s in schedules if s.date}
            
    return render_template('schedule/weekly.html', 
                           employees=employees, 
                           week_dates=week_dates, 
                           schedule_objs=schedule_objs, 
                           tasks=tasks,
                           prev_week=prev_week,
                           next_week=next_week)

@schedule_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        employee_id, task_id, date_str, shift = request.form.get('employee_id'), request.form.get('task_id'), request.form.get('date'), request.form.get('shift')
        if not all([employee_id, task_id, date_str, shift]): 
            return redirect(request.referrer or url_for('schedule.weekly'))

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            is_overtime = True if request.form.get('is_overtime') == '1' else (date_obj.weekday() >= 5 or shift == 'Tối')
            
            conflict = Schedule.query.filter_by(employee_id=int(employee_id), date=date_obj, shift=shift).first()
            if conflict:
                conflict.task_id = int(task_id)
                conflict.is_overtime = is_overtime
            else:
                db.session.add(Schedule(employee_id=int(employee_id), task_id=int(task_id), date=date_obj, shift=shift, is_overtime=is_overtime))
            db.session.commit()
        except Exception as e:
            db.session.rollback()

        # Giữ nguyên tuần đang xem sau khi Thêm ca
        return redirect(request.referrer or url_for('schedule.weekly'))
    return render_template('schedule/add.html', employees=get_non_admin_employees(), tasks=Task.query.all())

@schedule_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    s = Schedule.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return redirect(request.referrer or url_for('schedule.weekly'))

@schedule_bp.route('/delete_info', methods=['GET'])
@login_required
def delete_by_info():
    employee_id, date_str, shift = request.args.get('employee_id'), request.args.get('date'), request.args.get('shift')
    if employee_id and date_str and shift:
        try:
            schedule_item = Schedule.query.filter_by(employee_id=int(employee_id), date=datetime.strptime(date_str, '%Y-%m-%d').date(), shift=shift).first()
            if schedule_item:
                db.session.delete(schedule_item)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
    # Giữ nguyên tuần đang xem sau khi Xóa ca
    return redirect(request.referrer or url_for('schedule.weekly'))

@schedule_bp.route('/auto_assign', methods=['POST'])
@login_required
def auto_assign():
    start_date_str = request.form.get('start_date')
    if start_date_str:
        base_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        base_date = datetime.now().date()
        
    start_of_week = base_date - timedelta(days=base_date.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    employees, tasks = get_non_admin_employees(), Task.query.all()
    if not employees or not tasks: 
        return redirect(request.referrer or url_for('schedule.weekly'))
    
    for d in week_dates:
        if d.weekday() >= 5: continue
        for emp in employees:
            for shift in ['Sáng', 'Chiều']:
                if not Schedule.query.filter_by(employee_id=emp.id, date=d, shift=shift).first():
                    db.session.add(Schedule(employee_id=emp.id, task_id=random.choice(tasks).id, date=d, shift=shift, is_overtime=False))
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return redirect(request.referrer or url_for('schedule.weekly'))

@schedule_bp.route('/reset', methods=['POST'])
@login_required
def reset_schedule():
    start_date_str = request.form.get('start_date')
    try:
        if start_date_str:
            start_of_week = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_of_week = start_of_week + timedelta(days=6)
            # AN TOÀN: Chỉ xóa các ca trong Tuần đang xem, không xóa sạch DB
            Schedule.query.filter(Schedule.date >= start_of_week, Schedule.date <= end_of_week).delete()
        else:
            Schedule.query.delete()
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(request.referrer or url_for('schedule.weekly'))

@schedule_bp.route('/import_excel', methods=['POST'])
@login_required
def import_excel():
    file = request.files.get('excel_file')
    if file and file.filename.endswith(('.xlsx', '.xls')):
        try:
            df = pd.read_excel(file, sheet_name=0, skiprows=1)
            df.columns = ['Thứ', 'Buổi', 'Công việc', 'Nhân viên']
            df['Thứ'] = df['Thứ'].ffill()
            df['Buổi'] = df['Buổi'].ffill()
            
            for _, row in df.iterrows():
                match = re.search(r'(\d{2}/\d{2})', str(row['Thứ']))
                if not match: continue
                date_obj = datetime.strptime(f"{match.group(1)}/{datetime.now().year}", '%d/%m/%Y').date()
                
                emp = Employee.query.filter(db.func.trim(Employee.fullname) == str(row['Nhân viên']).strip()).first()
                if not emp or emp.role == 'admin': continue
                    
                task_name_str = str(row['Công việc']).strip()
                task = Task.query.filter(db.func.trim(Task.task_name) == task_name_str).first()
                if not task:
                    task = Task(task_name=task_name_str, code=task_name_str[:5], priority=2, duration=240, wage=150000)
                    db.session.add(task)
                    db.session.commit()
                    
                is_ot = (date_obj.weekday() >= 5) or (str(row['Buổi']).strip() == 'Tối')
                
                existing_schedule = Schedule.query.filter_by(employee_id=emp.id, date=date_obj, shift=str(row['Buổi']).strip()).first()
                if existing_schedule:
                    existing_schedule.task_id, existing_schedule.is_overtime = task.id, is_ot
                else:
                    db.session.add(Schedule(employee_id=emp.id, task_id=task.id, date=date_obj, shift=str(row['Buổi']).strip(), is_overtime=is_ot))
                
            db.session.commit()
        except Exception as e:
            db.session.rollback()
    return redirect(request.referrer or url_for('schedule.weekly'))
