"""
Phase 5 Candidate-Level Deterministic Hard-Constraint Evaluator.

Orchestrates barrier constraint evaluations (OTR, CO2TR, WVTR) for each
candidate material against a Phase 4 PackagingRequirementEnvelope and
produces CandidateFeasibility / FilteringResult outputs.

Does NOT rank, score, or recommend materials.
Does NOT recalculate any Phase 4 physics.
"""

import json
from pathlib import Path
from typing import List, Optional

from app.schemas.candidate_feasibility import CandidateFeasibility, FilteringResult
from app.schemas.constraints import ConstraintEvaluation, ConstraintStatus
from app.schemas.material_evidence import PackagingMaterialSpec
from app.schemas.packaging_requirements import PackagingRequirementEnvelope
from app.schemas.physics import CalculationStatus
from scientific_engine.constraints.barrier_constraints import (
    evaluate_co2tr_constraint,
    evaluate_otr_constraint,
    evaluate_wvtr_constraint,
)
from scientific_engine.physics.traceability import make_traceability


class HardConstraintEvaluator:
    """
    Deterministic hard-constraint filtering engine.

    Evaluates each candidate material against ALL applicable barrier requirements
    from a Phase 4 PackagingRequirementEnvelope and classifies each candidate as:

        FEASIBLE    — all evaluated constraints are definitively satisfied
        INFEASIBLE  — at least one constraint is definitively violated
        UNKNOWN     — no violations found, but at least one constraint is indeterminate
    """

    def evaluate_candidate(
        self,
        material: PackagingMaterialSpec,
        envelope: PackagingRequirementEnvelope,
    ) -> CandidateFeasibility:
        """
        Evaluate a single candidate material against the requirement envelope.
        """
        constraint_results: List[ConstraintEvaluation] = []
        all_warnings: List[str] = []

        storage_temp = envelope.storage_temperature_c
        storage_rh = envelope.relative_humidity_percent

        # --- OTR Constraint (area-normalised) ---
        otr_req = None
        if (
            envelope.gas_requirements.status != CalculationStatus.UNKNOWN
            and envelope.gas_requirements.required_otr_per_area is not None
        ):
            otr_req = envelope.gas_requirements.required_otr_per_area

        otr_eval = evaluate_otr_constraint(
            material=material,
            required_otr=otr_req,
            storage_temperature_c=storage_temp,
            storage_rh_percent=storage_rh,
        )
        constraint_results.append(otr_eval)
        all_warnings.extend(otr_eval.warnings)

        # --- CO2TR Constraint (area-normalised) ---
        co2tr_req = None
        if (
            envelope.gas_requirements.status != CalculationStatus.UNKNOWN
            and envelope.gas_requirements.required_co2tr_per_area is not None
        ):
            co2tr_req = envelope.gas_requirements.required_co2tr_per_area

        co2tr_eval = evaluate_co2tr_constraint(
            material=material,
            required_co2tr=co2tr_req,
            storage_temperature_c=storage_temp,
            storage_rh_percent=storage_rh,
        )
        constraint_results.append(co2tr_eval)
        all_warnings.extend(co2tr_eval.warnings)

        # --- WVTR Constraint (area-normalised) ---
        wvtr_req = None
        if (
            envelope.moisture_requirements.status != CalculationStatus.UNKNOWN
            and envelope.moisture_requirements.required_wvtr_per_area is not None
        ):
            wvtr_req = envelope.moisture_requirements.required_wvtr_per_area

        wvtr_eval = evaluate_wvtr_constraint(
            material=material,
            required_wvtr=wvtr_req,
            storage_temperature_c=storage_temp,
            storage_rh_percent=storage_rh,
        )
        constraint_results.append(wvtr_eval)
        all_warnings.extend(wvtr_eval.warnings)

        # --- Aggregate overall status ---
        passed: List[str] = []
        failed: List[str] = []
        unknown: List[str] = []

        for cr in constraint_results:
            if cr.status == ConstraintStatus.FEASIBLE:
                passed.append(cr.constraint_type)
            elif cr.status == ConstraintStatus.INFEASIBLE:
                failed.append(cr.constraint_type)
            else:
                unknown.append(cr.constraint_type)

        if failed:
            overall = ConstraintStatus.INFEASIBLE
        elif not unknown:
            overall = ConstraintStatus.FEASIBLE
        else:
            overall = ConstraintStatus.UNKNOWN

        trace = make_traceability(
            model_name="Phase5HardConstraintFilter",
            equation_form="overall = INFEASIBLE if any failed; FEASIBLE if all passed; else UNKNOWN",
            inputs_used={
                "material_id": material.material_id,
                "commodity": envelope.commodity,
                "storage_temperature_c": storage_temp,
                "storage_rh_percent": storage_rh,
            },
            parameters_used={
                "passed_count": len(passed),
                "failed_count": len(failed),
                "unknown_count": len(unknown),
            },
            assumptions=[
                "Conservative deterministic filtering: any single failure → INFEASIBLE; any unknown without failure → UNKNOWN.",
            ],
            warnings=list(dict.fromkeys(all_warnings)),
        )

        return CandidateFeasibility(
            material_id=material.material_id,
            material_name=material.material_name,
            material_category=material.material_category,
            overall_status=overall,
            constraint_results=constraint_results,
            passed_constraints=passed,
            failed_constraints=failed,
            unknown_constraints=unknown,
            warnings=list(dict.fromkeys(all_warnings)),
            traceability=trace,
        )

    def evaluate_all_candidates(
        self,
        materials: List[PackagingMaterialSpec],
        envelope: PackagingRequirementEnvelope,
    ) -> FilteringResult:
        """
        Evaluate all candidate materials and produce a complete FilteringResult.
        """
        all_results: List[CandidateFeasibility] = []
        feasible: List[CandidateFeasibility] = []
        infeasible: List[CandidateFeasibility] = []
        unknown: List[CandidateFeasibility] = []

        for mat in materials:
            result = self.evaluate_candidate(mat, envelope)
            all_results.append(result)
            if result.overall_status == ConstraintStatus.FEASIBLE:
                feasible.append(result)
            elif result.overall_status == ConstraintStatus.INFEASIBLE:
                infeasible.append(result)
            else:
                unknown.append(result)

        return FilteringResult(
            commodity=envelope.commodity,
            total_candidates_evaluated=len(materials),
            feasible_candidates=feasible,
            infeasible_candidates=infeasible,
            unknown_candidates=unknown,
            all_results=all_results,
        )


def load_reference_materials(
    json_path: Optional[str] = None,
) -> List[PackagingMaterialSpec]:
    """
    Load and validate the reference packaging materials dataset.

    Default path: data/reference/packaging_materials.json relative to project root.
    """
    if json_path is None:
        # Resolve relative to this file → project root
        project_root = Path(__file__).resolve().parent.parent.parent
        json_path = str(project_root / "data" / "reference" / "packaging_materials.json")

    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Reference material dataset not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    return [PackagingMaterialSpec(**record) for record in raw]
