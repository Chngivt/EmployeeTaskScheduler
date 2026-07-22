import random
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.employee import Employee
from app import db, mail
from flask_mail import Message

auth_bp = Blueprint('auth', __name__)

# --- BỔ SUNG HÀM BẢO VỆ ĐĂNG NHẬP ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'employee_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        emp = Employee.query.filter_by(email=email).first()
        if emp and emp.check_password(password):
            session['employee_id'] = emp.id
            session['fullname'] = emp.fullname
            session['role'] = emp.role
            return redirect(url_for('dashboard'))
        else:
            return render_template('auth/login.html', error="Email hoặc mật khẩu không chính xác!")
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        code = request.form.get('code')
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        department = request.form.get('department')
        position = request.form.get('position')
        password = request.form.get('password')
        
        # Kiểm tra trùng lặp
        existing_emp = Employee.query.filter((Employee.email == email) | (Employee.code == code)).first()
        if existing_emp:
            return render_template('auth/register.html', error="Mã nhân viên hoặc Email đã tồn tại trong hệ thống!")
        
        # 1. Tạo mã xác nhận ngẫu nhiên 6 chữ số
        verification_code = str(random.randint(100000, 999999))
        
        # Tạo nhân viên mới
        new_emp = Employee(
            code=code,
            fullname=fullname,
            email=email,
            phone=phone,
            department=department,
            position=position,
            role='employee'
        )
        new_emp.set_password(password)
        
        db.session.add(new_emp)
        db.session.commit()
        
        # 2. Tự động gửi mã xác nhận về Gmail của nhân viên
        try:
            msg = Message('Mã Xác Nhận Tài Khoản - Employee Task Scheduler', recipients=[email])
            msg.body = f"""Xin chào {fullname},

Cảm ơn bạn đã đăng ký tài khoản trên hệ thống Employee Task Scheduler.
Mã xác nhận tài khoản của bạn là: {verification_code}

Vui lòng giữ bảo mật mã này để hoàn tất quá trình xác thực.

Trân trọng,
Quản trị viên hệ thống."""
            mail.send(msg)
        except Exception as e:
            print("Lỗi gửi mail (kiểm tra lại cấu hình SMTP trong config.py):", e)
        
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))