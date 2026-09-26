"""
Barrier constraint evaluators for OTR, CO2TR, and WVTR.

Each evaluator:
1. Locates relevant property evidence on the candidate material.
2. Checks unit compatibility against the Phase 4 requirement unit.
3. Assesses environmental test-condition compatibility.
4. Performs conservative interval comparison.
5. Returns a fully traceable ConstraintEvaluation.

Comparison Semantics (derived from Phase 4 code inspection):
    OTR  → GE (material OTR >= required OTR) — material must transmit at least
           enough O2 for EMAP equilibrium to prevent anaerobiosis.
    CO2TR → GE (material CO2TR >= required CO2TR) — same logic for CO2 efflux.
    WVTR → LE (material WVTR <= required WVTR) — material must not exceed
           the maximum allowable moisture flux to protect shelf life.
"""

from typing import List, Optional, Tuple

from app.schemas.constraints import (
    ComparisonOperator,
    ConditionMatchLevel,
    ConstraintEvaluation,
    ConstraintStatus,
)
from app.schemas.material_evidence import MaterialPropertyEvidence, PackagingMaterialSpec
from app.schemas.physics import ScientificResult
from scientific_engine.constraints.base import (
    IntervalComparisonResult,
    compare_ge,
    compare_le,
    get_interval,
)
from scientific_engine.constraints.evidence_compatibility import (
    assess_overall_condition_compatibility,
    units_compatible,
)
from scientific_engine.physics.traceability import make_traceability


# ---------------------------------------------------------------------------
# Mapping from internal IntervalComparisonResult → public ConstraintStatus
# ---------------------------------------------------------------------------

_COMPARISON_TO_STATUS = {
    IntervalComparisonResult.DEFINITELY_FEASIBLE: ConstraintStatus.FEASIBLE,
    IntervalComparisonResult.DEFINITELY_INFEASIBLE: ConstraintStatus.INFEASIBLE,
    IntervalComparisonResult.UNCERTAIN: ConstraintStatus.UNKNOWN,
}


# ---------------------------------------------------------------------------
# Best-evidence selector
# ---------------------------------------------------------------------------

def _select_best_evidence(
    evidence_list: List[MaterialPropertyEvidence],
    requirement_temperature_c: Optional[float],
    requirement_rh_percent: Optional[float],
) -> Tuple[Optional[MaterialPropertyEvidence], ConditionMatchLevel, List[str]]:
    """
    Select the single most condition-compatible evidence record from a list.

    Priority: EXACT > SUPPORTED > UNKNOWN > INCOMPATIBLE.
    Within the same compatibility tier, selects the first encountered.

    Returns (best_evidence, condition_match, combined_warnings).
    Returns (None, UNKNOWN, warnings) if the list is empty.
    """
    if not evidence_list:
        return None, ConditionMatchLevel.UNKNOWN, ["No material property evidence records available."]

    _priority = {
        ConditionMatchLevel.EXACT: 3,
        ConditionMatchLevel.SUPPORTED: 2,
        ConditionMatchLevel.UNKNOWN: 1,
        ConditionMatchLevel.INCOMPATIBLE: 0,
    }

    best: Optional[MaterialPropertyEvidence] = None
    best_level = ConditionMatchLevel.INCOMPATIBLE
    best_warnings: List[str] = []

    for ev in evidence_list:
        level, warnings = assess_overall_condition_compatibility(
            test_temperature_c=ev.test_temperature_c,
            requirement_temperature_c=requirement_temperature_c,
            test_rh_percent=ev.test_relative_humidity_percent,
            requirement_rh_percent=requirement_rh_percent,
            evidence=ev,
        )
        if best is None or _priority[level] > _priority[best_level]:
            best = ev
            best_level = level
            best_warnings = warnings

    return best, best_level, best_warnings


# ---------------------------------------------------------------------------
# Generic barrier constraint evaluator
# ---------------------------------------------------------------------------

def _evaluate_barrier_constraint(
    constraint_type: str,
    comparison_operator: ComparisonOperator,
    requirement_result: Optional[ScientificResult],
    requirement_unit: Optional[str],
    material: PackagingMaterialSpec,
    material_property_name: str,
    requirement_temperature_c: Optional[float],
    requirement_rh_percent: Optional[float],
) -> ConstraintEvaluation:
    """
    Core barrier-constraint evaluation shared by OTR, CO2TR, and WVTR.

    Steps:
        1. Check if the Phase 4 requirement exists and has a value.
        2. Locate material evidence for the property.
        3. Select the best condition-compatible evidence record.
        4. Check unit compatibility.
        5. Check condition compatibility (INCOMPATIBLE → UNKNOWN).
        6. Extract intervals and perform deterministic comparison.
        7. Build traceable ConstraintEvaluation.
    """
    # --- Step 1: Validate requirement ---
    if requirement_result is None or requirement_result.value is None:
        return ConstraintEvaluation(
            constraint_type=constraint_type,
            status=ConstraintStatus.UNKNOWN,
            comparison_operator=comparison_operator,
            required_value=None,
            required_unit=requirement_unit,
            condition_match=ConditionMatchLevel.UNKNOWN,
            reason="Phase 4 requirement is absent or has no computed value.",
            traceability=make_traceability(
                model_name="Phase5HardConstraintFilter",
                equation_form=f"material.{constraint_type} {comparison_operator.value} requirement.{constraint_type}",
                failure_or_unknown_reason="Requirement value is None (not computed by Phase 4).",
            ),
        )

    req_val = requirement_result.value
    req_unit = requirement_result.unit
    req_interval = get_interval(
        req_val,
        requirement_result.minimum_value,
        requirement_result.maximum_value,
    )
    req_range = (requirement_result.minimum_value, requirement_result.maximum_value) if (
        requirement_result.minimum_value is not None and requirement_result.maximum_value is not None
    ) else None

    # --- Step 2: Locate material evidence ---
    evidence_list = material.get_property_evidence(material_property_name)
    if not evidence_list:
        return ConstraintEvaluation(
            constraint_type=constraint_type,
            status=ConstraintStatus.UNKNOWN,
            comparison_operator=comparison_operator,
            required_value=req_val,
            required_unit=req_unit,
            required_range=req_range,
            condition_match=ConditionMatchLevel.UNKNOWN,
            reason=f"Material '{material.material_id}' has no evidence for '{material_property_name}'.",
            traceability=make_traceability(
                model_name="Phase5HardConstraintFilter",
                equation_form=f"material.{constraint_type} {comparison_operator.value} requirement",
                failure_or_unknown_reason=f"No material evidence for {material_property_name}.",
            ),
        )

    # --- Step 3: Select best condition-compatible evidence ---
    best_ev, condition_level, condition_warnings = _select_best_evidence(
        evidence_list, requirement_temperature_c, requirement_rh_percent,
    )
    if best_ev is None:
        return ConstraintEvaluation(
            constraint_type=constraint_type,
            status=ConstraintStatus.UNKNOWN,
            comparison_operator=comparison_operator,
            required_value=req_val,
            required_unit=req_unit,
            required_range=req_range,
            condition_match=ConditionMatchLevel.UNKNOWN,
            reason="No usable material evidence record found.",
            warnings=condition_warnings,
            traceability=make_traceability(
                model_name="Phase5HardConstraintFilter",
                equation_form=f"material.{constraint_type} {comparison_operator.value} requirement",
                failure_or_unknown_reason="No usable material evidence record.",
            ),
        )

    # --- Step 4: Check unit compatibility ---
    if not units_compatible(best_ev.unit, req_unit):
        return ConstraintEvaluation(
            constraint_type=constraint_type,
            status=ConstraintStatus.UNKNOWN,
            comparison_operator=comparison_operator,
            required_value=req_val,
            required_unit=req_unit,
            required_range=req_range,
            material_value=best_ev.value,
            material_unit=best_ev.unit,
            material_range=(best_ev.minimum_value, best_ev.maximum_value) if (
                best_ev.minimum_value is not None and best_ev.maximum_value is not None
            ) else None,
            condition_match=condition_level,
            test_temperature_c=best_ev.test_temperature_c,
            test_relative_humidity_percent=best_ev.test_relative_humidity_percent,
            material_evidence_reference=best_ev.source_title,
            reason=(
                f"Unit mismatch: material unit '{best_ev.unit}' vs requirement unit '{req_unit}'. "
                f"No validated conversion available."
            ),
            warnings=condition_warnings,
            traceability=make_traceability(
                model_name="Phase5HardConstraintFilter",
                equation_form=f"material.{constraint_type} {comparison_operator.value} requirement",
                failure_or_unknown_reason=f"Incompatible units: '{best_ev.unit}' vs '{req_unit}'.",
            ),
        )

    # --- Step 5: Check condition compatibility ---
    if condition_level in (ConditionMatchLevel.INCOMPATIBLE, ConditionMatchLevel.UNKNOWN):
        reason = (
            "Environmental test conditions are explicitly marked incompatible with requirement conditions."
            if condition_level == ConditionMatchLevel.INCOMPATIBLE
            else "Environmental test conditions differ from requirement storage conditions and no validated cross-condition evidence exists."
        )
        return ConstraintEvaluation(
            constraint_type=constraint_type,
            status=ConstraintStatus.UNKNOWN,
            comparison_operator=comparison_operator,
            required_value=req_val,
            required_unit=req_unit,
            required_range=req_range,
            material_value=best_ev.value,
            material_unit=best_ev.unit,
            material_range=(best_ev.minimum_value, best_ev.maximum_value) if (
                best_ev.minimum_value is not None and best_ev.maximum_value is not None
            ) else None,
            condition_match=condition_level,
            test_temperature_c=best_ev.test_temperature_c,
            test_relative_humidity_percent=best_ev.test_relative_humidity_percent,
            material_evidence_reference=best_ev.source_title,
            reason=reason,
            warnings=condition_warnings,
            traceability=make_traceability(
                model_name="Phase5HardConstraintFilter",
                equation_form=f"material.{constraint_type} {comparison_operator.value} requirement",
                failure_or_unknown_reason=reason,
                inputs_used={
                    "test_temperature_c": best_ev.test_temperature_c,
                    "test_rh_percent": best_ev.test_relative_humidity_percent,
                    "storage_temperature_c": requirement_temperature_c,
                    "storage_rh_percent": requirement_rh_percent,
                },
            ),
        )

    # --- Step 6: Extract intervals and compare ---
    mat_interval = get_interval(best_ev.value, best_ev.minimum_value, best_ev.maximum_value)
    if mat_interval is None or req_interval is None:
        return ConstraintEvaluation(
            constraint_type=constraint_type,
            status=ConstraintStatus.UNKNOWN,
            comparison_operator=comparison_operator,
            required_value=req_val,
            required_unit=req_unit,
            required_range=req_range,
            material_value=best_ev.value,
            material_unit=best_ev.unit,
            condition_match=condition_level,
            test_temperature_c=best_ev.test_temperature_c,
            test_relative_humidity_percent=best_ev.test_relative_humidity_percent,
            material_evidence_reference=best_ev.source_title,
            reason="Cannot extract numeric interval from material or requirement evidence.",
            warnings=condition_warnings,
            traceability=make_traceability(
                model_name="Phase5HardConstraintFilter",
                equation_form=f"material.{constraint_type} {comparison_operator.value} requirement",
                failure_or_unknown_reason="Numeric interval extraction failed.",
            ),
        )

    if comparison_operator == ComparisonOperator.GE:
        comparison_result = compare_ge(mat_interval, req_interval)
    elif comparison_operator == ComparisonOperator.LE:
        comparison_result = compare_le(mat_interval, req_interval)
    else:
        comparison_result = IntervalComparisonResult.UNCERTAIN

    status = _COMPARISON_TO_STATUS[comparison_result]
    mat_range = (best_ev.minimum_value, best_ev.maximum_value) if (
        best_ev.minimum_value is not None and best_ev.maximum_value is not None
    ) else None

    # Build reason string
    if status == ConstraintStatus.FEASIBLE:
        reason = (
            f"Material {constraint_type} [{mat_interval[0]}, {mat_interval[1]}] "
            f"{comparison_operator.value} requirement [{req_interval[0]}, {req_interval[1]}] "
            f"— definitively satisfied."
        )
    elif status == ConstraintStatus.INFEASIBLE:
        reason = (
            f"Material {constraint_type} [{mat_interval[0]}, {mat_interval[1]}] "
            f"fails {comparison_operator.value} requirement [{req_interval[0]}, {req_interval[1]}] "
            f"— definitively violated."
        )
    else:
        reason = (
            f"Material {constraint_type} [{mat_interval[0]}, {mat_interval[1]}] "
            f"overlaps requirement [{req_interval[0]}, {req_interval[1]}] "
            f"— cannot definitively conclude."
        )

    # --- Step 7: Build traceable result ---
    trace = make_traceability(
        model_name="Phase5HardConstraintFilter",
        equation_form=f"material.{constraint_type} {comparison_operator.value} requirement.{constraint_type}",
        equation_reference="Deterministic interval comparison (Phase 5 specification)",
        inputs_used={
            "material_id": material.material_id,
            "material_value": best_ev.value,
            "material_interval": list(mat_interval),
            "material_unit": best_ev.unit,
            "required_value": req_val,
            "required_interval": list(req_interval),
            "required_unit": req_unit,
        },
        parameters_used={
            "comparison_operator": comparison_operator.value,
            "condition_match": condition_level.value,
        },
        units_used={
            "material": best_ev.unit or "unspecified",
            "requirement": req_unit or "unspecified",
        },
        assumptions=[
            f"Comparison performed using {comparison_operator.value} operator.",
            f"Test condition compatibility: {condition_level.value}.",
        ],
        warnings=condition_warnings,
    )

    return ConstraintEvaluation(
        constraint_type=constraint_type,
        status=status,
        comparison_operator=comparison_operator,
        required_value=req_val,
        required_unit=req_unit,
        required_range=req_range,
        material_value=best_ev.value,
        material_unit=best_ev.unit,
        material_range=mat_range,
        condition_match=condition_level,
        test_temperature_c=best_ev.test_temperature_c,
        test_relative_humidity_percent=best_ev.test_relative_humidity_percent,
        material_evidence_reference=best_ev.source_title,
        reason=reason,
        warnings=condition_warnings,
        traceability=trace,
    )


# ---------------------------------------------------------------------------
# Public evaluator functions
# ---------------------------------------------------------------------------

def evaluate_otr_constraint(
    material: PackagingMaterialSpec,
    required_otr: Optional[ScientificResult],
    storage_temperature_c: Optional[float],
    storage_rh_percent: Optional[float],
) -> ConstraintEvaluation:
    """
    Evaluate OTR hard constraint.

    Semantics (from Phase 4 gas_exchange.py):
        OTR_req is the MINIMUM required oxygen transmission rate for the package
        to maintain equilibrium modified atmosphere. If the material OTR is below
        this, the package cannot transmit enough O2 → anaerobic conditions.

    Comparison: material OTR >= required OTR (GE operator).
    """
    return _evaluate_barrier_constraint(
        constraint_type="oxygen_transmission_rate",
        comparison_operator=ComparisonOperator.GE,
        requirement_result=required_otr,
        requirement_unit=required_otr.unit if required_otr else None,
        material=material,
        material_property_name="oxygen_transmission_rate",
        requirement_temperature_c=storage_temperature_c,
        requirement_rh_percent=storage_rh_percent,
    )


def evaluate_co2tr_constraint(
    material: PackagingMaterialSpec,
    required_co2tr: Optional[ScientificResult],
    storage_temperature_c: Optional[float],
    storage_rh_percent: Optional[float],
) -> ConstraintEvaluation:
    """
    Evaluate CO2TR hard constraint.

    Semantics (from Phase 4 gas_exchange.py):
        CO2TR_req is the MINIMUM required carbon dioxide transmission rate
        for the package to release CO2 generated by respiration. If the material
        CO2TR is below this, CO2 accumulates → fermentation injury.

    Comparison: material CO2TR >= required CO2TR (GE operator).
    """
    return _evaluate_barrier_constraint(
        constraint_type="carbon_dioxide_transmission_rate",
        comparison_operator=ComparisonOperator.GE,
        requirement_result=required_co2tr,
        requirement_unit=required_co2tr.unit if required_co2tr else None,
        material=material,
        material_property_name="carbon_dioxide_transmission_rate",
        requirement_temperature_c=storage_temperature_c,
        requirement_rh_percent=storage_rh_percent,
    )


def evaluate_wvtr_constraint(
    material: PackagingMaterialSpec,
    required_wvtr: Optional[ScientificResult],
    storage_temperature_c: Optional[float],
    storage_rh_percent: Optional[float],
) -> ConstraintEvaluation:
    """
    Evaluate WVTR hard constraint.

    Semantics (from Phase 4 moisture.py):
        WVTR_req is the MAXIMUM allowable water vapor transmission rate. The material
        must not transmit more moisture than the product can tolerate over the target
        shelf life.

    Comparison: material WVTR <= required WVTR (LE operator).
    """
    return _evaluate_barrier_constraint(
        constraint_type="water_vapor_transmission_rate",
        comparison_operator=ComparisonOperator.LE,
        requirement_result=required_wvtr,
        requirement_unit=required_wvtr.unit if required_wvtr else None,
        material=material,
        material_property_name="water_vapor_transmission_rate",
        requirement_temperature_c=storage_temperature_c,
        requirement_rh_percent=storage_rh_percent,
    )
