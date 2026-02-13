"""Authentication constants."""

# JWT token types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# Audit log actions
AUDIT_ACTION_LOGIN = "login"
AUDIT_ACTION_LOGOUT = "logout"
AUDIT_ACTION_LOGIN_FAILED = "login_failed"

# Error messages
ERROR_INVALID_CREDENTIALS = "Tên đăng nhập hoặc mật khẩu không đúng"
ERROR_ACCOUNT_LOCKED = "Tài khoản bị khóa tạm thời, vui lòng thử lại sau 15 phút"
ERROR_ACCOUNT_INACTIVE = "Tài khoản đã bị vô hiệu hóa"
ERROR_INVALID_TOKEN = "Token không hợp lệ"
ERROR_USER_NOT_FOUND = "Không tìm thấy người dùng"
ERROR_USERNAME_EXISTS = "Username đã tồn tại"

# Success messages
SUCCESS_LOGIN = "Đăng nhập thành công"
SUCCESS_LOGOUT = "Đăng xuất thành công"
SUCCESS_REGISTER = "Đăng ký thành công"
