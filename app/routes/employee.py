from flask import Blueprint, render_template, request, redirect, url_for
from app.models.employee import Employee
from app import db
from app.routes.auth import login_required

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

@employee_bp.route('/')
@login_required
def index():
    employees = Employee.query.all()
    return render_template('employee/index.html', employees=employees)

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

        new_emp = Employee(
            code=code,
            fullname=fullname,
            email=email,
            phone=phone,
            department=department,
            position=position
        )
        db.session.add(new_emp)
        db.session.commit()
        return redirect(url_for('employee.index'))

    return render_template('employee/add.html')


@employee_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    emp = Employee.query.get_or_404(id)

    if request.method == 'POST':
        emp.fullname = request.form.get('fullname')
        emp.email = request.form.get('email')
        emp.phone = request.form.get('phone')
        emp.department = request.form.get('department')
        emp.position = request.form.get('position')
        emp.role = request.form.get('role', emp.role)

        password = request.form.get('password')
        if password:
            emp.set_password(password)

        db.session.commit()
        return redirect(url_for('employee.index'))

    return render_template('employee/edit.html', emp=emp)


@employee_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    return redirect(url_for('employee.index'))