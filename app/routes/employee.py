from flask import Blueprint, render_template, request, redirect, url_for
from app.models.employee import Employee
from app import db # Gọi CSDL để lưu dữ liệu

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

# Route hiển thị danh sách
@employee_bp.route('/')
def index():
    employees_list = Employee.query.all()
    return render_template('employee/index.html', employees=employees_list)

# Route xử lý Thêm nhân viên
@employee_bp.route('/add', methods=['GET', 'POST'])
def add():
    # Nếu người dùng bấm nút "Lưu Thông Tin" (gửi POST request)
    if request.method == 'POST':
        # Lấy dữ liệu từ các ô input của Form
        code = request.form.get('code')
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        department = request.form.get('department')
        position = request.form.get('position')

        # Tạo một đối tượng Nhân viên mới
        new_emp = Employee(
            code=code, fullname=fullname, email=email, 
            phone=phone, department=department, position=position
        )
        
        try:
            # Lưu vào Database
            db.session.add(new_emp)
            db.session.commit()
            # Lưu xong thì tự động quay về trang danh sách
            return redirect(url_for('employee.index'))
        except Exception as e:
            db.session.rollback() # Báo lỗi nếu trùng Mã NV hoặc Email
            return f"Có lỗi xảy ra (Mã NV hoặc Email đã tồn tại). Bấm quay lại để thử mã khác."

    # Nếu chỉ truy cập bình thường (GET) thì mở giao diện Form
    return render_template('employee/add.html')
# Route xử lý Sửa thông tin nhân viên
@employee_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    # Tìm nhân viên theo ID, nếu không có thì báo lỗi 404
    emp = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        # Cập nhật thông tin mới từ Form
        emp.code = request.form.get('code')
        emp.fullname = request.form.get('fullname')
        emp.email = request.form.get('email')
        emp.phone = request.form.get('phone')
        emp.department = request.form.get('department')
        emp.position = request.form.get('position')
        
        try:
            db.session.commit()
            return redirect(url_for('employee.index'))
        except Exception as e:
            db.session.rollback()
            return "Có lỗi xảy ra (Mã NV hoặc Email đã tồn tại). Bấm quay lại để thử lại."

    # Nếu là GET, hiển thị form kèm dữ liệu cũ
    return render_template('employee/edit.html', emp=emp)

# Route xử lý Xóa nhân viên
@employee_bp.route('/delete/<int:id>')
def delete(id):
    emp = Employee.query.get_or_404(id)
    try:
        db.session.delete(emp)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    
    return redirect(url_for('employee.index'))