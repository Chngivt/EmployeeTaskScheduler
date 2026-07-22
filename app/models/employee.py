from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Employee(db.Model):
    __tablename__ = 'employee'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    
    # Trường mật khẩu và phân quyền mới
    password_hash = db.Column(db.String(255), nullable=False, default='pbkdf2:sha256:600000$defaultpassword')
    role = db.Column(db.String(20), default='employee') # 'admin' hoặc 'employee'

    schedules = db.relationship('Schedule', backref='employee', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)