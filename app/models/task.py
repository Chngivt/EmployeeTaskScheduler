from app import db

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    wage = db.Column(db.Integer, default=150000) # Đơn giá / Ca
    priority = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    schedules = db.relationship('Schedule', backref='task', lazy=True)
