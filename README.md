# 🏢 Task Scheduler & Employee Management System (Hệ Thống Quản Lý Nhân Sự & Phân Công Ca Làm Việc)

> **Mô tả dự án:** Đây là một ứng dụng web quản lý nội bộ toàn diện được phát triển bằng ngôn ngữ Python sử dụng micro-framework **Flask**, kết hợp với giao diện hiện đại **Bootstrap 5** nhằm tối ưu hóa quy trình vận hành doanh nghiệp. Hệ thống tập trung giải quyết các bài toán cốt lõi trong doanh nghiệp như quản lý hồ sơ nhân sự, phân công ca làm việc trực quan theo tuần, tính lương tự động dựa trên hệ số tăng ca và tích hợp sâu dữ liệu Excel.

---

## 🌟 Tổng Quan Về Các Tính Năng Nổi Bật Của Hệ Thống

### 1. Phân Quyền & Quản Lý Nhân Sự Chuyên Sâu
* **Phân quyền truy cập rõ ràng:** Hệ thống thiết lập phân cấp rõ ràng giữa tài khoản Quản trị viên (**Admin**) có toàn quyền kiểm soát hệ thống và tài khoản **Nhân viên** với các quyền giới hạn phù hợp.
* **Quy trình phê duyệt tài khoản bảo mật:** Khi nhân viên mới đăng ký tài khoản trên hệ thống, tài khoản sẽ ở trạng thái chờ (`Pending Users`). Quản trị viên cần phải xem xét và bấm phê duyệt thì tài khoản đó mới được kích hoạt và tham gia vào hệ thống phân công.
* **Cá nhân hóa hồ sơ cá nhân:** Cho phép cập nhật đầy đủ thông tin chi tiết của nhân sự bao gồm mã nhân viên, họ tên, email, số điện thoại, chọn phòng ban chuyên môn (Quản lý, Kỹ Thuật, Bán hàng, Marketing, Giao Hàng, Quản trị) và chức vụ.
* **Tính năng tải lên Ảnh đại diện (Avatar):** Hỗ trợ người dùng tải ảnh cá nhân lên hệ thống, tự động kiểm tra định dạng file hợp lệ (`png`, `jpg`, `jpeg`, `webp`), xử lý và lưu trữ an toàn, đồng thời đồng bộ hóa hiển thị ảnh mượt mà trên toàn bộ các trang giao diện (Danh sách nhân sự, Trang phân công, Lịch tuần, Dashboard).

### 2. Quản Lý Công Việc & Phân Công Lịch Làm Việc Thông Minh
* **Lịch phân công theo tuần trực quan:** Xây dựng ma trận lịch làm việc theo tuần linh hoạt với 3 ca chi tiết (Ca Sáng, Ca Chiều, Ca Tối) từ Thứ Hai đến Chủ Nhật.
* **Thao tác tương tác nhanh:** Cho phép người dùng nhấp trực tiếp vào các ô ca trống trên lịch tuần để mở hộp thoại Modal chọn công việc và đăng ký phân công tức thì.
* **Thuật toán Phân công Tự động:** Tích hợp tính năng tự động phân công ngẫu nhiên thông minh, hệ thống sẽ tự động quét các ca làm việc còn trống trong tuần và điền công việc một cách cân đối, tiết kiệm tối đa thời gian cho nhà quản lý.
* **Nhận diện và Đánh dấu Tăng ca (Overtime):** Hệ thống tự động nhận diện thời gian làm việc vào ban đêm (Ca Tối) hoặc vào các ngày cuối tuần (Thứ Bảy, Chủ Nhật) để tự động đánh dấu cờ tăng ca, áp dụng hệ số nhân lương tiêu chuẩn (`x1.5`).

### 3. Tích Hợp Xử Lý File Excel Linh Hoạt
* **Nạp lịch phân công từ file Excel:** Cho phép quản trị viên tải lên file bảng tính Excel (`.xlsx`, `.xls`) chứa danh sách phân công; hệ thống sẽ tự động đọc cấu trúc ngày tháng, ca làm việc, công việc và tên nhân viên để đồng bộ dữ liệu vào cơ sở dữ liệu tuần tương ứng.
* **Xuất báo cáo dữ liệu:** Hỗ trợ tính năng xuất lịch phân công tuần ra file Excel phục vụ cho việc lưu trữ và theo dõi báo cáo công việc định kỳ.

### 4. Hệ Thống Tính Lương Tự Động & Xuất Bảng Lương
* **Tổng hợp ngày công tự động:** Hệ thống tự động truy vấn và tổng hợp chính xác số lượng ca làm việc thường và ca tăng ca của từng nhân viên trong tháng hiện tại.
* **Tính toán thu nhập minh bạch:** Dựa trên mức lương cơ bản của từng công việc và hệ số tăng ca (`1.5`), hệ thống tự động tính ra tổng thu nhập tương ứng của nhân sự.
* **Xuất Bảng lương ra file Excel:** Cung cấp tính năng xuất báo cáo bảng lương chi tiết ra file Excel (`.xlsx`) một cách nhanh chóng, hỗ trợ tối đa cho bộ phận kế toán trong việc chi trả lương.

### 5. Giao Diện Dashboard Thống Kê Tổng Quan
* Trang chủ Dashboard hiển thị các thẻ thống kê tổng quan trực quan bao gồm: **Tổng số nhân sự**, **Tổng số danh mục công việc** và **Tổng số ca phân công trong tuần hiện tại**.
* Tích hợp bảng lịch tuần ngay tại trang chủ giúp nhà quản lý có cái nhìn tổng quát và thao tác nhanh chóng ngay khi đăng nhập vào hệ thống.

---

## 🛠️ Công Nghệ & Thư Viện Sử Dụng

* **Ngôn ngữ lập trình chính:** Python 3.x
* **Web Framework:** Flask (áp dụng mô hình cấu trúc Blueprint hiện đại)
* **Thư viện Cơ sở dữ liệu:** Flask-SQLAlchemy (ORM quản lý dữ liệu), Flask-Migrate (Quản lý phiên bản Database)
* **Giao diện Frontend:** HTML5, CSS3, Bootstrap 5 (Framework giao diện chính), Bootstrap Icons, JavaScript (Vanilla JS xử lý các sự kiện Modal và giao diện động)
* **Thư viện Xử lý Dữ liệu & Bảng tính:** Pandas, Openpyxl (Chuyên dụng cho việc đọc, ghi và xử lý file Excel)
* **Hệ quản trị cơ sở dữ liệu:** SQLite (Lưu trữ cục bộ cho môi trường phát triển và máy chủ PythonAnywhere)

---

## 📂 Cấu Trúc Tổng Thể Thư Mục Dự Án

```text
EmployeeTaskScheduler/
│
├── app/
│   ├── models/         # Định nghĩa các bảng dữ liệu mô hình (Employee, Task, Schedule)
│   ├── routes/         # Các Blueprint phân chia logic điều hướng (auth, employee, schedule, task, export)
│   ├── static/         # Thư mục chứa mã nguồn CSS, JS, hình ảnh và thư mục lưu trữ ảnh đại diện (uploads/avatars)
│   └── templates/      # Các tệp giao diện HTML giao tiếp với người dùng (Dashboard, Lịch tuần, Nhân sự, Lương...)
│
├── instance/           # Thư mục lưu trữ tệp cơ sở dữ liệu SQLite
├── config.py           # Tệp cấu hình chung của hệ thống Flask
├── requirements.txt    # Danh sách các gói thư viện Python cần thiết
└── run.py              # Tệp khởi chạy chính của toàn bộ ứng dụng
