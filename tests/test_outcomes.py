"""Tests for synthetic outcome generation."""

from simulator.outcomes import generate_outcomes


def test_returns_the_requested_number_of_outcomes():
    outcomes = generate_outcomes(win_probability=0.5, count=100, seed=1)

    assert len(outcomes) == 100


def test_the_same_seed_produces_the_same_sequence():
    first = generate_outcomes(win_probability=0.5, count=50, seed=123)
    second = generate_outcomes(win_probability=0.5, count=50, seed=123)

    assert first == second


def test_different_seeds_produce_different_sequences():
    first = generate_outcomes(win_probability=0.5, count=50, seed=1)
    second = generate_outcomes(win_probability=0.5, count=50, seed=2)

    assert first != second


def test_a_zero_win_probability_never_wins():
    outcomes = generate_outcomes(win_probability=0.0, count=200, seed=1)

    assert not any(outcomes)


def test_a_certain_win_probability_always_wins():
    outcomes = generate_outcomes(win_probability=1.0, count=200, seed=1)

    assert all(outcomes)
