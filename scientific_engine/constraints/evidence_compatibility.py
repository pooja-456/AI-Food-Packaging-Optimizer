"""
Evidence compatibility checking for Phase 5 hard-constraint filtering.

Validates unit compatibility and environmental test-condition compatibility
(temperature, relative humidity) between material evidence and Phase 4 requirements.

Strictly evidence-backed:
- EXACT: Material test condition equals requirement storage condition.
- SUPPORTED: Material evidence explicitly documents cross-condition support.
- INCOMPATIBLE: Material evidence explicitly marks conditions as incompatible.
- UNKNOWN: Conditions differ and no validated cross-condition evidence exists.

Does NOT apply global temperature or humidity correction factors.
Does NOT invent universal temperature or humidity tolerance windows.
"""

from typing import List, Optional, Tuple

from app.schemas.constraints import ConditionMatchLevel
from app.schemas.material_evidence import MaterialPropertyEvidence


# ---------------------------------------------------------------------------
# Unit Normalisation
# ---------------------------------------------------------------------------
# Canonical unit forms used internally for comparison.
# Material evidence and Phase 4 requirements use slightly different formatting
# for the same SI/engineering units. This normaliser strips whitespace and
# formatting variations to determine equivalence.

_OTR_CANONICAL = "cc/(m2.day.atm)"
_WVTR_CANONICAL = "g/(m2.day)"
_CO2TR_CANONICAL = "cc/(m2.day.atm)"

_UNIT_ALIASES: dict[str, str] = {
    # OTR variants
    "cc/(m^2·day·atm)": _OTR_CANONICAL,
    "cc/(m²·day·atm)": _OTR_CANONICAL,
    "cc / (m² · day · atm)": _OTR_CANONICAL,
    "cc/(m2·day·atm)": _OTR_CANONICAL,
    "cc/(m2.day.atm)": _OTR_CANONICAL,
    "ml/(m^2·day·atm)": _OTR_CANONICAL,   # ml = cc at STP for gas
    # WVTR variants
    "g/(m^2·day)": _WVTR_CANONICAL,
    "g/(m²·day)": _WVTR_CANONICAL,
    "g / (m² · day)": _WVTR_CANONICAL,
    "g/(m2·day)": _WVTR_CANONICAL,
    "g/(m2.day)": _WVTR_CANONICAL,
    # CO2TR variants (same dimensional form as OTR)
    "cc co2/(m^2·day·atm)": _OTR_CANONICAL,
    "cc co2/(m²·day·atm)": _OTR_CANONICAL,
    "cc co2 / (m² · day · atm)": _OTR_CANONICAL,
}


def normalise_unit(unit: Optional[str]) -> Optional[str]:
    """
    Normalise a unit string to its canonical form for comparison.

    Returns None if the unit is None or unrecognised.
    """
    if unit is None:
        return None
    key = unit.strip().lower()
    for alias, canonical in _UNIT_ALIASES.items():
        if key == alias.lower():
            return canonical
    return None


def units_compatible(unit_a: Optional[str], unit_b: Optional[str]) -> bool:
    """
    Determine whether two unit strings are dimensionally equivalent.

    Both must normalise to the same canonical form.
    Returns False if either unit is None or unrecognised.
    """
    norm_a = normalise_unit(unit_a)
    norm_b = normalise_unit(unit_b)
    if norm_a is None or norm_b is None:
        return False
    return norm_a == norm_b


# ---------------------------------------------------------------------------
# Environmental Condition Compatibility (Evidence-Backed Only)
# ---------------------------------------------------------------------------

def assess_temperature_compatibility(
    test_temperature_c: Optional[float],
    requirement_temperature_c: Optional[float],
    evidence: Optional[MaterialPropertyEvidence] = None,
) -> Tuple[ConditionMatchLevel, List[str]]:
    """
    Assess temperature compatibility between material test condition and requirement.

    Classification:
    - EXACT: Temperatures match exactly (e.g. 23.0°C == 23.0°C).
    - SUPPORTED: Material evidence explicitly documents cross-temperature support.
    - INCOMPATIBLE: Material evidence explicitly marks conditions as incompatible.
    - UNKNOWN: Temperatures differ and no validated cross-temperature evidence exists.
    """
    warnings: List[str] = []

    if test_temperature_c is None or requirement_temperature_c is None:
        return ConditionMatchLevel.UNKNOWN, [
            "Temperature condition comparison not possible: "
            f"test_T={'unrecorded' if test_temperature_c is None else test_temperature_c}°C, "
            f"storage_T={'unrecorded' if requirement_temperature_c is None else requirement_temperature_c}°C."
        ]

    # Exact match check (accounting for floating point representation)
    if abs(test_temperature_c - requirement_temperature_c) < 1e-4:
        return ConditionMatchLevel.EXACT, []

    # Check evidence provenance notes for explicit cross-condition metadata
    if evidence and evidence.notes:
        notes_lower = evidence.notes.lower()
        if "incompatible" in notes_lower or "not_comparable" in notes_lower:
            warnings.append(
                f"Material tested at {test_temperature_c}°C is explicitly marked incompatible "
                f"with storage temperature of {requirement_temperature_c}°C."
            )
            return ConditionMatchLevel.INCOMPATIBLE, warnings

        if "cross_condition_supported" in notes_lower or "arrhenius_supported" in notes_lower:
            warnings.append(
                f"Material tested at {test_temperature_c}°C vs storage at {requirement_temperature_c}°C. "
                "Explicit material evidence supports cross-temperature comparison."
            )
            return ConditionMatchLevel.SUPPORTED, warnings

    # Differing temperatures without explicit cross-condition evidence -> UNKNOWN
    warnings.append(
        f"Material tested at {test_temperature_c}°C vs storage at {requirement_temperature_c}°C. "
        "No material-specific temperature activation model or cross-condition evidence available."
    )
    return ConditionMatchLevel.UNKNOWN, warnings


def assess_rh_compatibility(
    test_rh_percent: Optional[float],
    requirement_rh_percent: Optional[float],
    evidence: Optional[MaterialPropertyEvidence] = None,
) -> Tuple[ConditionMatchLevel, List[str]]:
    """
    Assess RH compatibility between material test condition and requirement.

    Classification:
    - EXACT: Relative humidities match exactly (e.g. 50.0% == 50.0%).
    - SUPPORTED: Material evidence explicitly documents cross-RH support.
    - INCOMPATIBLE: Material evidence explicitly marks conditions as incompatible.
    - UNKNOWN: Relative humidities differ and no validated cross-RH evidence exists.
    """
    warnings: List[str] = []

    if test_rh_percent is None or requirement_rh_percent is None:
        return ConditionMatchLevel.UNKNOWN, [
            "RH condition comparison not possible: "
            f"test_RH={'unrecorded' if test_rh_percent is None else test_rh_percent}%, "
            f"storage_RH={'unrecorded' if requirement_rh_percent is None else requirement_rh_percent}%."
        ]

    # Exact match check
    if abs(test_rh_percent - requirement_rh_percent) < 1e-4:
        return ConditionMatchLevel.EXACT, []

    # Check evidence provenance notes for explicit cross-condition metadata
    if evidence and evidence.notes:
        notes_lower = evidence.notes.lower()
        if "rh_incompatible" in notes_lower or "not_comparable" in notes_lower:
            warnings.append(
                f"Material tested at {test_rh_percent}% RH is explicitly marked incompatible "
                f"with storage RH of {requirement_rh_percent}%."
            )
            return ConditionMatchLevel.INCOMPATIBLE, warnings

        if "cross_condition_supported" in notes_lower or "rh_supported" in notes_lower:
            warnings.append(
                f"Material tested at {test_rh_percent}% RH vs storage at {requirement_rh_percent}% RH. "
                "Explicit material evidence supports cross-RH comparison."
            )
            return ConditionMatchLevel.SUPPORTED, warnings

    # Differing RH without explicit cross-condition evidence -> UNKNOWN
    warnings.append(
        f"Material tested at {test_rh_percent}% RH vs storage at {requirement_rh_percent}% RH. "
        "No material-specific RH plasticization model or cross-condition evidence available."
    )
    return ConditionMatchLevel.UNKNOWN, warnings


def assess_overall_condition_compatibility(
    test_temperature_c: Optional[float],
    requirement_temperature_c: Optional[float],
    test_rh_percent: Optional[float],
    requirement_rh_percent: Optional[float],
    evidence: Optional[MaterialPropertyEvidence] = None,
) -> Tuple[ConditionMatchLevel, List[str]]:
    """
    Combine temperature and RH compatibility into an overall condition match level.

    The overall level is the WORST (most restrictive) of the two individual checks.
    Priority order (worst -> best): INCOMPATIBLE > UNKNOWN > SUPPORTED > EXACT.
    """
    temp_level, temp_warnings = assess_temperature_compatibility(
        test_temperature_c, requirement_temperature_c, evidence=evidence
    )
    rh_level, rh_warnings = assess_rh_compatibility(
        test_rh_percent, requirement_rh_percent, evidence=evidence
    )

    combined_warnings = temp_warnings + rh_warnings

    _priority = {
        ConditionMatchLevel.INCOMPATIBLE: 0,
        ConditionMatchLevel.UNKNOWN: 1,
        ConditionMatchLevel.SUPPORTED: 2,
        ConditionMatchLevel.EXACT: 3,
    }

    if _priority[temp_level] <= _priority[rh_level]:
        overall = temp_level
    else:
        overall = rh_level

    return overall, combined_warnings
