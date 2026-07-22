from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models.schedule import Schedule
from app.models.employee import Employee
from app.models.task import Task
from app import db
from datetime import datetime, timedelta
from app.routes.auth import login_required
import json

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

@schedule_bp.route('/')
@login_required
def index():
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    # Tính từ Thứ Hai đầu tuần
    start_of_week = today - timedelta(days=today.weekday())
    
    # Tạo danh sách 7 ngày trong tuần (Thứ 2 đến Chủ Nhật)
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    employees = Employee.query.all()
    schedules = Schedule.query.all()
    tasks = Task.query.all()
    
    # Tạo dictionary lưu trữ lịch: key là (employee_id, date, shift) -> value là schedule object
    schedule_dict = {}
    for s in schedules:
        schedule_dict[(s.employee_id, s.date, s.shift)] = s
            
    return render_template('schedule/index.html', 
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

        # Chuyển đổi chuỗi ngày từ Form (YYYY-MM-DD) thành đối tượng Date của Python
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        # LOGIC KIỂM TRA TRÙNG LỊCH: Xem nhân viên này đã có lịch trong ca và ngày này chưa
        conflict = Schedule.query.filter_by(
            employee_id=employee_id, 
            date=date_obj, 
            shift=shift
        ).first()
        
        if conflict:
            # Nếu phát hiện trùng, trả về form kèm thông báo lỗi
            error_msg = f"Lỗi: Nhân viên này đã được đăng ký ca {shift} vào ngày {date_str} rồi!"
            employees = Employee.query.all()
            tasks = Task.query.all()
            return render_template('schedule/add.html', employees=employees, tasks=tasks, error=error_msg)

        # Nếu không trùng, tiến hành lưu vào Database
        new_schedule = Schedule(
            employee_id=employee_id, 
            task_id=task_id, 
            date=date_obj, 
            shift=shift
        )
        db.session.add(new_schedule)
        db.session.commit()
        return redirect(url_for('schedule.index'))

    # Nếu là GET request, lấy dữ liệu ngày/ca nếu được truyền sẵn từ giao diện Dashboard
    employees = Employee.query.all()
    tasks = Task.query.all()
    return render_template('schedule/add.html', employees=employees, tasks=tasks)

@schedule_bp.route('/register', methods=['POST'])
@login_required
def register():
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        task_id = data.get('task_id')
        date_str = data.get('date')
        shift = data.get('shift')

        # Chuyển đổi chuỗi ngày
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Kiểm tra xem ca này đã có người chưa
        existing = Schedule.query.filter_by(
            employee_id=employee_id,
            date=date_obj,
            shift=shift
        ).first()

        if existing:
            return jsonify({'success': False, 'message': 'Nhân viên này đã đăng ký ca này rồi!'})

        # Kiểm tra xem ca này có người khác đã đăng ký chưa
        shift_occupied = Schedule.query.filter_by(
            date=date_obj,
            shift=shift
        ).first()

        if shift_occupied:
            return jsonify({'success': False, 'message': 'Đã có người đăng ký ca này rồi!'})

        # Tạo phân công mới
        new_schedule = Schedule(
            employee_id=employee_id,
            task_id=task_id,
            date=date_obj,
            shift=shift
        )
        db.session.add(new_schedule)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Đăng ký ca thành công!', 'schedule_id': new_schedule.id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@schedule_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    s = Schedule.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return redirect(url_for('schedule.index'))