# Quant Strategy Simulator

A backtesting library for classic money-management strategies — Fixed, Martingale, D'Alembert, Fibonacci, and Kelly Criterion — run against synthetic outcome sequences and compared across hundreds of Monte Carlo trials.

This is a backtester, not a live signal generator: it answers "how does this staking strategy behave at a given edge" using generated outcomes, not "what should I bet on the next real trade."

## The core idea

Money management does not create an edge. At a given win probability and payout ratio, every strategy here has the same expected value per unit staked; what differs is the shape of the equity curve — how much it can grow, how deep it can drawdown, and how often it ruins the account entirely. `simulator/math_utils.break_even_win_rate` computes the win rate a payout ratio needs just to break even, independent of which strategy is used.

Run the comparison yourself:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.compare_strategies
```

At a 56% win rate against an 85% payout (break-even is 54.05%), 200 trials of 300 trades each produce results like:

```
strategy       runs    avg end  avg maxDD  ruin rate
kelly           200    1735.84     47.7%      0.0%
dalembert       200    1391.88     50.7%     19.0%
martingale      200    1384.47     53.1%     25.0%
fibonacci       200    1184.76     36.1%     14.0%
fixed           200    1124.19     13.3%      0.0%
```

Martingale and D'Alembert post decent average returns and still ruin the account in roughly a fifth to a quarter of runs — the average return alone would hide that risk completely.

## Strategies

| Strategy | Rule |
|---|---|
| `fixed` | Same stake every trade |
| `martingale` | Doubles after a loss, resets after a win |
| `dalembert` | +1 unit after a loss, -1 unit after a win, floored at the base unit |
| `fibonacci` | Steps forward in the Fibonacci sequence after a loss, back two steps after a win |
| `kelly` | Stakes a fixed fraction of the *current* bankroll, sized by the Kelly criterion for a known win probability and payout |

## Why DuckDB

A single backtest is one equity curve. Comparing strategies means aggregating across hundreds of runs — `simulator/storage.py` writes every run's result to a DuckDB table and `summarize_by_strategy` does the aggregation (average ending bankroll, average drawdown, ruin rate) in one SQL query.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The suite tests the betting math, each strategy's staking behavior in isolation, the backtest engine's bankroll and drawdown tracking (including that a strategy which outgrows the bankroll is marked ruined, not left to go negative), and the DuckDB aggregation.

## License

MIT — see [LICENSE](LICENSE).
