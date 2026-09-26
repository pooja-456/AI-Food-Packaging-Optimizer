"""
Physical constants, thermodynamic functions, and standard unit conversions for food packaging physics.

All functions and constants maintain explicit scientific provenance.
"""

import math
from typing import Optional, Tuple


# --- Universal Physical Constants ---
R_GAS_CONSTANT_J_MOL_K = 8.314462  # Universal gas constant (J / (mol · K))
R_GAS_CONSTANT_L_ATM_MOL_K = 0.082057  # L · atm / (mol · K)
STANDARD_MOLAR_VOLUME_L_MOL = 22.414  # Standard molar volume of ideal gas at STP (L / mol = mL / mmol)
MOLAR_MASS_H2O_G_MOL = 18.01528  # Molar mass of water (g / mol)
MOLAR_MASS_O2_G_MOL = 31.9988  # Molar mass of O2 (g / mol)
MOLAR_MASS_CO2_G_MOL = 44.0095  # Molar mass of CO2 (g / mol)

# Standard atmospheric pressures
STD_ATM_KPA = 101.325  # Standard atmospheric pressure in kPa
STD_ATM_BAR = 1.01325  # Standard atmospheric pressure in bar


def water_saturation_vapor_pressure_kpa(temperature_c: float) -> float:
    """
    Calculate saturation water vapor pressure Psat(T) in kPa using the Tetens/Buck equation.

    Equation:
        Psat(T) = 0.61078 * exp((17.27 * T) / (T + 237.3))  [for T >= 0 °C]
        Psat(T) = 0.61078 * exp((21.875 * T) / (T + 265.5)) [for T < 0 °C (over ice)]

    Scientific Source:
        Tetens, O. (1930). Über einige meteorologische Begriffe. Zeitschrift für Geophysik, 6:297–309.
        Buck, A. L. (1981). New equations for computing vapor pressure and enhancement factor.
        Journal of Applied Meteorology, 20(12):1527–1532.

    Validity: -40 °C to +50 °C. Error < 0.1% over standard postharvest food storage range.
    """
    if temperature_c >= 0.0:
        return 0.61078 * math.exp((17.27 * temperature_c) / (temperature_c + 237.3))
    else:
        return 0.61078 * math.exp((21.875 * temperature_c) / (temperature_c + 265.5))


def water_vapor_pressure_kpa(temperature_c: float, relative_humidity_percent: float) -> float:
    """
    Calculate ambient water vapor pressure in kPa from relative humidity.

    p_w = (RH / 100) * Psat(T)
    """
    rh_fraction = max(0.0, min(1.0, relative_humidity_percent / 100.0))
    psat = water_saturation_vapor_pressure_kpa(temperature_c)
    return rh_fraction * psat


def food_surface_vapor_pressure_kpa(temperature_c: float, water_activity: float) -> float:
    """
    Calculate equilibrium water vapor pressure above food surface from water activity.

    p_w,food = aw * Psat(T)
    """
    aw_bounded = max(0.0, min(1.0, water_activity))
    psat = water_saturation_vapor_pressure_kpa(temperature_c)
    return aw_bounded * psat


def mg_co2_to_ml_co2(mg_co2: float) -> float:
    """
    Convert mg CO2 to mL CO2 gas at standard STP conditions (0 °C, 1 atm).

    mL CO2 = (mg CO2 / 44.01 mg/mmol) * 22.414 mL/mmol = mg CO2 * 0.5093
    """
    return (mg_co2 / MOLAR_MASS_CO2_G_MOL) * STANDARD_MOLAR_VOLUME_L_MOL


def ml_co2_to_mg_co2(ml_co2: float) -> float:
    """Convert mL CO2 gas at STP to mg CO2."""
    return (ml_co2 / STANDARD_MOLAR_VOLUME_L_MOL) * MOLAR_MASS_CO2_G_MOL


def mg_o2_to_ml_o2(mg_o2: float) -> float:
    """
    Convert mg O2 to mL O2 gas at STP.

    mL O2 = (mg O2 / 32.00 mg/mmol) * 22.414 mL/mmol = mg O2 * 0.7005
    """
    return (mg_o2 / MOLAR_MASS_O2_G_MOL) * STANDARD_MOLAR_VOLUME_L_MOL


def ml_o2_to_mg_o2(ml_o2: float) -> float:
    """Convert mL O2 gas at STP to mg O2."""
    return (ml_o2 / STANDARD_MOLAR_VOLUME_L_MOL) * MOLAR_MASS_O2_G_MOL
