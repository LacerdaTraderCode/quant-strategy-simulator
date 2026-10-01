"""Classic money-management strategies, generalized as stateful staking rules.

Every strategy answers the same two questions on every trade: how much to
stake next, and how the outcome changes what gets staked after that. None of
them create an edge — see `math_utils.break_even_win_rate` — they only change
how quickly a bankroll grows or ruins at a given edge.
"""

from abc import ABC, abstractmethod

from simulator.math_utils import fibonacci_sequence, kelly_fraction


class Strategy(ABC):
    name: str

    @abstractmethod
    def reset(self, base_unit: float) -> None:
        """Prepare the strategy for a fresh backtest, betting `base_unit` per unit stake."""

    @abstractmethod
    def next_stake(self, bankroll: float) -> float:
        """Return the stake to risk on the next trade."""

    @abstractmethod
    def record_outcome(self, won: bool) -> None:
        """Update internal state after a trade resolves."""


class FixedStakeStrategy(Strategy):
    """Stakes the same amount every trade, regardless of streaks."""

    name = "fixed"

    def reset(self, base_unit: float) -> None:
        self._stake = base_unit

    def next_stake(self, bankroll: float) -> float:
        return self._stake

    def record_outcome(self, won: bool) -> None:
        pass


class MartingaleStrategy(Strategy):
    """Multiplies the stake after every loss and resets to base after a win."""

    name = "martingale"

    def __init__(self, multiplier: float = 2.0):
        self._multiplier = multiplier

    def reset(self, base_unit: float) -> None:
        self._base_unit = base_unit
        self._stake = base_unit

    def next_stake(self, bankroll: float) -> float:
        return self._stake

    def record_outcome(self, won: bool) -> None:
        self._stake = self._base_unit if won else self._stake * self._multiplier


class DAlembertStrategy(Strategy):
    """Adds one unit after a loss and removes one unit after a win, floored at the base unit."""

    name = "dalembert"

    def reset(self, base_unit: float) -> None:
        self._base_unit = base_unit
        self._stake = base_unit

    def next_stake(self, bankroll: float) -> float:
        return self._stake

    def record_outcome(self, won: bool) -> None:
        if won:
            self._stake = max(self._base_unit, self._stake - self._base_unit)
        else:
            self._stake = self._stake + self._base_unit


class FibonacciStrategy(Strategy):
    """Steps forward in the Fibonacci sequence after a loss, back two steps after a win."""

    name = "fibonacci"

    def __init__(self, sequence_length: int = 25):
        self._sequence_length = sequence_length

    def reset(self, base_unit: float) -> None:
        self._base_unit = base_unit
        self._sequence = fibonacci_sequence(self._sequence_length)
        self._position = 0

    def next_stake(self, bankroll: float) -> float:
        return self._base_unit * self._sequence[self._position]

    def record_outcome(self, won: bool) -> None:
        if won:
            self._position = max(0, self._position - 2)
        else:
            self._position = min(len(self._sequence) - 1, self._position + 1)


class KellyCriterionStrategy(Strategy):
    """Stakes a fixed fraction of the *current* bankroll, sized by the Kelly criterion.

    Unlike the other strategies, Kelly needs to know the true win probability
    and payout ratio up front — it is a statement about the edge, not a
    reaction to recent streaks the way Martingale or Fibonacci are.
    """

    name = "kelly"

    def __init__(self, win_probability: float, payout_ratio: float):
        self._fraction = kelly_fraction(win_probability, payout_ratio)

    def reset(self, base_unit: float) -> None:
        pass

    def next_stake(self, bankroll: float) -> float:
        return bankroll * self._fraction

    def record_outcome(self, won: bool) -> None:
        pass
