"""
Model B — Gas Exchange and Equilibrium Modified Atmosphere Packaging (EMAP) Model.

Calculates required package Oxygen Transmission Rate (OTR), Carbon Dioxide Transmission
Rate (CO2TR), and ideal film selectivity ratio (beta = CO2TR / OTR) to maintain target
equilibrium headspace atmospheres.

Equations (Steady-State EMAP Mass Balance):
    O2 Mass Balance:
        OTR_pkg * (y_O2,ext - y_O2,target) = r_O2 * M_product * 24
        => OTR_pkg,req = (r_O2 * M_product * 24) / (y_O2,ext - y_O2,target)  [cc O2 / pkg / day]

    CO2 Mass Balance:
        CO2TR_pkg * (y_CO2,target - y_CO2,ext) = r_CO2 * M_product * 24
        => CO2TR_pkg,req = (RQ * r_O2 * M_product * 24) / (y_CO2,target - y_CO2,ext)  [cc CO2 / pkg / day]

    Ideal Permeability Selectivity Ratio (Beta):
        Beta = CO2TR_req / OTR_req = RQ * (y_O2,ext - y_O2,target) / (y_CO2,target - y_CO2,ext)

Scientific Sources:
    - Cameron, A. C., Talasila, P. C., & Joles, D. W. (1995). Predicting film permeance
      requirements for modified atmosphere packaging of fresh produce. HortTechnology, 5(1), 25-34.
    - Exama, A., Arul, J., Lencki, R. W., Lee, Z. Z., & Toupin, C. (1993). Suitability of plastic
      films for modified atmosphere packaging of fruits and vegetables. Journal of Food Science, 58(6), 1365-1370.
    - Robertson, G. L. (2012). Food Packaging: Principles and Practice (3rd Ed.), CRC Press.
"""

from typing import Any, Dict, List, Optional, Tuple

from app.schemas.packaging_requirements import GasExchangeRequirement
from app.schemas.physics import CalculationStatus, ScientificResult
from scientific_engine.physics.applicability import validate_gas_fractions
from scientific_engine.physics.base import mg_o2_to_ml_o2
from scientific_engine.physics.traceability import make_traceability
from scientific_engine.physics.uncertainty import scale_interval


# Standard atmospheric gas compositions
AMBIENT_O2_PERCENT = 20.9
AMBIENT_CO2_PERCENT = 0.04


class GasExchangeModel:
    """
    Computes required gas transmission rates for modified atmosphere preservation.
    """

    MODEL_NAME = "SteadyStateEMAPGasExchange"

    def calculate_gas_requirements(
        self,
        respiration_result: ScientificResult,
        target_o2_percent: Optional[float] = 3.0,
        target_co2_percent: Optional[float] = 5.0,
        target_o2_range: Optional[Tuple[float, float]] = (2.0, 5.0),
        target_co2_range: Optional[Tuple[float, float]] = (3.0, 8.0),
        product_mass_kg: Optional[float] = None,
        package_area_m2: Optional[float] = None,
        rq: float = 1.0,
    ) -> GasExchangeRequirement:
        """
        Calculate required OTR, CO2TR, and ideal Beta ratio.

        If product mass is missing, produces PARTIALLY_CALCULATED with per-kg metrics.
        If respiration is UNKNOWN, produces UNKNOWN.
        """
        warnings: List[str] = []
        assumptions: List[str] = []

        # 1. If respiration is unknown, gas exchange cannot be determined
        if respiration_result.status == CalculationStatus.UNKNOWN or respiration_result.value is None:
            return GasExchangeRequirement(
                status=CalculationStatus.UNKNOWN,
                target_o2_percent=target_o2_percent,
                target_o2_range=target_o2_range,
                target_co2_percent=target_co2_percent,
                target_co2_range=target_co2_range,
                warnings=["Respiration rate is UNKNOWN; gas exchange requirements cannot be calculated."],
                traceability=make_traceability(
                    model_name=self.MODEL_NAME,
                    equation_form="OTR_req = (r_O2 * M * 24) / (y_O2,ext - y_O2,target)",
                    failure_or_unknown_reason="Respiration rate is UNKNOWN.",
                ),
            )

        # 2. Check target gas atmospheres
        y_o2_tgt = target_o2_percent / 100.0 if target_o2_percent is not None else 0.03
        y_co2_tgt = target_co2_percent / 100.0 if target_co2_percent is not None else 0.05
        y_o2_ext = AMBIENT_O2_PERCENT / 100.0
        y_co2_ext = AMBIENT_CO2_PERCENT / 100.0

        warnings.extend(validate_gas_fractions(y_o2_tgt, y_co2_tgt, model_name=self.MODEL_NAME))

        delta_y_o2 = y_o2_ext - y_o2_tgt
        delta_y_co2 = y_co2_tgt - y_co2_ext

        if delta_y_o2 <= 0.001 or delta_y_co2 <= 0.001:
            warnings.append("Target atmosphere gradients are zero or negative relative to ambient air.")
            return GasExchangeRequirement(
                status=CalculationStatus.UNKNOWN,
                warnings=warnings,
                traceability=make_traceability(
                    model_name=self.MODEL_NAME,
                    equation_form="OTR_req = (r_O2 * M * 24) / delta_y_O2",
                    failure_or_unknown_reason="Invalid target gas gradient (driving force <= 0).",
                ),
            )

        # 3. Calculate ideal Beta ratio (independent of product mass and area!)
        ideal_beta = rq * (delta_y_o2 / delta_y_co2)
        beta_trace = make_traceability(
            model_name=self.MODEL_NAME,
            equation_form="Beta = RQ * (y_O2,ext - y_O2,target) / (y_CO2,target - y_CO2,ext)",
            equation_reference="Exama et al. (1993) J. Food Sci. 58:1365-1370",
            inputs_used={
                "target_o2_percent": target_o2_percent,
                "target_co2_percent": target_co2_percent,
                "ambient_o2_percent": AMBIENT_O2_PERCENT,
                "ambient_co2_percent": AMBIENT_CO2_PERCENT,
            },
            parameters_used={"RQ": rq},
            assumptions=["Steady-state gas exchange equilibrium (influx = consumption; efflux = generation)."],
        )
        beta_result = ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=round(ideal_beta, 2),
            unit="dimensionless (CO2TR / OTR)",
            traceability=beta_trace,
        )

        # 4. Convert respiration rate from mg O2/kg/hr to mL O2/kg/day
        # Note: If respiration unit was mg O2/kg/hr:
        r_o2_mg_kg_hr = respiration_result.value
        r_o2_ml_kg_hr = mg_o2_to_ml_o2(r_o2_mg_kg_hr)
        r_o2_ml_kg_day = r_o2_ml_kg_hr * 24.0

        r_unc_ml_day = None
        if respiration_result.uncertainty_range:
            unc_min_ml = mg_o2_to_ml_o2(respiration_result.uncertainty_range[0]) * 24.0
            unc_max_ml = mg_o2_to_ml_o2(respiration_result.uncertainty_range[1]) * 24.0
            r_unc_ml_day = (unc_min_ml, unc_max_ml)

        # 5. Check if product mass is supplied
        if product_mass_kg is None or product_mass_kg <= 0:
            # PARTIALLY_CALCULATED: We know required OTR per kg, but not absolute whole-package OTR
            otr_per_kg = round(r_o2_ml_kg_day / delta_y_o2, 1)
            co2tr_per_kg = round((rq * r_o2_ml_kg_day) / delta_y_co2, 1)

            otr_pkg_trace = make_traceability(
                model_name=self.MODEL_NAME,
                equation_form="OTR_req_per_kg = (r_O2 * 24) / (y_O2,ext - y_O2,target)",
                equation_reference="Cameron et al. (1995) HortTechnology 5:25-34",
                inputs_used={
                    "respiration_rate_mg_o2_kg_hr": r_o2_mg_kg_hr,
                    "target_o2_percent": target_o2_percent,
                    "target_co2_percent": target_co2_percent,
                },
                units_used={"OTR_req_per_kg": "cc O2 / (kg product · day)"},
                failure_or_unknown_reason="Package product mass (kg) not provided; computed on per-kg basis only.",
                assumptions=["Headspace equilibrium reached without transient hypoxic period."],
                warnings=warnings + ["Product mass missing: whole-package OTR requirement is PARTIALLY_CALCULATED."],
            )

            otr_pkg_result = ScientificResult(
                status=CalculationStatus.PARTIALLY_CALCULATED,
                value=otr_per_kg,
                unit="cc O2 / (kg product · day)",
                traceability=otr_pkg_trace,
            )
            co2tr_pkg_result = ScientificResult(
                status=CalculationStatus.PARTIALLY_CALCULATED,
                value=co2tr_per_kg,
                unit="cc CO2 / (kg product · day)",
                traceability=otr_pkg_trace,
            )

            return GasExchangeRequirement(
                status=CalculationStatus.PARTIALLY_CALCULATED,
                target_o2_percent=target_o2_percent,
                target_o2_range=target_o2_range,
                target_co2_percent=target_co2_percent,
                target_co2_range=target_co2_range,
                required_otr_cc_per_pkg_day=otr_pkg_result,
                required_co2tr_cc_per_pkg_day=co2tr_pkg_result,
                ideal_beta_ratio_co2_to_o2=beta_result,
                traceability=otr_pkg_trace,
                warnings=warnings + ["Product mass not provided: gas exchange is PARTIALLY_CALCULATED per kg."],
            )

        # 6. Complete calculation with product mass
        total_o2_consumption_ml_day = r_o2_ml_kg_day * product_mass_kg
        total_co2_evolution_ml_day = rq * total_o2_consumption_ml_day

        required_otr_pkg = total_o2_consumption_ml_day / delta_y_o2
        required_co2tr_pkg = total_co2_evolution_ml_day / delta_y_co2

        otr_unc_pkg = None
        if r_unc_ml_day:
            otr_unc_pkg = (
                round((r_unc_ml_day[0] * product_mass_kg) / delta_y_o2, 1),
                round((r_unc_ml_day[1] * product_mass_kg) / delta_y_o2, 1),
            )

        assumptions.extend([
            "Steady-state gas exchange equilibrium.",
            f"Product mass = {product_mass_kg} kg.",
            f"Ambient atmosphere: O2 = {AMBIENT_O2_PERCENT}%, CO2 = {AMBIENT_CO2_PERCENT}%.",
        ])

        otr_trace = make_traceability(
            model_name=self.MODEL_NAME,
            equation_form="OTR_req = (r_O2 * M_product * 24) / (y_O2,ext - y_O2,target)",
            equation_reference="Cameron et al. (1995) HortTechnology 5:25-34",
            inputs_used={
                "r_O2_mg_kg_hr": r_o2_mg_kg_hr,
                "product_mass_kg": product_mass_kg,
                "target_o2_percent": target_o2_percent,
                "target_co2_percent": target_co2_percent,
            },
            parameters_used={"RQ": rq, "ambient_O2_%": AMBIENT_O2_PERCENT, "ambient_CO2_%": AMBIENT_CO2_PERCENT},
            units_used={"OTR_req": "cc O2 / package / day", "CO2TR_req": "cc CO2 / package / day"},
            assumptions=assumptions,
            uncertainty_interval=otr_unc_pkg,
            warnings=warnings,
        )

        otr_pkg_result = ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=round(required_otr_pkg, 1),
            unit="cc O2 / package / day",
            uncertainty_range=otr_unc_pkg,
            minimum_value=otr_unc_pkg[0] if otr_unc_pkg else round(required_otr_pkg, 1),
            maximum_value=otr_unc_pkg[1] if otr_unc_pkg else round(required_otr_pkg, 1),
            traceability=otr_trace,
        )

        co2tr_pkg_result = ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=round(required_co2tr_pkg, 1),
            unit="cc CO2 / package / day",
            traceability=otr_trace,
        )

        # 7. If package area is supplied, calculate normalized OTR (cc / (m² · day · atm))
        otr_area_result = None
        co2tr_area_result = None
        if package_area_m2 is not None and package_area_m2 > 0:
            normalized_otr = required_otr_pkg / package_area_m2
            normalized_co2tr = required_co2tr_pkg / package_area_m2
            otr_area_result = ScientificResult(
                status=CalculationStatus.CALCULATED,
                value=round(normalized_otr, 1),
                unit="cc / (m² · day · atm)",
                traceability=otr_trace,
            )
            co2tr_area_result = ScientificResult(
                status=CalculationStatus.CALCULATED,
                value=round(normalized_co2tr, 1),
                unit="cc / (m² · day · atm)",
                traceability=otr_trace,
            )

        return GasExchangeRequirement(
            status=CalculationStatus.CALCULATED,
            target_o2_percent=target_o2_percent,
            target_o2_range=target_o2_range,
            target_co2_percent=target_co2_percent,
            target_co2_range=target_co2_range,
            required_otr_cc_per_pkg_day=otr_pkg_result,
            required_otr_per_area=otr_area_result,
            required_co2tr_cc_per_pkg_day=co2tr_pkg_result,
            required_co2tr_per_area=co2tr_area_result,
            ideal_beta_ratio_co2_to_o2=beta_result,
            traceability=otr_trace,
            warnings=warnings,
        )
