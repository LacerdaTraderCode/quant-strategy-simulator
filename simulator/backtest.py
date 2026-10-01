"""Runs a money-management strategy against a fixed sequence of trade outcomes."""

from dataclasses import dataclass

from simulator.strategies import Strategy


@dataclass(frozen=True)
class BankrollPoint:
    trade_index: int
    stake: float
    won: bool
    bankroll_after: float


@dataclass(frozen=True)
class BacktestResult:
    strategy_name: str
    starting_bankroll: float
    ending_bankroll: float
    max_drawdown: float
    ruined: bool
    history: tuple[BankrollPoint, ...]


def run_backtest(
    strategy: Strategy,
    outcomes: list[bool],
    starting_bankroll: float,
    base_unit: float,
    payout_ratio: float,
) -> BacktestResult:
    strategy.reset(base_unit)
    bankroll = starting_bankroll
    peak = starting_bankroll
    max_drawdown = 0.0
    history: list[BankrollPoint] = []
    ruined = False

    for index, won in enumerate(outcomes):
        stake = min(strategy.next_stake(bankroll), bankroll)
        if stake <= 0:
            ruined = True
            break

        bankroll += stake * payout_ratio if won else -stake
        strategy.record_outcome(won)

        peak = max(peak, bankroll)
        drawdown = (peak - bankroll) / peak if peak > 0 else 1.0
        max_drawdown = max(max_drawdown, drawdown)

        history.append(
            BankrollPoint(trade_index=index, stake=stake, won=won, bankroll_after=bankroll)
        )

        if bankroll <= 0:
            ruined = True
            break

    return BacktestResult(
        strategy_name=strategy.name,
        starting_bankroll=starting_bankroll,
        ending_bankroll=bankroll,
        max_drawdown=max_drawdown,
        ruined=ruined,
        history=tuple(history),
    )
