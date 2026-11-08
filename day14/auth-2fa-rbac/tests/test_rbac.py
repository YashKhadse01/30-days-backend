
import pytest

from auth_2fa_rbac.rbac import (
    Role,
    Permission,
    ROLE_PERMISSIONS,
    has_permission,
    require_permission,
)


@pytest.mark.parametrize(
    ("role", "permission", "expected"),
    [
        (Role.ADMIN, Permission.PROFILE_READ, True),
        (Role.ADMIN, Permission.REPORTS_READ, True),
        (Role.ADMIN, Permission.REPORTS_CREATE, True),
        (Role.ADMIN, Permission.USERS_MANAGE, True),
        (Role.USER, Permission.PROFILE_READ, True),
        (Role.USER, Permission.REPORTS_READ, True),
        (Role.USER, Permission.REPORTS_CREATE, True),
        (Role.USER, Permission.USERS_MANAGE, False),
        (Role.VIEWER, Permission.PROFILE_READ, True),
        (Role.VIEWER, Permission.REPORTS_READ, True),
        (Role.VIEWER, Permission.REPORTS_CREATE, False),
        (Role.VIEWER, Permission.USERS_MANAGE, False),
    ],
)
def test_role_permission_matrix(role, permission, expected):
    assert has_permission(role, permission) is expected


def test_unknown_role_rejected():
    assert has_permission(
        "hacker", Permission.USERS_MANAGE
    ) is False


def test_unknown_permission_rejected():
    assert has_permission(
        Role.ADMIN, "system:destroy"
    ) is False


def test_string_roles_supported():
    assert has_permission(
        "admin", "users:manage"
    ) is True


def test_permission_granted():
    require_permission(
        Role.ADMIN, Permission.USERS_MANAGE
    )


def test_permission_denied():
    with pytest.raises(PermissionError, match="Access denied"):
        require_permission(
            Role.VIEWER, Permission.USERS_MANAGE
        )


def test_admin_has_every_permission():
    assert ROLE_PERMISSIONS[Role.ADMIN] == frozenset(Permission)


def test_user_cannot_manage_users():
    assert not has_permission(
        Role.USER, Permission.USERS_MANAGE
    )


def test_viewer_has_read_only_permissions():
    assert ROLE_PERMISSIONS[Role.VIEWER] == frozenset({
        Permission.PROFILE_READ,
        Permission.REPORTS_READ,
    })
