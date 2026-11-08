
import pytest

from auth_2fa_rbac.backup_codes import (
    generate_backup_codes,
    hash_backup_code,
    redeem_backup_code,
)


def test_generates_ten_backup_codes():
    codes, hashes = generate_backup_codes()

    assert len(codes) == 10
    assert len(hashes) == 10
    assert len(set(codes)) == 10


def test_backup_codes_are_hashed():
    codes, hashes = generate_backup_codes()

    for code in codes:
        assert code not in hashes
        assert hash_backup_code(code) in hashes


def test_first_redemption_succeeds():
    codes, hashes = generate_backup_codes()

    assert redeem_backup_code(codes[0], hashes) is True
    assert len(hashes) == 9


def test_reuse_is_rejected():
    codes, hashes = generate_backup_codes()

    assert redeem_backup_code(codes[0], hashes) is True
    assert redeem_backup_code(codes[0], hashes) is False


def test_invalid_code_rejected():
    _, hashes = generate_backup_codes()

    assert redeem_backup_code(
        "INVALID-RECOVERY-CODE", hashes
    ) is False


def test_other_codes_remain_valid():
    codes, hashes = generate_backup_codes()

    assert redeem_backup_code(codes[0], hashes)
    assert redeem_backup_code(codes[1], hashes)


def test_hash_normalization():
    code = "ABCD1234EF567890"

    assert hash_backup_code(code) == hash_backup_code(
        "abcd-1234-ef56-7890"
    )


@pytest.mark.parametrize("count", [0, -1, -10])
def test_invalid_code_count_rejected(count):
    with pytest.raises(ValueError):
        generate_backup_codes(count)


def test_redeeming_code_removes_only_one_hash():
    codes, hashes = generate_backup_codes()

    original = hashes.copy()

    assert redeem_backup_code(codes[0], hashes)

    assert len(original - hashes) == 1
