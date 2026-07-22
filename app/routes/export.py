import pandas as pd
from flask import Blueprint, send_file
import io
from app.models.task import Task

export_bp = Blueprint('export', __name__)

@export_bp.route('/export/tasks')
def export_tasks():
    # Lấy toàn bộ danh sách task từ database
    tasks = Task.query.all()
    
    # Chuyển dữ liệu thành dạng danh sách từ điển
    data = []
    for t in tasks:
        data.append({
            'ID': t.id,
            'Tên công việc': t.task_name,
            'Mô tả': t.description,
            'Trạng thái': t.status
        })
        
    # Tạo DataFrame bằng pandas
    df = pd.DataFrame(data)
    
    # Lưu ra bộ nhớ tạm dưới dạng file Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='DanhSachTask')
    output.seek(0)
    
    # Trả file về cho trình duyệt tải xuống
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='Danh_sach_cong_viec.xlsx'
    )