import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models.employee import Employee
from app.routes.auth import login_required

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 1. DANH SÁCH NHÂN VIÊN ---
@employee_bp.route('/')
@login_required
def index():
    employees = Employee.query.order_by(Employee.id.desc()).all()
    return render_template('employee/index.html', employees=employees)

# --- 2. THÊM NHÂN VIÊN MỚI ---
@employee_bp.route('/add', methods=['GET', 'POST'])
@login_required
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
            role='employee'
        )
        new_emp.set_password('123456')

        db.session.add(new_emp)
        db.session.commit()
        return redirect(url_for('employee.index'))

    return render_template('employee/add.html')

# --- 3. CHỈNH SỬA NHÂN VIÊN (ĐÃ SỬA CHUẨN ĐẦY ĐỦ LOGIC) ---
@employee_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
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

        # Kiểm tra xem Email mới có bị trùng với nhân viên khác trong hệ thống không
        existing_email = Employee.query.filter(Employee.email == email, Employee.id != id).first()
        if existing_email:
            return render_template('employee/edit.html', emp=emp, error="Email này đã được sử dụng bởi nhân viên khác!")

        # Cập nhật thông tin
        emp.fullname = fullname
        emp.email = email
        emp.phone = phone
        emp.department = department
        emp.position = position
        emp.role = role

        # Xử lý đổi mật khẩu nếu người dùng có nhập mật khẩu mới
        if new_password and new_password.strip():
            emp.set_password(new_password.strip())

        # Xử lý upload ảnh đại diện mới
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

    # TRUYỀN ĐÚNG BIẾN 'emp' TƯƠNG THÍCH HOÀN HẢO VỚI FILE edit.html
    return render_template('employee/edit.html', emp=emp)

# --- 4. XÓA NHÂN VIÊN ---
@employee_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    return redirect(url_for('employee.index'))
