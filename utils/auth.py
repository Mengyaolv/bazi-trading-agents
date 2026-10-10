"""Local authentication helpers for the Streamlit web UI."""

import hashlib
import hmac
import json
import os
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_USERS_FILE = "./data/users.json"
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_\-\u4e00-\u9fff]{2,32}$")
PBKDF2_ITERATIONS = 180_000


def get_users_file(path: str = "") -> Path:
    return Path(path or os.environ.get("AUTH_USERS_FILE") or DEFAULT_USERS_FILE)


def load_users(path: str = "") -> Dict[str, Any]:
    users_file = get_users_file(path)
    if not users_file.exists():
        return {"users": {}}
    try:
        payload = json.loads(users_file.read_text(encoding="utf-8"))
    except Exception:
        return {"users": {}}
    if not isinstance(payload, dict):
        return {"users": {}}
    users = payload.get("users")
    if not isinstance(users, dict):
        payload["users"] = {}
    return payload


def save_users(payload: Dict[str, Any], path: str = "") -> None:
    users_file = get_users_file(path)
    users_file.parent.mkdir(parents=True, exist_ok=True)
    users_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def register_user(username: str, password: str, path: str = "", admin_token: str = "") -> Dict[str, Any]:
    username = normalize_username(username)
    validate_username(username)
    validate_password(password)

    payload = load_users(path)
    users = payload.setdefault("users", {})
    key = username.lower()
    if key in users:
        raise ValueError("该用户名已存在")

    expected_token = os.environ.get("INITIAL_ADMIN_TOKEN", "")
    role = "user"
    if not users and expected_token and admin_token and hmac.compare_digest(admin_token, expected_token):
        role = "admin"
    salt = secrets.token_hex(16)
    users[key] = {
        "user_id": secrets.token_urlsafe(12),
        "username": username,
        "password_hash": hash_password(password, salt),
        "salt": salt,
        "role": role,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    save_users(payload, path)
    return public_user(users[key])


def authenticate_user(username: str, password: str, path: str = "") -> Dict[str, Any]:
    username = normalize_username(username)
    payload = load_users(path)
    record = payload.get("users", {}).get(username.lower())
    if not record:
        raise ValueError("用户名或密码错误")
    expected = record.get("password_hash", "")
    actual = hash_password(password, record.get("salt", ""))
    if not hmac.compare_digest(expected, actual):
        raise ValueError("用户名或密码错误")
    return public_user(record)


def public_user(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "user_id": record.get("user_id", ""),
        "username": record.get("username", ""),
        "role": record.get("role", "user"),
        "created_at": record.get("created_at", ""),
    }


def is_admin(user: Optional[Dict[str, Any]]) -> bool:
    return bool(user and user.get("role") == "admin")


def user_count(path: str = "") -> int:
    return len(load_users(path).get("users", {}))


def normalize_username(username: str) -> str:
    return str(username or "").strip()


def validate_username(username: str) -> None:
    if not USERNAME_PATTERN.match(username):
        raise ValueError("用户名需为 2-32 位中文、字母、数字、下划线或短横线")


def validate_password(password: str) -> None:
    if len(str(password or "")) < 8:
        raise ValueError("密码至少需要 8 位")


def hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        str(password).encode("utf-8"),
        str(salt).encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return digest.hex()
