
import pytest

from advanced_api.etags import ETagManager


@pytest.fixture
def manager():
    return ETagManager()


@pytest.fixture
def item():
    return {
        "id": 1,
        "name": "Laptop",
        "price": 45000,
    }


def test_generate_etag(manager, item):
    etag = manager.generate(item)

    assert isinstance(etag, str)
    assert etag.startswith('"')
    assert etag.endswith('"')
    assert len(etag) == 66


def test_same_data_generates_same_etag(manager, item):
    first = manager.generate(item)
    second = manager.generate(item)

    assert first == second


def test_different_data_generates_different_etag(manager, item):
    original = manager.generate(item)

    updated = manager.generate({
        **item,
        "price": 50000,
    })

    assert original != updated


def test_dictionary_order_does_not_affect_etag(manager):
    first = manager.generate({
        "name": "Laptop",
        "price": 45000,
    })

    second = manager.generate({
        "price": 45000,
        "name": "Laptop",
    })

    assert first == second


def test_valid_etag_matches(manager, item):
    etag = manager.generate(item)

    assert manager.matches(etag, etag) is True


def test_invalid_etag_does_not_match(manager, item):
    etag = manager.generate(item)

    assert manager.matches(
        etag,
        '"different-etag"',
    ) is False


def test_missing_etag_does_not_match(manager, item):
    etag = manager.generate(item)

    assert manager.matches(etag, None) is False


def test_not_modified_when_etag_matches(manager, item):
    etag = manager.generate(item)

    assert manager.is_not_modified(
        item,
        etag,
    ) is True


def test_modified_when_etag_differs(manager, item):
    assert manager.is_not_modified(
        item,
        '"old-etag"',
    ) is False


def test_update_allowed_with_correct_etag(manager, item):
    etag = manager.generate(item)

    assert manager.can_update(
        item,
        etag,
    ) is True


def test_update_rejected_with_stale_etag(manager, item):
    assert manager.can_update(
        item,
        '"stale-etag"',
    ) is False


def test_update_rejected_without_etag(manager, item):
    assert manager.can_update(
        item,
        None,
    ) is False


def test_unicode_data_supported(manager):
    etag = manager.generate({
        "name": "नमस्ते",
    })

    assert etag.startswith('"')
    assert etag.endswith('"')


def test_nested_data_supported(manager):
    data = {
        "item": {
            "id": 1,
            "name": "Laptop",
        },
        "tags": ["electronics", "office"],
    }

    assert manager.generate(data) == manager.generate(data)
