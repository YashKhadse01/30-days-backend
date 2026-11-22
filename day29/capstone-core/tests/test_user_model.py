import uuid

from sqlalchemy import inspect

from capstone_core.models.user import User


def test_user_table_name() -> None:
    assert User.__tablename__ == "users"


def test_user_primary_key() -> None:
    mapper = inspect(User)

    assert len(mapper.primary_key) == 1
    assert mapper.primary_key[0].name == "id"


def test_user_email_is_unique() -> None:
    email_column = User.__table__.columns["email"]

    assert email_column.unique is True
    assert email_column.nullable is False


def test_user_password_hash_optional_for_oauth() -> None:
    column = User.__table__.columns["password_hash"]

    assert column.nullable is True


def test_user_uuid_assignment() -> None:
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="test-hash",
    )

    assert isinstance(user.id, uuid.UUID)
    assert user.email == "test@example.com"
