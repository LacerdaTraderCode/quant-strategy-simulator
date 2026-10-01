"""Domain math shared across strategies: Kelly sizing, break-even win rate, Fibonacci steps."""


def break_even_win_rate(payout_ratio: float) -> float:
    """The win rate at which `payout_ratio` breaks even on average.

    Below this win rate, every staking strategy loses money in expectation —
    money management changes the shape of the equity curve, not whether the
    underlying edge exists.
    """
    return 1 / (1 + payout_ratio)


def kelly_fraction(win_probability: float, payout_ratio: float) -> float:
    """Kelly-optimal fraction of bankroll to stake.

    `payout_ratio` is the profit per unit staked on a win — the `b` in the
    standard Kelly formula f* = p - q/b. A non-positive result means there is
    no edge at this win probability and payout: staking anything loses money
    on average, so the fraction is floored at zero instead of going short.
    """
    if payout_ratio <= 0:
        return 0.0
    loss_probability = 1 - win_probability
    fraction = win_probability - loss_probability / payout_ratio
    return max(0.0, fraction)


def fibonacci_sequence(length: int) -> list[int]:
    sequence = [1, 1]
    while len(sequence) < length:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:length]
