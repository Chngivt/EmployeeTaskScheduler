from app import db

class Task(db.Model):
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.Integer, nullable=False) # Ví dụ: 1-Cao, 2-TB, 3-Thấp
    duration = db.Column(db.Integer, nullable=False) # Thời lượng (giờ)
    
    # Mối quan hệ: Một công việc có thể xuất hiện trong nhiều lịch phân công
    schedules = db.relationship('Schedule', backref='task', lazy=True)