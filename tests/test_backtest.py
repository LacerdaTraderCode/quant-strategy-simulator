"""Tests for the backtest engine: bankroll tracking, drawdown, and ruin."""

from simulator.backtest import run_backtest
from simulator.strategies import FixedStakeStrategy, MartingaleStrategy


def test_a_winning_streak_grows_the_bankroll_by_the_payout_ratio():
    result = run_backtest(
        FixedStakeStrategy(),
        outcomes=[True, True, True],
        starting_bankroll=1000,
        base_unit=10,
        payout_ratio=0.8,
    )

    assert result.ending_bankroll == 1000 + 3 * (10 * 0.8)
    assert result.ruined is False


def test_a_losing_streak_shrinks_the_bankroll_by_the_stake():
    result = run_backtest(
        FixedStakeStrategy(),
        outcomes=[False, False, False],
        starting_bankroll=1000,
        base_unit=10,
        payout_ratio=0.8,
    )

    assert result.ending_bankroll == 1000 - 30


def test_max_drawdown_reflects_the_deepest_dip_from_a_prior_peak():
    # Win, then lose twice: the peak is set after the win, and the drawdown
    # is measured from that peak, not from the starting bankroll.
    result = run_backtest(
        FixedStakeStrategy(),
        outcomes=[True, False, False],
        starting_bankroll=1000,
        base_unit=100,
        payout_ratio=1.0,
    )

    peak = 1100
    trough = 1100 - 100 - 100
    expected_drawdown = (peak - trough) / peak
    assert round(result.max_drawdown, 6) == round(expected_drawdown, 6)


def test_a_strategy_that_outgrows_the_bankroll_is_marked_ruined():
    result = run_backtest(
        MartingaleStrategy(multiplier=2.0),
        outcomes=[False] * 10,
        starting_bankroll=100,
        base_unit=10,
        payout_ratio=0.85,
    )

    assert result.ruined is True
    assert result.ending_bankroll <= 0


def test_history_records_one_point_per_trade_actually_played():
    result = run_backtest(
        FixedStakeStrategy(),
        outcomes=[True, False, True],
        starting_bankroll=1000,
        base_unit=10,
        payout_ratio=0.8,
    )

    assert len(result.history) == 3
    assert [point.trade_index for point in result.history] == [0, 1, 2]


def test_the_strategy_name_is_carried_into_the_result():
    result = run_backtest(
        FixedStakeStrategy(), outcomes=[True], starting_bankroll=1000, base_unit=10, payout_ratio=0.8
    )

    assert result.strategy_name == "fixed"
