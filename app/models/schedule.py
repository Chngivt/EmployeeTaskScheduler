from app import db
from datetime import datetime

class Schedule(db.Model):
    __tablename__ = 'schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    # Khóa ngoại liên kết tới bảng Employee và Task
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False)
    shift = db.Column(db.String(20), nullable=False) # 'Sáng' hoặc 'Chiều' hoặc 'Tối'