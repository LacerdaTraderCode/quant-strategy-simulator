"""Tests for persisting and aggregating backtest results in DuckDB."""

import duckdb
import pytest

from simulator.backtest import BacktestResult
from simulator.storage import create_results_table, save_result, summarize_by_strategy


@pytest.fixture
def connection():
    connection = duckdb.connect(":memory:")
    create_results_table(connection)
    return connection


def _result(strategy_name: str, ending_bankroll: float, ruined: bool) -> BacktestResult:
    return BacktestResult(
        strategy_name=strategy_name,
        starting_bankroll=1000,
        ending_bankroll=ending_bankroll,
        max_drawdown=0.1,
        ruined=ruined,
        history=(),
    )


def test_saved_results_can_be_summarized_by_strategy(connection):
    save_result(connection, "run-1", _result("fixed", 1200, ruined=False))
    save_result(connection, "run-2", _result("fixed", 1300, ruined=False))
    save_result(connection, "run-3", _result("martingale", 0, ruined=True))

    summary = summarize_by_strategy(connection)
    by_name = {row["strategy_name"]: row for row in summary}

    assert by_name["fixed"]["runs"] == 2
    assert by_name["fixed"]["avg_ending_bankroll"] == 1250
    assert by_name["fixed"]["ruin_rate"] == 0.0
    assert by_name["martingale"]["ruin_rate"] == 1.0


def test_summary_is_ordered_by_average_ending_bankroll_descending(connection):
    save_result(connection, "run-1", _result("worse", 900, ruined=False))
    save_result(connection, "run-2", _result("better", 1500, ruined=False))

    summary = summarize_by_strategy(connection)

    assert [row["strategy_name"] for row in summary] == ["better", "worse"]
