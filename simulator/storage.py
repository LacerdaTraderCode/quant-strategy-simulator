"""Persists backtest results to DuckDB so many Monte Carlo runs can be aggregated with SQL."""

import duckdb

from simulator.backtest import BacktestResult


def create_results_table(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS backtest_results (
            run_id TEXT,
            strategy_name TEXT,
            starting_bankroll DOUBLE,
            ending_bankroll DOUBLE,
            max_drawdown DOUBLE,
            ruined BOOLEAN
        )
        """
    )


def save_result(connection: duckdb.DuckDBPyConnection, run_id: str, result: BacktestResult) -> None:
    connection.execute(
        "INSERT INTO backtest_results VALUES (?, ?, ?, ?, ?, ?)",
        [
            run_id,
            result.strategy_name,
            result.starting_bankroll,
            result.ending_bankroll,
            result.max_drawdown,
            result.ruined,
        ],
    )


def summarize_by_strategy(connection: duckdb.DuckDBPyConnection) -> list[dict]:
    rows = connection.execute(
        """
        SELECT
            strategy_name,
            count(*) AS runs,
            avg(ending_bankroll) AS avg_ending_bankroll,
            avg(max_drawdown) AS avg_max_drawdown,
            sum(CASE WHEN ruined THEN 1 ELSE 0 END) * 1.0 / count(*) AS ruin_rate
        FROM backtest_results
        GROUP BY strategy_name
        ORDER BY avg_ending_bankroll DESC
        """
    ).fetchall()
    columns = ["strategy_name", "runs", "avg_ending_bankroll", "avg_max_drawdown", "ruin_rate"]
    return [dict(zip(columns, row, strict=True)) for row in rows]
