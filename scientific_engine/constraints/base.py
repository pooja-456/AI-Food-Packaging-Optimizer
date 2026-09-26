"""
Generic interval comparison primitives for deterministic hard-constraint filtering.

Provides conservative comparison logic for scalar and interval values
with explicit determinacy classification.
"""

from enum import Enum
from typing import Optional, Tuple


class IntervalComparisonResult(str, Enum):
    """Internal determinacy classification for interval comparisons."""
    DEFINITELY_FEASIBLE = "DEFINITELY_FEASIBLE"
    DEFINITELY_INFEASIBLE = "DEFINITELY_INFEASIBLE"
    UNCERTAIN = "UNCERTAIN"


def get_interval(
    value: Optional[float],
    minimum_value: Optional[float],
    maximum_value: Optional[float],
) -> Optional[Tuple[float, float]]:
    """
    Extract a conservative [min, max] interval from value/min/max fields.

    If min/max are available, uses them (they may be wider than the point value).
    If only a point value is available, returns [value, value].
    Returns None if no usable numeric data exists.
    """
    if minimum_value is not None and maximum_value is not None:
        return (minimum_value, maximum_value)
    if value is not None:
        return (value, value)
    return None


def compare_le(
    material_interval: Tuple[float, float],
    requirement_interval: Tuple[float, float],
) -> IntervalComparisonResult:
    """
    Evaluate: material <= requirement.

    Used when the requirement represents a MAXIMUM allowable value
    (e.g. material WVTR must not exceed the maximum allowable moisture flux).

    DEFINITELY_FEASIBLE:   material_max <= requirement_min
        Even the worst-case material is within the most conservative requirement.
    DEFINITELY_INFEASIBLE: material_min > requirement_max
        Even the best-case material exceeds the most generous requirement.
    UNCERTAIN:             intervals overlap — cannot definitively conclude.
    """
    mat_min, mat_max = material_interval
    req_min, req_max = requirement_interval

    if mat_max <= req_min:
        return IntervalComparisonResult.DEFINITELY_FEASIBLE
    elif mat_min > req_max:
        return IntervalComparisonResult.DEFINITELY_INFEASIBLE
    else:
        return IntervalComparisonResult.UNCERTAIN


def compare_ge(
    material_interval: Tuple[float, float],
    requirement_interval: Tuple[float, float],
) -> IntervalComparisonResult:
    """
    Evaluate: material >= requirement.

    Used when the requirement represents a MINIMUM required value
    (e.g. material OTR must provide at least the required gas transmission
    to prevent anaerobiosis in EMAP applications).

    DEFINITELY_FEASIBLE:   material_min >= requirement_max
        Even the worst-case material meets the most demanding requirement.
    DEFINITELY_INFEASIBLE: material_max < requirement_min
        Even the best-case material falls short of the minimum requirement.
    UNCERTAIN:             intervals overlap — cannot definitively conclude.
    """
    mat_min, mat_max = material_interval
    req_min, req_max = requirement_interval

    if mat_min >= req_max:
        return IntervalComparisonResult.DEFINITELY_FEASIBLE
    elif mat_max < req_min:
        return IntervalComparisonResult.DEFINITELY_INFEASIBLE
    else:
        return IntervalComparisonResult.UNCERTAIN
