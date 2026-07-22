from flask import Blueprint, render_template, request, redirect, url_for
from app.models.schedule import Schedule
from app.models.employee import Employee
from app.models.task import Task
from app import db
from datetime import datetime
from app.routes.auth import login_required

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

@schedule_bp.route('/')
@login_required
def index():
    # Lấy danh sách lịch phân công, sắp xếp theo ngày mới nhất
    schedules_list = Schedule.query.order_by(Schedule.date.desc()).all()
    return render_template('schedule/index.html', schedules=schedules_list)

@schedule_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        task_id = request.form.get('task_id')
        date_str = request.form.get('date')
        shift = request.form.get('shift')

        # Chuyển đổi chuỗi ngày từ Form (YYYY-MM-DD) thành đối tượng Date của Python
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        # LOGIC QUAN TRỌNG: Kiểm tra trùng lịch
        conflict = Schedule.query.filter_by(employee_id=employee_id, date=date_obj, shift=shift).first()
        
        if conflict:
            # Nếu phát hiện trùng, trả về form kèm thông báo lỗi
            error_msg = f"Lỗi: Nhân viên này đã bị phân công công việc vào ca {shift} ngày {date_str}!"
            employees = Employee.query.all()
            tasks = Task.query.all()
            return render_template('schedule/add.html', employees=employees, tasks=tasks, error=error_msg)

        # Nếu không trùng, tiến hành lưu vào DB
        new_schedule = Schedule(employee_id=employee_id, task_id=task_id, date=date_obj, shift=shift)
        db.session.add(new_schedule)
        db.session.commit()
        return redirect(url_for('schedule.index'))

    # Nếu là GET request, gửi danh sách Nhân viên và Công việc sang form để làm Menu chọn (Dropdown)
    employees = Employee.query.all()
    tasks = Task.query.all()
    return render_template('schedule/add.html', employees=employees, tasks=tasks)

@schedule_bp.route('/delete/<int:id>')
def delete(id):
    s = Schedule.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return redirect(url_for('schedule.index'))