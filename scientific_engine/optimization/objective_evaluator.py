"""
M6-B3 Objective Evaluator.

Implements deterministic calculation of the four M6-A objectives:
1. f_thickness
2. f_moisture_margin
3. f_gas_alignment
4. f_shelf_life_margin

Does NOT optimize, rank, or combine these objectives.
"""

from typing import Dict, Optional, Tuple
from app.schemas.optimization import (
    PackagingCandidate,
    CandidateScientificEvaluationResult,
    ObjectiveValue,
    ObjectiveDirection,
    UncertaintyType
)
from app.schemas.physics import CalculationStatus
from app.schemas.constraints import ConstraintStatus

class ObjectiveEvaluator:
    
    def evaluate_objectives(
        self,
        candidate: PackagingCandidate,
        scientific_result: CandidateScientificEvaluationResult
    ) -> Dict[str, ObjectiveValue]:
        
        # M6-A Eligibility Rule: INFEASIBLE or UNKNOWN constraint candidates 
        # do not receive valid objective calculations for the Pareto front.
        # We compute them as UNKNOWN.
        is_feasible = scientific_result.constraint_profile.overall_status == ConstraintStatus.FEASIBLE
        
        objectives = {
            "f_thickness": self._calc_f_thickness(candidate, is_feasible),
            "f_moisture_margin": self._calc_f_moisture_margin(candidate, scientific_result, is_feasible),
            "f_gas_alignment": self._calc_f_gas_alignment(candidate, scientific_result, is_feasible),
            "f_shelf_life_margin": self._calc_f_shelf_life_margin(scientific_result, is_feasible)
        }
        return objectives

    def _unknown_objective(self, name: str, direction: ObjectiveDirection, unit: str, reason: str) -> ObjectiveValue:
        return ObjectiveValue(
            objective_name=name,
            direction=direction,
            value=None,
            value_min=None,
            value_max=None,
            is_interval=False,
            unit=unit,
            status=CalculationStatus.UNKNOWN,
            explanation_metadata=reason
        )

    def _calc_f_thickness(self, candidate: PackagingCandidate, is_feasible: bool) -> ObjectiveValue:
        if not is_feasible:
            return self._unknown_objective("f_thickness", ObjectiveDirection.MINIMIZE, "um", "Candidate is not feasible.")
            
        thick = candidate.decision_variables.total_thickness_um
        if thick is None or thick <= 0:
            return self._unknown_objective("f_thickness", ObjectiveDirection.MINIMIZE, "um", "Candidate thickness missing or invalid.")
            
        return ObjectiveValue(
            objective_name="f_thickness",
            direction=ObjectiveDirection.MINIMIZE,
            value=thick,
            unit="um",
            status=CalculationStatus.CALCULATED
        )

    def _calc_f_moisture_margin(
        self, 
        candidate: PackagingCandidate, 
        res: CandidateScientificEvaluationResult,
        is_feasible: bool
    ) -> ObjectiveValue:
        if not is_feasible:
            return self._unknown_objective("f_moisture_margin", ObjectiveDirection.MAXIMIZE, "dimensionless", "Candidate is not feasible.")
            
        moist_req = res.updated_moisture_requirement
        if moist_req.status == CalculationStatus.UNKNOWN or not moist_req.required_wvtr_per_area or moist_req.required_wvtr_per_area.value is None:
            return self._unknown_objective("f_moisture_margin", ObjectiveDirection.MAXIMIZE, "dimensionless", "Allowable WVTR unknown.")
            
        allowable_wvtr = moist_req.required_wvtr_per_area.value
        cand_wvtr = candidate.barrier_properties.wvtr
        
        if not cand_wvtr:
            return self._unknown_objective("f_moisture_margin", ObjectiveDirection.MAXIMIZE, "dimensionless", "Candidate WVTR missing.")
            
        if cand_wvtr.is_range and cand_wvtr.value_min is not None and cand_wvtr.value_max is not None:
            # f = (allowable - wvtr) / allowable
            val_min = (allowable_wvtr - cand_wvtr.value_max) / allowable_wvtr
            val_max = (allowable_wvtr - cand_wvtr.value_min) / allowable_wvtr
            return ObjectiveValue(
                objective_name="f_moisture_margin",
                direction=ObjectiveDirection.MAXIMIZE,
                value_min=val_min,
                value_max=val_max,
                is_interval=True,
                unit="dimensionless",
                status=CalculationStatus.CALCULATED
            )
        else:
            val = (allowable_wvtr - cand_wvtr.value) / allowable_wvtr
            return ObjectiveValue(
                objective_name="f_moisture_margin",
                direction=ObjectiveDirection.MAXIMIZE,
                value=val,
                unit="dimensionless",
                status=CalculationStatus.CALCULATED
            )

    def _calc_f_gas_alignment(
        self, 
        candidate: PackagingCandidate, 
        res: CandidateScientificEvaluationResult,
        is_feasible: bool
    ) -> ObjectiveValue:
        if not is_feasible:
            return self._unknown_objective("f_gas_alignment", ObjectiveDirection.MINIMIZE, "dimensionless", "Candidate is not feasible.")
            
        gas_req = res.updated_gas_exchange_requirement
        if gas_req.status == CalculationStatus.UNKNOWN or not gas_req.required_otr_per_area or gas_req.required_otr_per_area.value is None:
            return self._unknown_objective("f_gas_alignment", ObjectiveDirection.MINIMIZE, "dimensionless", "Target OTR unknown.")
            
        target_otr = gas_req.required_otr_per_area.value
        cand_otr = candidate.barrier_properties.otr
        if not cand_otr:
            return self._unknown_objective("f_gas_alignment", ObjectiveDirection.MINIMIZE, "dimensionless", "Candidate OTR missing.")

        cand_co2tr = candidate.barrier_properties.co2tr
        ideal_beta_res = gas_req.ideal_beta_ratio_co2_to_o2
        
        LAMBDA_BETA = 0.5
        
        def calc_alignment(otr: float, co2tr: Optional[float]) -> float:
            if target_otr == 0:
                return float('inf') # Prevent div by zero
            term1 = abs(otr - target_otr) / target_otr
            
            if ideal_beta_res and ideal_beta_res.value is not None and ideal_beta_res.value > 0 and co2tr is not None and otr > 0:
                ideal_beta = ideal_beta_res.value
                mat_beta = co2tr / otr
                term2 = LAMBDA_BETA * abs(mat_beta - ideal_beta) / ideal_beta
                return term1 + term2
            return term1

        if cand_otr.is_range and cand_otr.value_min is not None and cand_otr.value_max is not None:
            otrs = [cand_otr.value_min, cand_otr.value_max]
            co2trs = [cand_co2tr.value] if (cand_co2tr and not cand_co2tr.is_range) else \
                     ([cand_co2tr.value_min, cand_co2tr.value_max] if (cand_co2tr and cand_co2tr.is_range and cand_co2tr.value_min and cand_co2tr.value_max) else [None])
            
            vals = []
            for o in otrs:
                for c in co2trs:
                    vals.append(calc_alignment(o, c))
                    
            return ObjectiveValue(
                objective_name="f_gas_alignment",
                direction=ObjectiveDirection.MINIMIZE,
                value_min=min(vals),
                value_max=max(vals),
                is_interval=True,
                unit="dimensionless",
                status=CalculationStatus.CALCULATED
            )
        else:
            c_val = cand_co2tr.value if cand_co2tr else None
            val = calc_alignment(cand_otr.value, c_val)
            return ObjectiveValue(
                objective_name="f_gas_alignment",
                direction=ObjectiveDirection.MINIMIZE,
                value=val,
                unit="dimensionless",
                status=CalculationStatus.CALCULATED
            )

    def _calc_f_shelf_life_margin(
        self,
        res: CandidateScientificEvaluationResult,
        is_feasible: bool
    ) -> ObjectiveValue:
        if not is_feasible:
            return self._unknown_objective("f_shelf_life_margin", ObjectiveDirection.MAXIMIZE, "dimensionless", "Candidate is not feasible.")
            
        sl_req = res.candidate_shelf_life_requirement
        if sl_req.status == CalculationStatus.UNKNOWN or not sl_req.supported_calculated_shelf_life_days or sl_req.supported_calculated_shelf_life_days.value is None:
            return self._unknown_objective("f_shelf_life_margin", ObjectiveDirection.MAXIMIZE, "dimensionless", "Candidate achievable shelf life unknown.")
            
        t_achievable = sl_req.supported_calculated_shelf_life_days.value
        t_target = sl_req.target_days
        
        if t_target <= 0:
            return self._unknown_objective("f_shelf_life_margin", ObjectiveDirection.MAXIMIZE, "dimensionless", "Target shelf life missing or invalid.")
            
        if sl_req.supported_calculated_shelf_life_days.uncertainty_range is not None and sl_req.supported_calculated_shelf_life_days.minimum_value is not None and sl_req.supported_calculated_shelf_life_days.maximum_value is not None:
            v_min = (sl_req.supported_calculated_shelf_life_days.minimum_value - t_target) / t_target
            v_max = (sl_req.supported_calculated_shelf_life_days.maximum_value - t_target) / t_target
            return ObjectiveValue(
                objective_name="f_shelf_life_margin",
                direction=ObjectiveDirection.MAXIMIZE,
                value_min=v_min,
                value_max=v_max,
                is_interval=True,
                unit="dimensionless",
                status=CalculationStatus.CALCULATED
            )
        else:
            val = (t_achievable - t_target) / t_target
            return ObjectiveValue(
                objective_name="f_shelf_life_margin",
                direction=ObjectiveDirection.MAXIMIZE,
                value=val,
                unit="dimensionless",
                status=CalculationStatus.CALCULATED
            )
