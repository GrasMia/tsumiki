import re
from fastapi import HTTPException, status

# 禁止字符 <>:"|?*\\/ 与 控制字符 \x00-\x1f 以及 空格 \s
FORBIDDEN_PATTERN = re.compile(r'[<>:"|?*\x00-\x1f]')
SPACE_PATTERN = re.compile(r"\s")

# Windows 保留文件名
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}

# 服务器保留名（文件/目录/用户名禁止）
SERVER_RESERVED_NAMES = {"profile"}

# 服务器保留用户名（仅用户名禁止）
SERVER_RESERVED_USERNAMES = {"auth", "users", "disk", "login", "register", "root"}


MIN_USERNAME_LENGTH = 5
MAX_USERNAME_LENGTH = 20
MAX_DFNAME_LENGTH = 50
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 50
MAX_DIR_PATH_LENGTH = 255


def _base_validation(name: str, name_type: str, max_len: int, allow_slash: bool = False) -> str:
    """基础校验（通用）"""
    if not name or not name.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{name_type}不能为空")

    if name_type == "用户名" and SPACE_PATTERN.search(name):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{name_type}不能包含空格")
    else:
        if name != name.strip():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{name_type}不能包含首尾空格")

    if len(name) > max_len:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{name_type}不能超过 {max_len} 个字符")

    if not allow_slash and ("/" in name or "\\" in name):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{name_type}不能包含 '/' 或 '\\' 字符")

    if "\\" in name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{name_type}不能包含 '\\' 字符")

    if FORBIDDEN_PATTERN.search(name):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{name_type}包含非法字符")

    if name.upper() in WINDOWS_RESERVED_NAMES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{name_type} '{name}' 是系统保留名称")

    return name


def validate_username(username: str) -> str:
    name = _base_validation(username, "用户名", max_len=MAX_USERNAME_LENGTH, allow_slash=False)

    if len(username) < MIN_USERNAME_LENGTH:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"用户名不能少于 {MIN_USERNAME_LENGTH} 个字符")

    if name in SERVER_RESERVED_NAMES or name in SERVER_RESERVED_USERNAMES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"用户名 '{name}' 是服务器保留名称")
    return name


def validate_password(password: str) -> str:
    if not password or not password.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "密码不能为空")

    if SPACE_PATTERN.search(password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "密码不能包含空格")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"密码长度不能少于 {MIN_PASSWORD_LENGTH} 位")

    if len(password) > MAX_PASSWORD_LENGTH:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"密码长度不能超过 {MAX_PASSWORD_LENGTH} 位")

    if FORBIDDEN_PATTERN.search(password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "密码包含非法字符")

    return password


def _validate_path_item(name: str, name_type: str, max_len: int, allow_dot_start: bool = False) -> str:
    name = _base_validation(name, name_type, max_len=max_len, allow_slash=False)

    if re.match(r"^\.+$", name):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{name_type}不能全为 '.'")

    if not allow_dot_start and name.startswith("."):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{name_type}不能以 '.' 开头")

    if name.endswith("."):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{name_type}不能以 '.' 结尾")

    if name in SERVER_RESERVED_NAMES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{name_type} '{name}' 是服务器保留名称")

    return name


def validate_dir_name(dir_name: str) -> str:
    return _validate_path_item(dir_name, "目录名", max_len=MAX_DFNAME_LENGTH, allow_dot_start=False)


def validate_file_name(file_name: str) -> str:
    return _validate_path_item(file_name, "文件名", max_len=MAX_DFNAME_LENGTH, allow_dot_start=False)


def validate_file_name_allow_hidden(file_name: str) -> str:
    return _validate_path_item(file_name, "文件名", max_len=MAX_DFNAME_LENGTH, allow_dot_start=True)


def validate_dir_path(dir_path: str) -> str:
    if not dir_path or not dir_path.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "目录路径不能为空")

    if "\\" in dir_path:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "目录路径不能包含 '\\' 字符")

    parts = dir_path.split("/")
    for part in parts:
        if part:
            _validate_path_item(part, "目录路径", max_len=MAX_DIR_PATH_LENGTH, allow_dot_start=False)

    return dir_path
