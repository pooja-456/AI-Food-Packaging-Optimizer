"""
Interval arithmetic and non-destructive uncertainty propagation utilities.
"""

from typing import Optional, Tuple


def add_intervals(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float]:
    """[a_min + b_min, a_max + b_max]"""
    return (round(a[0] + b[0], 4), round(a[1] + b[1], 4))


def subtract_intervals(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float]:
    """[a_min - b_max, a_max - b_min]"""
    return (round(a[0] - b[1], 4), round(a[1] - b[0], 4))


def scale_interval(interval: Tuple[float, float], factor: float) -> Tuple[float, float]:
    """Multiply interval by a positive scalar."""
    if factor >= 0:
        return (round(interval[0] * factor, 4), round(interval[1] * factor, 4))
    else:
        return (round(interval[1] * factor, 4), round(interval[0] * factor, 4))


def multiply_intervals(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float]:
    """Interval product: min/max of all pairwise products."""
    products = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
    return (round(min(products), 4), round(max(products), 4))


def divide_interval_by_scalar(interval: Tuple[float, float], scalar: float) -> Optional[Tuple[float, float]]:
    """Divide interval by a non-zero scalar."""
    if scalar == 0:
        return None
    return scale_interval(interval, 1.0 / scalar)


def divide_intervals(a: Tuple[float, float], b: Tuple[float, float]) -> Optional[Tuple[float, float]]:
    """
    Interval division: [a] / [b].
    Returns None if denominator interval spans zero (b_min <= 0 <= b_max).
    """
    if b[0] <= 0.0 <= b[1]:
        return None
    quotients = [a[0] / b[0], a[0] / b[1], a[1] / b[0], a[1] / b[1]]
    return (round(min(quotients), 4), round(max(quotients), 4))
