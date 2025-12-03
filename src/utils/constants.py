"""
Application constants
"""

# Staff Positions
POSITION_ADMIN = 'admin'
POSITION_MANAGER = 'manager'
POSITION_STAFF = 'staff'

STAFF_POSITIONS = [
    POSITION_ADMIN,
    POSITION_MANAGER,
    POSITION_STAFF
]

# Payment Status
PAYMENT_STATUS_PENDING = 'pending'
PAYMENT_STATUS_PAID = 'paid'
PAYMENT_STATUS_CANCELLED = 'cancelled'

PAYMENT_STATUSES = [
    PAYMENT_STATUS_PENDING,
    PAYMENT_STATUS_PAID,
    PAYMENT_STATUS_CANCELLED
]

# Date Formats
DATE_FORMAT_DISPLAY = "%d/%m/%Y"
DATE_FORMAT_DATABASE = "%Y-%m-%d"
DATETIME_FORMAT_DISPLAY = "%d/%m/%Y %H:%M:%S"
DATETIME_FORMAT_DATABASE = "%Y-%m-%d %H:%M:%S"

# Expiry Warning Days
EXPIRY_WARNING_DAYS = 60  # Warn when medicine expires within 60 days

# Table Column Names (for consistency)
TABLE_HEADERS = {
    'medicine': ['ID', 'Tên thuốc', 'Hoạt chất', 'Thương hiệu', 'NCC', 'Danh mục', 'Giá nhập', 'Giá bán', 'Tồn kho', 'Đơn vị', 'Hạn dùng', 'Số lô'],
    'supplier': ['ID', 'Tên NCC', 'Người liên hệ', 'Số điện thoại', 'Email', 'Địa chỉ', 'Điều khoản thanh toán'],
    'customer': ['ID', 'Tên khách hàng', 'Số điện thoại', 'Email'],
    'staff': ['ID', 'Họ tên', 'Chức vụ', 'Số điện thoại', 'Email', 'Lương', 'Ngày vào làm'],
    'invoice': ['ID', 'Ngày tạo', 'Khách hàng', 'Nhân viên', 'Tổng tiền', 'Trạng thái', 'Hạn thanh toán'],
    'stock': ['ID', 'Thuốc', 'NCC', 'Số lượng', 'Ngày nhập'],
    'activity_log': ['ID', 'Nhân viên', 'Hành động', 'Thời gian']
}

# Report Types
REPORT_TYPE_STOCK = 'stock'
REPORT_TYPE_INVOICE = 'invoice'
REPORT_TYPE_EXPIRY = 'expiry'

# UI Messages
MSG_SUCCESS_SAVE = "Lưu thành công!"
MSG_SUCCESS_DELETE = "Xóa thành công!"
MSG_SUCCESS_UPDATE = "Cập nhật thành công!"
MSG_ERROR_SAVE = "Lỗi khi lưu dữ liệu!"
MSG_ERROR_DELETE = "Lỗi khi xóa dữ liệu!"
MSG_ERROR_UPDATE = "Lỗi khi cập nhật dữ liệu!"
MSG_ERROR_CONNECTION = "Không thể kết nối database!"
MSG_ERROR_VALIDATION = "Vui lòng kiểm tra lại thông tin!"
MSG_CONFIRM_DELETE = "Bạn có chắc muốn xóa?"
MSG_LOGIN_SUCCESS = "Đăng nhập thành công!"
MSG_LOGIN_FAILED = "Sai tên đăng nhập hoặc mật khẩu!"
MSG_LOGOUT = "Đăng xuất thành công!"

# Permissions (future feature)
PERM_VIEW_MEDICINE = 'view_medicine'
PERM_EDIT_MEDICINE = 'edit_medicine'
PERM_VIEW_INVOICE = 'view_invoice'
PERM_CREATE_INVOICE = 'create_invoice'
PERM_VIEW_STAFF = 'view_staff'
PERM_MANAGE_STAFF = 'manage_staff'
PERM_VIEW_REPORTS = 'view_reports'
PERM_MANAGE_SETTINGS = 'manage_settings'
