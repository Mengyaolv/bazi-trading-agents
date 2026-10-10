#!/usr/bin/env python3
"""Checks for local web authentication helpers."""

import tempfile
import os
from pathlib import Path

from utils.auth import authenticate_user, is_admin, register_user, user_count


def test_register_login_and_roles():
    with tempfile.TemporaryDirectory() as tmpdir:
        users_file = str(Path(tmpdir) / "users.json")
        assert user_count(users_file) == 0

        os.environ["INITIAL_ADMIN_TOKEN"] = "test-only-admin-token"
        admin = register_user("admin_user", "password123", users_file, admin_token="test-only-admin-token")
        assert admin["username"] == "admin_user"
        assert is_admin(admin)
        assert "password_hash" not in admin

        user = register_user("普通用户", "password456", users_file)
        assert user["role"] == "user"
        assert not is_admin(user)
        assert user_count(users_file) == 2

        with tempfile.TemporaryDirectory() as other_dir:
            regular = register_user("first_user", "password123", str(Path(other_dir) / "users.json"))
            assert not is_admin(regular)

        logged_in = authenticate_user("admin_user", "password123", users_file)
        assert logged_in["user_id"] == admin["user_id"]

        try:
            authenticate_user("admin_user", "wrong-password", users_file)
        except ValueError:
            pass
        else:
            raise AssertionError("wrong password should fail")


if __name__ == "__main__":
    test_register_login_and_roles()
    print("auth checks OK")
