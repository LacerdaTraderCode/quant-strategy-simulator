"""Tests for each staking strategy's behavior in isolation, independent of the backtest engine."""

from simulator.strategies import (
    DAlembertStrategy,
    FibonacciStrategy,
    FixedStakeStrategy,
    KellyCriterionStrategy,
    MartingaleStrategy,
)


def test_fixed_stake_never_changes():
    strategy = FixedStakeStrategy()
    strategy.reset(base_unit=10)

    for won in [True, False, False, True]:
        assert strategy.next_stake(bankroll=1000) == 10
        strategy.record_outcome(won)


def test_martingale_doubles_after_a_loss_and_resets_after_a_win():
    strategy = MartingaleStrategy(multiplier=2.0)
    strategy.reset(base_unit=10)

    assert strategy.next_stake(bankroll=1000) == 10
    strategy.record_outcome(False)
    assert strategy.next_stake(bankroll=1000) == 20
    strategy.record_outcome(False)
    assert strategy.next_stake(bankroll=1000) == 40
    strategy.record_outcome(True)
    assert strategy.next_stake(bankroll=1000) == 10


def test_dalembert_adds_a_unit_after_a_loss_and_removes_one_after_a_win():
    strategy = DAlembertStrategy()
    strategy.reset(base_unit=10)

    strategy.record_outcome(False)
    assert strategy.next_stake(bankroll=1000) == 20
    strategy.record_outcome(False)
    assert strategy.next_stake(bankroll=1000) == 30
    strategy.record_outcome(True)
    assert strategy.next_stake(bankroll=1000) == 20


def test_dalembert_never_drops_below_the_base_unit():
    strategy = DAlembertStrategy()
    strategy.reset(base_unit=10)

    strategy.record_outcome(True)
    assert strategy.next_stake(bankroll=1000) == 10


def test_fibonacci_advances_one_step_on_a_loss():
    strategy = FibonacciStrategy()
    strategy.reset(base_unit=10)

    assert strategy.next_stake(bankroll=1000) == 10  # sequence[0] == 1
    strategy.record_outcome(False)
    assert strategy.next_stake(bankroll=1000) == 10  # sequence[1] == 1
    strategy.record_outcome(False)
    assert strategy.next_stake(bankroll=1000) == 20  # sequence[2] == 2


def test_fibonacci_retreats_two_steps_on_a_win_and_floors_at_the_start():
    strategy = FibonacciStrategy()
    strategy.reset(base_unit=10)

    for _ in range(4):
        strategy.record_outcome(False)  # advance to position 4 (sequence value 5)
    assert strategy.next_stake(bankroll=1000) == 50

    strategy.record_outcome(True)  # retreat two positions, to position 2 (value 2)
    assert strategy.next_stake(bankroll=1000) == 20

    strategy.record_outcome(True)
    strategy.record_outcome(True)
    strategy.record_outcome(True)
    assert strategy.next_stake(bankroll=1000) == 10  # floored at the first term


def test_kelly_stakes_a_fraction_of_the_current_bankroll_not_the_base_unit():
    strategy = KellyCriterionStrategy(win_probability=0.6, payout_ratio=0.85)
    strategy.reset(base_unit=10)

    assert strategy.next_stake(bankroll=1000) == strategy.next_stake(bankroll=1000)
    assert strategy.next_stake(bankroll=2000) == 2 * strategy.next_stake(bankroll=1000)


def test_kelly_stakes_nothing_when_there_is_no_edge():
    strategy = KellyCriterionStrategy(win_probability=0.3, payout_ratio=0.85)
    strategy.reset(base_unit=10)

    assert strategy.next_stake(bankroll=1000) == 0
