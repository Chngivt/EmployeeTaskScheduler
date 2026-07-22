# Employee Task Scheduler

Hệ thống quản lý nhân viên và phân công công việc tự động được xây dựng bằng **Flask (Python)** và **Bootstrap 5**.

## Các tính năng chính
- **Quản lý Nhân viên (CRUD):** Thêm, sửa, xóa, quản lý thông tin nhân viên (Mã NV, họ tên, email, phòng ban, chức vụ).
- **Quản lý Công việc (CRUD):** Quản lý danh sách nhiệm vụ, độ ưu tiên (Cao, Trung bình, Thấp) và thời lượng thực hiện.
- **Phân công Công việc & Kiểm tra Trùng lịch:** 
  - Phân công công việc cho nhân viên theo ngày và ca làm việc (Sáng/Chiều).
  - **Tự động chặn xung đột:** Hệ thống kiểm tra và ngăn chặn việc phân công trùng một nhân viên vào cùng một ca trong cùng một ngày.
- **Dashboard Tổng quan:** Hiển thị số liệu thống kê trực quan và bảng Lịch làm việc toàn hệ thống.

## Công nghệ sử dụng
- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Migrate
- **Database:** SQLite
- **Frontend:** HTML5, Bootstrap 5

## Hướng dẫn cài đặt và chạy dự án
1. Clone repository về máy:
   ```bash
   git clone [https://github.com/Chngivt/EmployeeTaskScheduler.git](https://github.com/Chngivt/EmployeeTaskScheduler.git)
   cd EmployeeTaskScheduler