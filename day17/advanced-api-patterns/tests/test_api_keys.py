
import pytest

from advanced_api.api_keys import APIKeyManager


@pytest.fixture
def manager():
    return APIKeyManager()


def test_create_api_key(manager):
    raw_key, record = manager.create_key(
        "payment-service",
        {"read:items"},
    )

    assert raw_key.startswith("ak_")
    assert record.client_name == "payment-service"
    assert record.revoked is False


def test_only_hash_is_stored(manager):
    raw_key, record = manager.create_key(
        "inventory-service",
        {"read:items"},
    )

    assert record.key_hash != raw_key
    assert record.key_hash == manager.hash_key(raw_key)
    assert raw_key not in record.__dict__.values()


def test_valid_api_key_authenticates(manager):
    raw_key, record = manager.create_key(
        "reporting-service",
        {"read:items"},
    )

    authenticated = manager.authenticate(raw_key)

    assert authenticated is record


def test_invalid_api_key_rejected(manager):
    manager.create_key(
        "payment-service",
        {"read:items"},
    )

    assert manager.authenticate("invalid-api-key") is None


def test_allowed_scope(manager):
    raw_key, record = manager.create_key(
        "inventory-service",
        {"read:items", "write:items"},
    )

    result = manager.authenticate(
        raw_key,
        required_scope="write:items",
    )

    assert result is record


def test_missing_scope_rejected(manager):
    raw_key, _ = manager.create_key(
        "reporting-service",
        {"read:items"},
    )

    assert manager.authenticate(
        raw_key,
        required_scope="write:items",
    ) is None


def test_revoke_api_key(manager):
    raw_key, record = manager.create_key(
        "payment-service",
        {"read:items"},
    )

    assert manager.revoke_key(record.key_id) is True
    assert manager.authenticate(raw_key) is None


def test_revoke_unknown_key(manager):
    assert manager.revoke_key("unknown-key") is False


def test_rotate_api_key(manager):
    old_key, old_record = manager.create_key(
        "payment-service",
        {"read:items", "write:items"},
    )

    new_key, new_record = manager.rotate_key(
        old_record.key_id
    )

    assert old_record.revoked is True
    assert manager.authenticate(old_key) is None
    assert manager.authenticate(new_key) is new_record
    assert new_key != old_key
    assert new_record.scopes == old_record.scopes


def test_rotate_revoked_key_rejected(manager):
    _, record = manager.create_key(
        "payment-service",
        {"read:items"},
    )

    manager.revoke_key(record.key_id)

    with pytest.raises(ValueError):
        manager.rotate_key(record.key_id)


def test_empty_client_name_rejected(manager):
    with pytest.raises(ValueError):
        manager.create_key(
            "   ",
            {"read:items"},
        )


def test_empty_scopes_rejected(manager):
    with pytest.raises(ValueError):
        manager.create_key(
            "payment-service",
            set(),
        )


def test_generated_keys_are_unique(manager):
    first_key, _ = manager.create_key(
        "payment-service",
        {"read:items"},
    )

    second_key, _ = manager.create_key(
        "payment-service",
        {"read:items"},
    )

    assert first_key != second_key
