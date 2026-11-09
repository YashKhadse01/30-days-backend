
import time

import pytest

from oauth_by_hand.pkce import (
    generate_code_verifier,
    generate_code_challenge,
    verify_code_challenge,
)
from oauth_by_hand.oauth_state import (
    create_oauth_state,
    consume_oauth_state,
    pending_states,
    STATE_TTL_SECONDS,
)


@pytest.fixture(autouse=True)
def clear_states():
    pending_states.clear()
    yield
    pending_states.clear()


def test_pkce_verifier_length():
    verifier = generate_code_verifier()
    assert len(verifier) == 43


def test_pkce_verifier_unique():
    first = generate_code_verifier()
    second = generate_code_verifier()
    assert first != second


def test_pkce_challenge_length():
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)
    assert len(challenge) == 43


def test_pkce_correct_verifier():
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)
    assert verify_code_challenge(verifier, challenge)


def test_pkce_wrong_verifier():
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)
    assert not verify_code_challenge(
        generate_code_verifier(),
        challenge,
    )


def test_state_created():
    state = create_oauth_state(generate_code_verifier())
    assert len(state) == 43


def test_state_returns_verifier():
    verifier = generate_code_verifier()
    state = create_oauth_state(verifier)
    assert consume_oauth_state(state) == verifier


def test_state_replay_rejected():
    state = create_oauth_state(generate_code_verifier())
    assert consume_oauth_state(state) is not None
    assert consume_oauth_state(state) is None


def test_unknown_state_rejected():
    assert consume_oauth_state("unknown") is None


def test_expired_state_rejected():
    state = create_oauth_state(generate_code_verifier())
    pending_states[state].expires_at = time.time() - 1
    assert consume_oauth_state(state) is None


def test_empty_verifier_rejected():
    with pytest.raises(ValueError):
        create_oauth_state("")


def test_empty_state_rejected():
    assert consume_oauth_state("") is None
