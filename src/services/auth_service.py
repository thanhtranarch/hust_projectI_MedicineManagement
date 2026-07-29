"""
Authentication service - password hashing, verification and registration.

Kept out of the UI layer so the rules can be tested without a running Qt app.
"""

import bcrypt

MIN_PASSWORD_LENGTH = 6
MIN_STAFF_ID_LENGTH = 3


def hash_password(plain_password):
    """Hash a plain-text password with bcrypt."""
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


class AuthService:
    """Authenticates staff and creates new accounts."""

    def __init__(self, context):
        self.context = context
        self.db = context.db_manager

    def authenticate(self, username, password):
        """
        Check a username/password pair.

        Accounts created before password hashing was introduced still hold
        plain text; those are verified directly and transparently upgraded to
        a bcrypt hash on first successful login.

        Returns:
            str | None: the staff_id on success, None otherwise
        """
        if not username or not password:
            return None

        self.db.execute(
            "SELECT staff_id, staff_psw FROM staff WHERE staff_id = %s", (username,)
        )
        row = self.db.fetchone()
        if not row:
            return None

        staff_id, stored = row

        try:
            if bcrypt.checkpw(password.encode('utf-8'), stored.encode('utf-8')):
                return staff_id
        except (ValueError, AttributeError):
            # Not a bcrypt hash - fall through to the legacy plain-text check
            if password == stored:
                self._upgrade_password(staff_id, password)
                return staff_id

        return None

    def _upgrade_password(self, staff_id, plain_password):
        """Replace a legacy plain-text password with a bcrypt hash."""
        try:
            self.db.execute(
                "UPDATE staff SET staff_psw = %s WHERE staff_id = %s",
                (hash_password(plain_password), staff_id)
            )
            self.db.commit()
        except Exception as e:
            print(f"Failed to upgrade password for {staff_id}: {e}")

    def staff_id_exists(self, staff_id):
        """True when the staff ID is already taken."""
        self.db.execute("SELECT 1 FROM staff WHERE staff_id = %s", (staff_id,))
        return self.db.fetchone() is not None

    def register(self, staff_id, password, name, phone=None, email=None,
                 position='staff'):
        """
        Create a staff account.

        Returns:
            tuple: (success, message)
        """
        is_valid, error = validate_registration(staff_id, password, name, phone, email)
        if not is_valid:
            return False, error

        if self.staff_id_exists(staff_id):
            return False, "Mã nhân viên đã tồn tại, vui lòng chọn mã khác"

        try:
            self.db.execute(
                """INSERT INTO staff (staff_id, staff_psw, staff_name, staff_phone,
                                      staff_email, staff_position)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (staff_id, hash_password(password), name, phone, email, position)
            )
            self.db.commit()
            return True, "Đăng ký thành công"
        except Exception as e:
            self.db.rollback()
            return False, f"Đăng ký thất bại: {e}"


def validate_registration(staff_id, password, name, phone=None, email=None):
    """
    Validate registration input.

    Returns:
        tuple: (is_valid, error_message)
    """
    from src.utils.helpers import validate_email, validate_phone

    if not staff_id:
        return False, "Vui lòng nhập mã nhân viên"
    if len(staff_id) < MIN_STAFF_ID_LENGTH:
        return False, f"Mã nhân viên phải có ít nhất {MIN_STAFF_ID_LENGTH} ký tự"
    if not password:
        return False, "Vui lòng nhập mật khẩu"
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Mật khẩu phải có ít nhất {MIN_PASSWORD_LENGTH} ký tự"
    if not name:
        return False, "Vui lòng nhập họ tên"
    if phone and not validate_phone(phone):
        return False, "Số điện thoại không hợp lệ"
    if email and not validate_email(email):
        return False, "Email không hợp lệ"

    return True, ""
