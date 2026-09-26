"""
Domain applicability and boundary validation rules for food packaging physics models.
"""

from typing import List, Optional, Tuple


def validate_temperature_range(
    temperature_c: Optional[float],
    min_c: float = -20.0,
    max_c: float = 50.0,
    model_name: str = "Model",
) -> List[str]:
    """Check whether storage temperature lies within physiological or physical validity."""
    warnings: List[str] = []
    if temperature_c is None:
        return warnings
    if temperature_c < min_c:
        warnings.append(
            f"[{model_name}] Temperature {temperature_c}°C is below validated lower limit ({min_c}°C). "
            f"Freezing or severe chilling effects may invalidate standard kinetics."
        )
    elif temperature_c > max_c:
        warnings.append(
            f"[{model_name}] Temperature {temperature_c}°C exceeds validated upper limit ({max_c}°C). "
            f"Thermal injury, protein denaturation, or rapid collapse may occur."
        )
    return warnings


def validate_water_activity(
    aw: Optional[float],
    model_name: str = "MoistureModel",
) -> List[str]:
    """Check that water activity is in the physical range [0.0, 1.0]."""
    warnings: List[str] = []
    if aw is None:
        return warnings
    if not (0.0 <= aw <= 1.0):
        warnings.append(
            f"[{model_name}] Water activity aw = {aw} is outside thermodynamic range [0.0, 1.0]."
        )
    return warnings


def validate_relative_humidity(
    rh_percent: Optional[float],
    model_name: str = "MoistureModel",
) -> List[str]:
    """Check that relative humidity is within [0.0, 100.0]%."""
    warnings: List[str] = []
    if rh_percent is None:
        return warnings
    if not (0.0 <= rh_percent <= 100.0):
        warnings.append(
            f"[{model_name}] Relative humidity RH = {rh_percent}% is outside physical range [0.0, 100.0]%."
        )
    return warnings


def validate_gas_fractions(
    o2_fraction: Optional[float],
    co2_fraction: Optional[float],
    model_name: str = "GasExchangeModel",
) -> List[str]:
    """Check that headspace gas fractions are valid proportions [0.0, 1.0]."""
    warnings: List[str] = []
    if o2_fraction is not None and not (0.0 <= o2_fraction <= 1.0):
        warnings.append(f"[{model_name}] O2 fraction {o2_fraction} is outside valid range [0.0, 1.0].")
    if co2_fraction is not None and not (0.0 <= co2_fraction <= 1.0):
        warnings.append(f"[{model_name}] CO2 fraction {co2_fraction} is outside valid range [0.0, 1.0].")
    if o2_fraction is not None and co2_fraction is not None and (o2_fraction + co2_fraction > 1.0):
        warnings.append(
            f"[{model_name}] Sum of O2 ({o2_fraction}) and CO2 ({co2_fraction}) exceeds 1.0."
        )
    return warnings
