"""Generates synthetic win/loss sequences for Monte Carlo style backtesting."""

import random


def generate_outcomes(win_probability: float, count: int, seed: int | None = None) -> list[bool]:
    rng = random.Random(seed)
    return [rng.random() < win_probability for _ in range(count)]
