import csv
import io

from flask import Blueprint, Response

from app.models.employee import Employee
from app.models.schedule import Schedule
from app.models.task import Task
from app.routes.auth import login_required

export_bp = Blueprint('export', __name__)

@export_bp.route('/export/tasks')
@login_required
def export_tasks():
    output = io.StringIO()
    
    # BỔ SUNG QUAN TRỌNG: Thêm ký tự BOM để Excel tự động nhận diện chuẩn UTF-8 Tiếng Việt
    output.write('\ufeff')
    
    writer = csv.writer(output)
    writer.writerow(['Mã nhân viên', 'Họ tên', 'Phòng ban', 'Ngày', 'Ca', 'Công việc', 'Mức độ', 'Thời lượng'])

    schedules = Schedule.query.all()
    for schedule in schedules:
        employee = Employee.query.get(schedule.employee_id)
        task = Task.query.get(schedule.task_id)
        writer.writerow([
            employee.code if employee else '',
            employee.fullname if employee else '',
            employee.department if employee else '',
            schedule.date.strftime('%d/%m/%Y') if schedule.date else '',
            schedule.shift,
            task.task_name if task else '',
            task.priority if task else '',
            task.duration if task else '',
        ])

    # BỔ SUNG QUAN TRỌNG: Khai báo charset=utf-8 trong mimetype
    response = Response(output.getvalue(), mimetype='text/csv; charset=utf-8')
    response.headers['Content-Disposition'] = 'attachment; filename=task_schedule.csv'
    return response
