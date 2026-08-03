import os
import pandas as pd
import calendar
from io import BytesIO
from datetime import datetime, date
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, send_file
from werkzeug.utils import secure_filename
from app import db
from app.models.employee import Employee
from app.models.schedule import Schedule
from app.routes.auth import login_required

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Chỉ Quản trị viên mới có quyền thực hiện thao tác này!', 'danger')
            return redirect(url_for('employee.index'))
        return f(*args, **kwargs)
    return decorated_function

@employee_bp.route('/')
@login_required
def index():
    employees = Employee.query.order_by(Employee.id.desc()).all()
    return render_template('employee/index.html', employees=employees)

@employee_bp.route('/pending-users')
@login_required
@admin_required
def pending_users():
    pending_list = Employee.query.filter_by(is_approved=False).all()
    return render_template('employee/pending.html', pending_list=pending_list)

@employee_bp.route('/approve/<int:id>')
@login_required
@admin_required
def approve_user(id):
    emp = Employee.query.get_or_404(id)
    emp.is_approved = True
    db.session.commit()
    flash(f'Đã phê duyệt tài khoản cho: {emp.fullname}', 'success')
    return redirect(url_for('employee.pending_users'))

@employee_bp.route('/reject/<int:id>')
@login_required
@admin_required
def reject_user(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    flash(f'Đã xóa yêu cầu của: {emp.fullname}', 'danger')
    return redirect(url_for('employee.pending_users'))

@employee_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        code = request.form.get('code')
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        department = request.form.get('department')
        position = request.form.get('position')

        existing_emp = Employee.query.filter((Employee.code == code) | (Employee.email == email)).first()
        if existing_emp:
            flash('Mã nhân viên hoặc Email đã tồn tại!', 'danger')
            return redirect(url_for('employee.add'))

        new_emp = Employee(
            code=code, fullname=fullname, email=email, phone=phone,
            department=department, position=position, role='employee', is_approved=True
        )
        new_emp.set_password('123456')
        db.session.add(new_emp)
        db.session.commit()
        return redirect(url_for('employee.index'))
    return render_template('employee/add.html')

@employee_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    emp = Employee.query.get_or_404(id)
    if request.method == 'POST':
        emp.fullname = request.form.get('fullname')
        emp.email = request.form.get('email')
        emp.phone = request.form.get('phone')
        emp.department = request.form.get('department')
        emp.position = request.form.get('position')
        emp.role = request.form.get('role', 'employee')
        
        new_password = request.form.get('password')
        if new_password and new_password.strip():
            emp.set_password(new_password.strip())
            
        try:
            db.session.commit()
            return redirect(url_for('employee.index'))
        except Exception as e:
            db.session.rollback()
    return render_template('employee/edit.html', emp=emp)

@employee_bp.route('/delete/<int:id>')
@login_required
@admin_required
def delete(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    return redirect(url_for('employee.index'))

@employee_bp.route('/salary')
@login_required
@admin_required
def salary_view():
    today = date.today()
    current_month, current_year = today.month, today.year
    _, last_day = calendar.monthrange(current_year, current_month)
    start_date, end_date = date(current_year, current_month, 1), date(current_year, current_month, last_day)

    employees = Employee.query.filter(Employee.role != 'admin', Employee.email != 'caohoangviet738@gmail.com').all()
    data = []
    OVERTIME_MULTIPLIER = 1.5

    for emp in employees:
        shifts = Schedule.query.filter(Schedule.employee_id == emp.id, Schedule.date >= start_date, Schedule.date <= end_date).all()
        total_salary, normal_count, overtime_count = 0, 0, 0
        
        for s in shifts:
            base_wage = int(s.task.wage) if s.task and s.task.wage else 150000
            is_ot = getattr(s, 'is_overtime', False) or (s.date.weekday() >= 5) or (s.shift == 'Tối')
            
            if is_ot:
                total_salary += base_wage * OVERTIME_MULTIPLIER
                overtime_count += 1
            else:
                total_salary += base_wage
                normal_count += 1

        if normal_count > 0 or overtime_count > 0:
            data.append({
                'code': emp.code, 'fullname': emp.fullname, 'department': emp.department,
                'normal_count': normal_count, 'overtime_count': overtime_count, 'total_salary': int(total_salary)
            })

    return render_template('employee/salary.html', salary_data=data, month=current_month, year=current_year)

@employee_bp.route('/salary/export')
@login_required
@admin_required
def export_salary():
    today = date.today()
    current_month, current_year = today.month, today.year
    _, last_day = calendar.monthrange(current_year, current_month)
    start_date, end_date = date(current_year, current_month, 1), date(current_year, current_month, last_day)

    employees = Employee.query.filter(Employee.role != 'admin', Employee.email != 'caohoangviet738@gmail.com').all()
    data = []
    OVERTIME_MULTIPLIER = 1.5

    for emp in employees:
        shifts = Schedule.query.filter(Schedule.employee_id == emp.id, Schedule.date >= start_date, Schedule.date <= end_date).all()
        total_salary, normal_count, overtime_count = 0, 0, 0
        
        for s in shifts:
            base_wage = int(s.task.wage) if s.task and s.task.wage else 150000
            is_ot = getattr(s, 'is_overtime', False) or (s.date.weekday() >= 5) or (s.shift == 'Tối')
            
            if is_ot:
                total_salary += base_wage * OVERTIME_MULTIPLIER
                overtime_count += 1
            else:
                total_salary += base_wage
                normal_count += 1

        if normal_count > 0 or overtime_count > 0:
            data.append({
                'Mã NV': emp.code, 'Họ và Tên': emp.fullname, 'Phòng ban': emp.department,
                'Số Ca Thường': normal_count, 'Số Ca Tăng Ca (x1.5)': overtime_count, 'Tổng Lương (VNĐ)': f"{int(total_salary):,}"
            })

    if not data:
        flash("Chưa có dữ liệu làm việc để xuất Excel!", "warning")
        return redirect(url_for('employee.salary_view'))

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Luong_T{current_month}_{current_year}')
    output.seek(0)
    return send_file(output, download_name=f"Bang_Luong_Thang_{current_month}_{current_year}.xlsx", as_attachment=True)
