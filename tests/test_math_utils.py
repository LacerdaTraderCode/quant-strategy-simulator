"""Tests for the shared betting math."""

from simulator.math_utils import break_even_win_rate, fibonacci_sequence, kelly_fraction


def test_break_even_win_rate_for_a_typical_binary_option_payout():
    assert round(break_even_win_rate(0.85), 4) == round(1 / 1.85, 4)


def test_break_even_win_rate_is_half_at_even_money():
    assert break_even_win_rate(1.0) == 0.5


def test_kelly_fraction_is_zero_when_there_is_no_edge():
    # At exactly the break-even win rate, the edge is zero.
    payout_ratio = 0.85
    win_probability = break_even_win_rate(payout_ratio)

    assert round(kelly_fraction(win_probability, payout_ratio), 6) == 0.0


def test_kelly_fraction_is_positive_when_the_win_rate_beats_break_even():
    assert kelly_fraction(0.6, 0.85) > 0


def test_kelly_fraction_is_floored_at_zero_below_break_even():
    assert kelly_fraction(0.3, 0.85) == 0.0


def test_kelly_fraction_handles_a_non_positive_payout_ratio():
    assert kelly_fraction(0.6, 0.0) == 0.0


def test_fibonacci_sequence_starts_with_two_ones():
    assert fibonacci_sequence(5) == [1, 1, 2, 3, 5]


def test_fibonacci_sequence_respects_the_requested_length():
    assert len(fibonacci_sequence(10)) == 10
