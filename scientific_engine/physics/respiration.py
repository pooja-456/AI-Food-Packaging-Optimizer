"""
Model A — Respiration Kinetics Model.

Implements Michaelis-Menten-type O2-dependent respiration with CO2 inhibition
and evidence-backed empirical rate handling.

Equations:
    Base Michaelis-Menten:
        r_O2 = (Vm * [O2]) / (Km + [O2])

    Uncompetitive CO2-inhibited Michaelis-Menten:
        r_O2 = (Vm * [O2]) / (Km + (1 + [CO2] / Ki) * [O2])

    Respiration Quotient (RQ):
        r_CO2 = RQ * r_O2

Scientific Sources:
    - Peppelenbos, H. W., & Leven, J. V. (1996). Evaluation of four types of inhibition
      for modelling the influence of carbon dioxide on oxygen consumption of fruits and
      vegetables. Postharvest Biology and Technology, 7(1-2), 27-40.
    - Hertog, M. L., Peppelenbos, H. W., Evelo, R. G., & Tijskens, L. M. (1998).
      A dynamic and generic model of gas exchange of respiring produce: the effects of
      oxygen, carbon dioxide and temperature. Postharvest Biology and Technology, 14(3), 335-349.
    - Kader, A. A. (2002). Postharvest Technology of Horticultural Crops (3rd Ed.).
"""

from typing import Any, Dict, List, Optional, Tuple

from app.schemas.inference import InferredProperty
from app.schemas.physics import CalculationStatus, ScientificResult
from scientific_engine.physics.applicability import validate_gas_fractions, validate_temperature_range
from scientific_engine.physics.base import (
    MOLAR_MASS_CO2_G_MOL,
    MOLAR_MASS_O2_G_MOL,
    mg_co2_to_ml_co2,
    ml_o2_to_mg_o2,
)
from scientific_engine.physics.traceability import make_traceability
from scientific_engine.physics.uncertainty import scale_interval


class RespirationKineticsModel:
    """
    Evaluates respiration rate under modified atmosphere headspace conditions.

    If Michaelis-Menten kinetic parameters (Vm, Km, Ki) are provided with verified provenance,
    calculates dynamic gas-dependent consumption. Otherwise, utilizes evidence-derived
    respiration rates from the PropertyInferenceProfile.
    """

    MODEL_NAME = "MichaelisMentenRespirationKinetics"

    def calculate_respiration(
        self,
        inferred_respiration: Optional[InferredProperty] = None,
        o2_percent: Optional[float] = None,
        co2_percent: Optional[float] = None,
        temperature_c: Optional[float] = None,
        vm: Optional[float] = None,
        km: Optional[float] = None,
        ki: Optional[float] = None,
        rq: float = 1.0,
        parameter_sources: Optional[Dict[str, str]] = None,
    ) -> ScientificResult:
        """
        Calculate O2 consumption and CO2 evolution rates under specified headspace and temperature.

        Returns ScientificResult with status CALCULATED, PARTIALLY_CALCULATED, or UNKNOWN.
        """
        warnings: List[str] = []
        assumptions: List[str] = []
        param_sources = parameter_sources or {}

        # 1. Validate inputs and temperature range
        if temperature_c is not None:
            warnings.extend(validate_temperature_range(temperature_c, min_c=-2.0, max_c=40.0, model_name=self.MODEL_NAME))
        if o2_percent is not None or co2_percent is not None:
            o2_frac = o2_percent / 100.0 if o2_percent is not None else None
            co2_frac = co2_percent / 100.0 if co2_percent is not None else None
            warnings.extend(validate_gas_fractions(o2_frac, co2_frac, model_name=self.MODEL_NAME))

        # Case 1: Full Michaelis-Menten kinetic parameters available
        if vm is not None and km is not None and o2_percent is not None:
            o2_val = max(0.0, o2_percent)
            if ki is not None and co2_percent is not None:
                co2_val = max(0.0, co2_percent)
                # Uncompetitive CO2 inhibition
                denom = km + (1.0 + (co2_val / ki)) * o2_val
                eq_form = "r_O2 = (Vm * [O2]) / (Km + (1 + [CO2] / Ki) * [O2])"
                assumptions.append("Uncompetitive CO2 inhibition kinetics governing cytochrome oxidase pathway.")
            else:
                denom = km + o2_val
                eq_form = "r_O2 = (Vm * [O2]) / (Km + [O2])"
                assumptions.append("Standard Michaelis-Menten O2 dependency without CO2 inhibition.")

            if denom <= 0:
                return ScientificResult(
                    status=CalculationStatus.UNKNOWN,
                    traceability=make_traceability(
                        model_name=self.MODEL_NAME,
                        equation_form=eq_form,
                        failure_or_unknown_reason="Invalid kinetic parameters causing zero/negative denominator.",
                        warnings=warnings,
                    ),
                )

            r_o2_calculated = (vm * o2_val) / denom
            assumptions.append(f"Respiration quotient assumed RQ = {rq} based on aerobic carbohydrate metabolism.")

            trace = make_traceability(
                model_name=self.MODEL_NAME,
                equation_form=eq_form,
                equation_reference="Peppelenbos & Leven (1996), Postharvest Biol. Technol. 7:27-40",
                scientific_sources=["Hertog et al. (1998) Postharvest Biol. Technol. 14:335-349"],
                inputs_used={"o2_percent": o2_percent, "co2_percent": co2_percent, "temperature_c": temperature_c},
                parameters_used={"Vm": vm, "Km": km, "Ki": ki, "RQ": rq},
                parameter_sources=param_sources,
                units_used={"r_O2": "mg O2/kg/hr", "Vm": "mg O2/kg/hr", "Km": "% O2", "Ki": "% CO2"},
                validity_range={"o2_percent": (0.5, 21.0), "co2_percent": (0.0, 20.0)},
                assumptions=assumptions,
                uncertainty_description="Parametric sensitivity based on kinetic parameter confidence.",
                warnings=warnings,
            )

            return ScientificResult(
                status=CalculationStatus.CALCULATED,
                value=round(r_o2_calculated, 3),
                unit="mg O2/kg/hr",
                uncertainty_range=(round(r_o2_calculated * 0.9, 3), round(r_o2_calculated * 1.1, 3)),
                minimum_value=round(r_o2_calculated * 0.9, 3),
                maximum_value=round(r_o2_calculated * 1.1, 3),
                traceability=trace,
            )

        # Case 2: Inferred empirical respiration rate available from evidence layer
        if inferred_respiration is not None and inferred_respiration.value is not None:
            raw_r = inferred_respiration.value
            raw_unit = inferred_respiration.unit or "mg CO2/kg/hr"
            unc_range = inferred_respiration.uncertainty_range

            # Convert to mg O2/kg/hr using stoichiometric conversion
            # RQ is defined on molar/volume basis: RQ = (mol CO2) / (mol O2)
            # Therefore: mol O2 = (mol CO2) / RQ = (mass_CO2 / M_CO2) / RQ
            # mass_O2 = mol O2 * M_O2 = (mass_CO2 / RQ) * (M_O2 / M_CO2)
            eq_form_empirical = "r_O2 = (r_CO2_observed / RQ) * (M_O2 / M_CO2)"
            if "CO2" in raw_unit:
                if "ml" in raw_unit.lower() or "cc" in raw_unit.lower():
                    # raw_r is in mL CO2/kg/hr -> mL O2/kg/hr = raw_r / RQ -> mg O2/kg/hr
                    r_o2_ml = raw_r / rq
                    r_o2_val = round(ml_o2_to_mg_o2(r_o2_ml), 3)
                    r_o2_unc = (
                        round(ml_o2_to_mg_o2(unc_range[0] / rq), 3),
                        round(ml_o2_to_mg_o2(unc_range[1] / rq), 3),
                    ) if unc_range else None
                    eq_form_empirical = "r_O2 = ml_to_mg((r_CO2_ml / RQ))"
                else:
                    # raw_r is in mg CO2/kg/hr
                    conversion_factor = (MOLAR_MASS_O2_G_MOL / MOLAR_MASS_CO2_G_MOL) / rq
                    r_o2_val = round(raw_r * conversion_factor, 3)
                    r_o2_unc = (
                        round(unc_range[0] * conversion_factor, 3),
                        round(unc_range[1] * conversion_factor, 3),
                    ) if unc_range else None
            elif "ml" in raw_unit.lower() or "cc" in raw_unit.lower():
                # raw_r is in mL O2/kg/hr
                r_o2_val = round(ml_o2_to_mg_o2(raw_r), 3)
                r_o2_unc = (
                    round(ml_o2_to_mg_o2(unc_range[0]), 3),
                    round(ml_o2_to_mg_o2(unc_range[1]), 3),
                ) if unc_range else None
                eq_form_empirical = "r_O2 = ml_o2_to_mg_o2(r_O2_ml)"
            else:
                r_o2_val = round(raw_r, 3)
                r_o2_unc = unc_range
                eq_form_empirical = "r_O2 = r_O2_observed"

            assumptions.append("Direct empirical respiration rate from verified literature evidence profile.")
            assumptions.append(f"Respiration quotient assumed RQ = {rq} based on carbohydrate oxidation stoichiometry.")

            trace = make_traceability(
                model_name="EmpiricalEvidenceRespiration",
                equation_form=eq_form_empirical,
                equation_reference="Kader, A. A. (2002) Postharvest Technology of Horticultural Crops",
                scientific_sources=inferred_respiration.citations,
                inputs_used={"inferred_respiration": raw_r, "unit": raw_unit, "temperature_c": temperature_c},
                parameters_used={
                    "RQ": rq,
                    "M_O2_g_mol": MOLAR_MASS_O2_G_MOL,
                    "M_CO2_g_mol": MOLAR_MASS_CO2_G_MOL,
                },
                parameter_sources={"inferred_respiration": "Phase 3 PropertyInferenceProfile"},
                units_used={"r_O2": "mg O2/kg/hr", "r_observed": raw_unit},
                assumptions=assumptions,
                uncertainty_description="Inherited directly from Phase 3 evidence uncertainty range.",
                uncertainty_interval=r_o2_unc,
                warnings=warnings + [w.message for w in inferred_respiration.warnings],
            )

            status = (
                CalculationStatus.CALCULATED
                if inferred_respiration.status.value in ["measured", "literature"]
                else CalculationStatus.PARTIALLY_CALCULATED
            )

            return ScientificResult(
                status=status,
                value=r_o2_val,
                unit="mg O2/kg/hr",
                uncertainty_range=r_o2_unc,
                minimum_value=r_o2_unc[0] if r_o2_unc else r_o2_val,
                maximum_value=r_o2_unc[1] if r_o2_unc else r_o2_val,
                traceability=trace,
            )

        # Case 3: Respiration data completely unavailable
        return ScientificResult(
            status=CalculationStatus.UNKNOWN,
            value=None,
            unit="mg O2/kg/hr",
            traceability=make_traceability(
                model_name=self.MODEL_NAME,
                equation_form="r_O2 = f([O2], [CO2], T)",
                failure_or_unknown_reason="Neither Michaelis-Menten parameters (Vm, Km) nor empirical respiration rate available.",
                warnings=warnings + ["Respiration rate cannot be evaluated due to missing scientific evidence."],
            ),
        )
