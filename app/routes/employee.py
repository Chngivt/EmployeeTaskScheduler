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

# --- DECORATOR KIỂM TRA QUYỀN ADMIN ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Chỉ Quản trị viên (Admin) mới có quyền thực hiện thao tác này!', 'danger')
            return redirect(url_for('employee.index'))
        return f(*args, **kwargs)
    return decorated_function

# --- 1. DANH SÁCH NHÂN VIÊN (AI CŨNG XEM ĐƯỢC) ---
@employee_bp.route('/')
@login_required
def index():
    employees = Employee.query.order_by(Employee.id.desc()).all()
    return render_template('employee/index.html', employees=employees)

# --- TRANG XEM DANH SÁCH CHỜ DUYỆT (CHỈ ADMIN) ---
@employee_bp.route('/pending-users')
@login_required
@admin_required
def pending_users():
    pending_list = Employee.query.filter_by(is_approved=False).all()
    return render_template('employee/pending.html', pending_list=pending_list)

# --- DUYỆT TÀI KHOẢN (CHỈ ADMIN) ---
@employee_bp.route('/approve/<int:id>')
@login_required
@admin_required
def approve_user(id):
    emp = Employee.query.get_or_404(id)
    emp.is_approved = True
    db.session.commit()
    flash(f'Đã phê duyệt tài khoản cho nhân viên: {emp.fullname}', 'success')
    return redirect(url_for('employee.pending_users'))

# --- TỪ CHỐI / XÓA TÀI KHOẢN CHỜ DUYỆT (CHỈ ADMIN) ---
@employee_bp.route('/reject/<int:id>')
@login_required
@admin_required
def reject_user(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    flash(f'Đã từ chối và xóa yêu cầu đăng ký của: {emp.fullname}', 'danger')
    return redirect(url_for('employee.pending_users'))

# --- 2. THÊM NHÂN VIÊN MỚI (CHỈ ADMIN) ---
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

        avatar_filename = None
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                avatar_filename = timestamp + filename

                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, avatar_filename))

        existing_emp = Employee.query.filter(
            (Employee.code == code) | (Employee.email == email)
        ).first()

        if existing_emp:
            flash('Mã nhân viên hoặc Email đã tồn tại!', 'danger')
            return redirect(url_for('employee.add'))

        new_emp = Employee(
            code=code,
            fullname=fullname,
            email=email,
            phone=phone,
            department=department,
            position=position,
            avatar=avatar_filename,
            role='employee',
            is_approved=True  # Tài khoản do Admin trực tiếp thêm sẽ được duyệt sẵn
        )
        new_emp.set_password('123456')

        db.session.add(new_emp)
        db.session.commit()
        return redirect(url_for('employee.index'))

    return render_template('employee/add.html')

# --- 3. CHỈNH SỬA NHÂN VIÊN (CHỈ ADMIN) ---
@employee_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    emp = Employee.query.get_or_404(id)

    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        department = request.form.get('department')
        position = request.form.get('position')
        role = request.form.get('role', 'employee')
        new_password = request.form.get('password')

        existing_email = Employee.query.filter(Employee.email == email, Employee.id != id).first()
        if existing_email:
            return render_template('employee/edit.html', emp=emp, error="Email này đã được sử dụng bởi nhân viên khác!")

        emp.fullname = fullname
        emp.email = email
        emp.phone = phone
        emp.department = department
        emp.position = position
        emp.role = role

        if new_password and new_password.strip():
            emp.set_password(new_password.strip())

        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                avatar_filename = timestamp + filename

                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, avatar_filename))

                emp.avatar = avatar_filename

        try:
            db.session.commit()
            return redirect(url_for('employee.index'))
        except Exception as e:
            db.session.rollback()
            return render_template('employee/edit.html', emp=emp, error=f"Lỗi lưu CSDL: {e}")

    return render_template('employee/edit.html', emp=emp)

# --- 4. XÓA NHÂN VIÊN (CHỈ ADMIN) ---
@employee_bp.route('/delete/<int:id>')
@login_required
@admin_required
def delete(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    return redirect(url_for('employee.index'))

# --- 5. TÍNH LƯƠNG TỰ ĐỘNG THEO TỪNG CÔNG VIỆC VÀ TĂNG CA (CHỈ ADMIN) ---
@employee_bp.route('/salary')
@login_required
@admin_required
def export_salary():
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Tính ngày đầu tháng và cuối tháng
    _, last_day = calendar.monthrange(current_year, current_month)
    start_date = date(current_year, current_month, 1)
    end_date = date(current_year, current_month, last_day)

    # Truy vấn danh sách nhân viên (bỏ qua admin)
    employees = Employee.query.filter(
        Employee.role != 'admin',
        Employee.email != 'caohoangviet738@gmail.com'
    ).all()

    data = []
    OVERTIME_MULTIPLIER = 1.5  # Hệ số nhân lương tăng ca

    for emp in employees:
        # Lấy tất cả các ca làm việc của nhân viên này trong tháng hiện tại
        shifts = Schedule.query.filter(
            Schedule.employee_id == emp.id,
            Schedule.date >= start_date,
            Schedule.date <= end_date
        ).all()
        
        total_salary = 0
        normal_count = 0
        overtime_count = 0
        
        for s in shifts:
            # Lấy lương cơ bản của công việc đó (Nếu chưa cài hoặc lỗi thì mặc định 150k)
            try:
                base_wage = int(s.task.wage) if s.task and s.task.wage else 150000
            except:
                base_wage = 150000

            # Kiểm tra xem ca này có đánh dấu tăng ca không
            is_ot = getattr(s, 'is_overtime', False)
            
            if is_ot:
                total_salary += base_wage * OVERTIME_MULTIPLIER
                overtime_count += 1
            else:
                total_salary += base_wage
                normal_count += 1

        # Chỉ xuất ra Excel những nhân viên CÓ ĐI LÀM trong tháng
        if normal_count > 0 or overtime_count > 0:
            data.append({
                'Mã NV': emp.code,
                'Họ và Tên': emp.fullname,
                'Phòng ban': emp.department,
                'Số Ca Thường': normal_count,
                'Số Ca Tăng Ca (x1.5)': overtime_count,
                'Tổng Lương (VNĐ)': f"{int(total_salary):,}"
            })

    # Nếu không có ai đi làm trong tháng này
    if not data:
        flash("Chưa có dữ liệu làm việc trong tháng này để xuất bảng lương!", "warning")
        return redirect(url_for('employee.index'))

    # Tạo file Excel
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Luong_T{current_month}_{current_year}')
        
        # Căn chỉnh độ rộng cột cho đẹp
        worksheet = writer.sheets[f'Luong_T{current_month}_{current_year}']
        for idx, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 4
            worksheet.column_dimensions[chr(65 + idx)].width = max_len

    output.seek(0)
    filename = f"Bang_Luong_Thang_{current_month}_{current_year}.xlsx"
    
    return send_file(output, download_name=filename, as_attachment=True)
