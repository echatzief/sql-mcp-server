from dataclasses import dataclass, field
from functools import partial
from typing import List, Optional
from src.lib.utils import get_conditional_required_env, get_required_env, get_env

@dataclass
class Config:
    # HTTP Client
    http_host: str = field(default_factory=partial(get_required_env, "HTTP_HOST"))
    http_port: str = field(default_factory=partial(get_required_env, "HTTP_PORT"))

    # Database
    db_provider: str = field(
        default_factory=partial(get_required_env, "DATABASE_PROVIDER")
    )
    db_host: str = field(default_factory=partial(get_required_env, "DATABASE_HOST"))
    db_port: str = field(default_factory=partial(get_required_env, "DATABASE_PORT"))
    db_user: str = field(default_factory=partial(get_required_env, "DATABASE_USER"))
    db_password: str = field(default_factory=partial(get_env, "DATABASE_PASSWORD"))
    db_name: str = field(default_factory=partial(get_required_env, "DATABASE_NAME"))
    db_min_pool_size: str = field(
        default_factory=partial(get_required_env, "DATABASE_MIN_POOL_SIZE")
    )
    db_max_pool_size: str = field(
        default_factory=partial(get_required_env, "DATABASE_MAX_POOL_SIZE")
    )

    # Execution Mode
    readonly: bool = field(default_factory=lambda: get_env("READ_ONLY_MODE", "true") == "true")
    
