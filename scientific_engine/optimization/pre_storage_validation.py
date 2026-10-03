"""
M6-I (B5C): Precomputed Optimization-State Pre-Storage Validation Implementation.

Provides deterministic, observational validation for PrecomputedOptimizationState records
before they are accepted by the B5A state store.

Adheres strictly to docs/m6b5c_precomputed_state_generation_contract.md Section 12:
- Pure validation: ZERO scientific recalculations, ZERO Phase 5 constraint checks, ZERO Pareto recalculations.
- Observational: ZERO mutation of the input state.
- Validates Identity completeness, Search-space consistency, Objective-set consistency,
  ParetoFront structural integrity, and Interval bound ordering.
- Preserves valid empty ParetoFront objects (candidate_count == 0).
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

from app.schemas.physics import CalculationStatus, ScientificResult
from app.schemas.packaging_requirements import PackagingRequirementEnvelope
from scientific_engine.optimization.canonical_representation import (
    build_canonical_representation
)

if TYPE_CHECKING:
    from scientific_engine.optimization.precomputed_store import (
        PrecomputedOptimizationState
    )


class PreStorageValidationResult(BaseModel):
    """Result object returned by B5C pre-storage validation."""

    is_valid: bool = Field(..., description="True if the state passes all B5C pre-storage contract checks.")
    reasons: List[str] = Field(default_factory=list, description="List of deterministic validation failure reasons if invalid.")


class PreStorageValidator:
    """
    B5C Pre-Storage Validator.
    Validates structural and contractual integrity of an ALREADY-COMPUTED optimization state.
    Does NOT recalculate physics, objectives, constraints, or Pareto dominance.
    """

    def validate(self, state: PrecomputedOptimizationState) -> PreStorageValidationResult:
        reasons: List[str] = []

        # 1. Identity Completeness
        if state.requirement_envelope is None:
            reasons.append("Missing required identity component: requirement_envelope is None")
        if state.package_geometry is None:
            reasons.append("Missing required identity component: package_geometry is None")
        if not state.active_objectives:
            reasons.append("Missing required identity component: active_objectives is empty or None")
        if not state.eligible_candidate_materials:
            reasons.append("Missing required identity component: eligible_candidate_materials is empty or None")

        # Early return if basic identity fields are missing to prevent downstream null errors
        if reasons:
            return PreStorageValidationResult(is_valid=False, reasons=reasons)

        # 2. Canonical Representation Consistency
        try:
            build_canonical_representation(
                requirement_envelope=state.requirement_envelope,
                package_geometry=state.package_geometry,
                active_objectives=state.active_objectives,
                eligible_candidate_materials=state.eligible_candidate_materials
            )
        except Exception as e:
            reasons.append(f"Canonical representation construction failed: {str(e)}")

        # 3. Active Objectives Integrity (No duplicate objective strings)
        if len(state.active_objectives) != len(set(state.active_objectives)):
            reasons.append("Active objective set contains duplicate objective identifiers")

        active_obj_set = set(state.active_objectives)

        # 4. Eligible Candidate Set Integrity
        eligible_ids: Set[str] = set()
        for cand in state.eligible_candidate_materials:
            if not cand.candidate_id:
                reasons.append("Eligible candidate material found with empty or None candidate_id")
            else:
                eligible_ids.add(cand.candidate_id)

        # 5. ParetoFront Structural Integrity
        if state.pareto_front is None:
            reasons.append("Missing required result component: pareto_front is None")
        else:
            pf = state.pareto_front
            
            # Check candidate count consistency
            if pf.candidate_count != len(pf.candidates):
                reasons.append(
                    f"ParetoFront candidate_count mismatch: candidate_count={pf.candidate_count} "
                    f"but len(candidates)={len(pf.candidates)}"
                )

            # Check each Pareto candidate
            for cand in pf.candidates:
                cand_id = getattr(cand, "candidate_id", None)
                if cand_id is None and hasattr(cand, "candidate_design") and cand.candidate_design:
                    cand_id = cand.candidate_design.candidate_id
                if cand_id is None and hasattr(cand, "pareto_candidate_id"):
                    cand_id = cand.pareto_candidate_id

                if not cand_id:
                    reasons.append("ParetoCandidate found with missing candidate_id")
                elif cand_id not in eligible_ids:
                    reasons.append(
                        f"Search-space inconsistency: Candidate '{cand_id}' in ParetoFront "
                        f"is not present in eligible_candidate_materials"
                    )

                # Objective-set consistency
                if hasattr(cand, "objective_values") and cand.objective_values is not None:
                    cand_objs = set(cand.objective_values.keys())
                    
                    # Check for unauthorized objectives in candidate
                    unauthorized_objs = cand_objs - active_obj_set
                    if unauthorized_objs:
                        reasons.append(
                            f"Objective-set inconsistency: Candidate '{cand_id}' contains "
                            f"unauthorized objectives: {sorted(list(unauthorized_objs))}"
                        )
                    
                    # Check for missing active objectives in candidate
                    missing_objs = active_obj_set - cand_objs
                    if missing_objs:
                        reasons.append(
                            f"Objective-set inconsistency: Candidate '{cand_id}' missing "
                            f"active objectives: {sorted(list(missing_objs))}"
                        )

        # 6. Interval Structural Correctness (lower <= upper when both exist)
        self._validate_requirement_intervals(state.requirement_envelope, reasons)

        is_valid = (len(reasons) == 0)
        return PreStorageValidationResult(is_valid=is_valid, reasons=reasons)

    def _validate_scientific_result_interval(
        self, sr: Optional[ScientificResult], field_name: str, reasons: List[str]
    ) -> None:
        if sr is not None and sr.minimum_value is not None and sr.maximum_value is not None:
            if sr.minimum_value > sr.maximum_value:
                reasons.append(
                    f"Invalid interval in {field_name}: lower bound ({sr.minimum_value}) "
                    f"> upper bound ({sr.maximum_value})"
                )

    def _validate_requirement_intervals(
        self, env: PackagingRequirementEnvelope, reasons: List[str]
    ) -> None:
        if env.gas_requirements:
            gr = env.gas_requirements
            self._validate_scientific_result_interval(gr.required_otr_cc_per_pkg_day, "gas_requirements.required_otr_cc_per_pkg_day", reasons)
            self._validate_scientific_result_interval(gr.required_otr_per_area, "gas_requirements.required_otr_per_area", reasons)
            self._validate_scientific_result_interval(gr.required_co2tr_cc_per_pkg_day, "gas_requirements.required_co2tr_cc_per_pkg_day", reasons)
            self._validate_scientific_result_interval(gr.required_co2tr_per_area, "gas_requirements.required_co2tr_per_area", reasons)

        if env.moisture_requirements:
            mr = env.moisture_requirements
            self._validate_scientific_result_interval(mr.water_vapor_pressure_gradient_kpa, "moisture_requirements.water_vapor_pressure_gradient_kpa", reasons)
            self._validate_scientific_result_interval(mr.moisture_transfer_rate_g_day, "moisture_requirements.moisture_transfer_rate_g_day", reasons)
            self._validate_scientific_result_interval(mr.required_wvtr_g_per_pkg_day, "moisture_requirements.required_wvtr_g_per_pkg_day", reasons)
            self._validate_scientific_result_interval(mr.required_wvtr_per_area, "moisture_requirements.required_wvtr_per_area", reasons)


def validate_precomputed_state_b5c(state: PrecomputedOptimizationState) -> PreStorageValidationResult:
    """Convenience function to execute B5C pre-storage validation."""
    validator = PreStorageValidator()
    return validator.validate(state)
