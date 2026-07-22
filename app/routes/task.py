from flask import Blueprint, render_template, request, redirect, url_for
from app.models.task import Task
from app import db
from app.routes.auth import login_required

task_bp = Blueprint('task', __name__, url_prefix='/task')

@task_bp.route('/')
@login_required
def index():
    tasks_list = Task.query.all()
    return render_template('task/index.html', tasks=tasks_list)

@task_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        code = request.form.get('code')
        task_name = request.form.get('task_name')
        priority = request.form.get('priority')
        duration = request.form.get('duration')

        new_task = Task(code=code, task_name=task_name, priority=int(priority), duration=int(duration))
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('task.index'))
        except:
            db.session.rollback()
            return "Mã công việc đã tồn tại!"
    return render_template('task/add.html')

@task_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    t = Task.query.get_or_404(id)
    if request.method == 'POST':
        t.code = request.form.get('code')
        t.task_name = request.form.get('task_name')
        t.priority = int(request.form.get('priority'))
        t.duration = int(request.form.get('duration'))
        try:
            db.session.commit()
            return redirect(url_for('task.index'))
        except:
            db.session.rollback()
            return "Lỗi cập nhật!"
    return render_template('task/edit.html', t=t)

@task_bp.route('/delete/<int:id>')
def delete(id):
    t = Task.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return redirect(url_for('task.index'))