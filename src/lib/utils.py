import os


def get_conditional_required_env(key: str, is_required: bool) -> str | None:
    value = os.environ.get(key)
    if not value and is_required:
        raise ValueError(f"Required environment variable '{key}' is not set or empty")
    return value


def get_required_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise ValueError(f"Required environment variable '{key}' is not set or empty")
    return value


def get_env(key: str, default="") -> str:
    return os.environ.get(key, default)
