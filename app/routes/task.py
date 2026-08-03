from flask import Blueprint, render_template, request, redirect, url_for
from app.models.task import Task
from app.models.schedule import Schedule  # Bổ sung import model Schedule để xử lý xóa ca liên quan
from app import db
from app.routes.auth import login_required

task_bp = Blueprint('task', __name__, url_prefix='/task')

@task_bp.route('/')
@login_required
def index():
    tasks_list = Task.query.all()
    return render_template('task/index.html', tasks=tasks_list)

@task_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        code = request.form.get('code')
        task_name = request.form.get('task_name')
        priority = request.form.get('priority')
        duration = request.form.get('duration')
        
        # Bắt giá trị mức lương từ giao diện
        wage = request.form.get('wage')
        
        # Xử lý mức lương (Mặc định 150000 nếu để trống hoặc nhập sai)
        try:
            wage_val = int(wage) if wage else 150000
        except ValueError:
            wage_val = 150000

        new_task = Task(
            code=code, 
            task_name=task_name, 
            priority=int(priority), 
            duration=int(duration),
            wage=wage_val  # Lưu mức lương vào DB
        )
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('task.index'))
        except:
            db.session.rollback()
            return "Mã công việc đã tồn tại!"
    return render_template('task/add.html')

@task_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    t = Task.query.get_or_404(id)
    if request.method == 'POST':
        t.code = request.form.get('code')
        t.task_name = request.form.get('task_name')
        t.priority = int(request.form.get('priority'))
        t.duration = int(request.form.get('duration'))
        
        # Cập nhật mức lương
        wage = request.form.get('wage')
        try:
            t.wage = int(wage) if wage else 150000
        except ValueError:
            t.wage = 150000

        try:
            db.session.commit()
            return redirect(url_for('task.index'))
        except:
            db.session.rollback()
            return "Lỗi cập nhật!"
    return render_template('task/edit.html', t=t)

@task_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    t = Task.query.get_or_404(id)
    try:
        # 1. Xóa tất cả các lịch làm việc đang sử dụng công việc này trước
        Schedule.query.filter_by(task_id=id).delete()
        
        # 2. Xóa công việc chính
        db.session.delete(t)
        
        # 3. Lưu lại thay đổi
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xóa công việc: {e}")
        
    return redirect(url_for('task.index'))
