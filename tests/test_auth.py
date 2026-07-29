"""
Tests for authentication: login, legacy password upgrade and registration.
"""

import bcrypt
import pytest

from src.services.auth_service import AuthService, hash_password, validate_registration


@pytest.fixture
def auth(context):
    return AuthService(context)


class TestAuthenticate:
    def test_default_admin_can_log_in(self, auth):
        assert auth.authenticate('admin', 'admin') == 'admin'

    def test_wrong_password_rejected(self, auth):
        assert auth.authenticate('admin', 'wrong-password') is None

    def test_unknown_user_rejected(self, auth):
        assert auth.authenticate('khong-ton-tai', 'admin') is None

    @pytest.mark.parametrize("username,password", [
        ('', 'admin'), ('admin', ''), ('', ''), (None, None),
    ])
    def test_blank_credentials_rejected(self, auth, username, password):
        assert auth.authenticate(username, password) is None

    def test_password_is_stored_hashed_not_plain(self, auth, db):
        db.execute("SELECT staff_psw FROM staff WHERE staff_id = 'admin'")
        stored = db.fetchone()[0]
        assert stored != 'admin'
        assert stored.startswith('$2')


class TestLegacyPasswordUpgrade:
    def test_plain_text_password_accepted_and_upgraded(self, auth, db):
        """Pre-hashing accounts must still work, then be migrated to bcrypt."""
        db.execute(
            "INSERT INTO staff (staff_id, staff_psw, staff_name) VALUES (%s, %s, %s)",
            ('legacy', 'plaintext123', 'Nhân viên cũ')
        )
        db.commit()

        assert auth.authenticate('legacy', 'plaintext123') == 'legacy'

        db.execute("SELECT staff_psw FROM staff WHERE staff_id = 'legacy'")
        stored = db.fetchone()[0]
        assert stored != 'plaintext123'
        assert bcrypt.checkpw(b'plaintext123', stored.encode())

    def test_upgraded_password_still_works_next_login(self, auth, db):
        db.execute(
            "INSERT INTO staff (staff_id, staff_psw, staff_name) VALUES (%s, %s, %s)",
            ('legacy2', 'secret', 'Nhân viên cũ 2')
        )
        db.commit()

        assert auth.authenticate('legacy2', 'secret') == 'legacy2'
        assert auth.authenticate('legacy2', 'secret') == 'legacy2'

    def test_wrong_plain_text_password_rejected(self, auth, db):
        db.execute(
            "INSERT INTO staff (staff_id, staff_psw, staff_name) VALUES (%s, %s, %s)",
            ('legacy3', 'secret', 'Nhân viên cũ 3')
        )
        db.commit()

        assert auth.authenticate('legacy3', 'not-secret') is None


class TestRegistration:
    def test_registers_and_can_log_in(self, auth):
        ok, _ = auth.register('nv001', 'matkhau123', 'Trần Văn B',
                              '0912345678', 'b@example.com')
        assert ok
        assert auth.authenticate('nv001', 'matkhau123') == 'nv001'

    def test_duplicate_staff_id_rejected(self, auth):
        auth.register('nv002', 'matkhau123', 'Nhân viên')
        ok, message = auth.register('nv002', 'matkhau456', 'Người khác')
        assert not ok
        assert 'đã tồn tại' in message

    def test_new_account_defaults_to_staff_position(self, auth, db):
        auth.register('nv003', 'matkhau123', 'Nhân viên')
        db.execute("SELECT staff_position FROM staff WHERE staff_id = 'nv003'")
        assert db.fetchone()[0] == 'staff'


class TestRegistrationValidation:
    @pytest.mark.parametrize("args", [
        ('', 'matkhau123', 'Tên'),           # missing id
        ('ab', 'matkhau123', 'Tên'),         # id too short
        ('nv001', '', 'Tên'),                # missing password
        ('nv001', '12345', 'Tên'),           # password too short
        ('nv001', 'matkhau123', ''),         # missing name
    ])
    def test_rejects_invalid_input(self, args):
        ok, message = validate_registration(*args)
        assert not ok
        assert message

    def test_rejects_bad_phone(self):
        ok, _ = validate_registration('nv001', 'matkhau123', 'Tên', phone='123')
        assert not ok

    def test_rejects_bad_email(self):
        ok, _ = validate_registration('nv001', 'matkhau123', 'Tên',
                                      email='not-an-email')
        assert not ok

    def test_accepts_valid_input(self):
        ok, message = validate_registration('nv001', 'matkhau123', 'Trần Văn B',
                                            '0912345678', 'b@example.com')
        assert ok
        assert message == ""

    def test_optional_fields_may_be_empty(self):
        ok, _ = validate_registration('nv001', 'matkhau123', 'Trần Văn B')
        assert ok


class TestHashPassword:
    def test_hash_is_verifiable(self):
        assert bcrypt.checkpw(b'matkhau', hash_password('matkhau').encode())

    def test_hashes_are_salted(self):
        assert hash_password('matkhau') != hash_password('matkhau')
