"""CLI: runs many Monte Carlo backtests per strategy and prints a comparison.

Usage:
    python -m scripts.compare_strategies
"""

import uuid

import duckdb

from simulator.backtest import run_backtest
from simulator.math_utils import break_even_win_rate
from simulator.outcomes import generate_outcomes
from simulator.storage import create_results_table, save_result, summarize_by_strategy
from simulator.strategies import (
    DAlembertStrategy,
    FibonacciStrategy,
    FixedStakeStrategy,
    KellyCriterionStrategy,
    MartingaleStrategy,
)

TRIALS_PER_STRATEGY = 200
TRADES_PER_TRIAL = 300
WIN_PROBABILITY = 0.56
PAYOUT_RATIO = 0.85
STARTING_BANKROLL = 1000.0
BASE_UNIT = 10.0


def build_strategies() -> list:
    return [
        FixedStakeStrategy(),
        MartingaleStrategy(),
        DAlembertStrategy(),
        FibonacciStrategy(),
        KellyCriterionStrategy(win_probability=WIN_PROBABILITY, payout_ratio=PAYOUT_RATIO),
    ]


def main() -> None:
    connection = duckdb.connect(":memory:")
    create_results_table(connection)

    print(
        f"Win probability {WIN_PROBABILITY:.0%}, payout {PAYOUT_RATIO}, "
        f"break-even win rate {break_even_win_rate(PAYOUT_RATIO):.2%}\n"
    )

    for trial in range(TRIALS_PER_STRATEGY):
        outcomes = generate_outcomes(WIN_PROBABILITY, TRADES_PER_TRIAL, seed=trial)
        for strategy in build_strategies():
            result = run_backtest(strategy, outcomes, STARTING_BANKROLL, BASE_UNIT, PAYOUT_RATIO)
            save_result(connection, str(uuid.uuid4()), result)

    print(f"{'strategy':12s} {'runs':>6s} {'avg end':>10s} {'avg maxDD':>10s} {'ruin rate':>10s}")
    for row in summarize_by_strategy(connection):
        print(
            f"{row['strategy_name']:12s} {row['runs']:6d} "
            f"{row['avg_ending_bankroll']:10.2f} {row['avg_max_drawdown']:9.1%} "
            f"{row['ruin_rate']:9.1%}"
        )


if __name__ == "__main__":
    main()
