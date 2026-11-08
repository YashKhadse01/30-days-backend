
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class Permission(str, Enum):
    PROFILE_READ = "profile:read"
    REPORTS_READ = "reports:read"
    REPORTS_CREATE = "reports:create"
    USERS_MANAGE = "users:manage"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),
    Role.USER: frozenset({
        Permission.PROFILE_READ,
        Permission.REPORTS_READ,
        Permission.REPORTS_CREATE,
    }),
    Role.VIEWER: frozenset({
        Permission.PROFILE_READ,
        Permission.REPORTS_READ,
    }),
}


def has_permission(
    role: Role | str,
    permission: Permission | str,
) -> bool:
    """Return True only for explicitly granted permissions."""
    try:
        validated_role = Role(role)
        validated_permission = Permission(permission)
    except (ValueError, TypeError):
        return False

    return validated_permission in ROLE_PERMISSIONS[validated_role]


def require_permission(
    role: Role | str,
    permission: Permission | str,
) -> None:
    """Reject users without the required permission."""
    if not has_permission(role, permission):
        raise PermissionError("Access denied")
