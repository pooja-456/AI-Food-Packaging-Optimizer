"""
Model C — Moisture Transfer and Water Activity Dynamics Model.

Calculates water vapor pressure gradients (Δp_w), allowable moisture flux,
required package Water Vapor Transmission Rate (WVTR), and moisture-limited shelf life.

Equations:
    Saturation Vapor Pressure (Tetens / Buck Formulation):
        Psat(T) = 0.61078 * exp((17.27 * T) / (T + 237.3))  [kPa, for T >= 0 °C (over liquid water)]
        Psat(T) = 0.61078 * exp((21.875 * T) / (T + 265.5)) [kPa, for T < 0 °C (over ice)]

    Vapor Pressure Gradient Driving Force:
        p_w,ext = (RH_ext / 100) * Psat(T)
        p_w,int = aw * Psat(T)
        Δp_w = |p_w,ext - p_w,int|  [kPa]

    Allowable Moisture Gain / Loss:
        ΔM_H2O = |m_crit - m_init| * (M_dry / 100)  [g H2O]

    Required Whole-Package WVTR:
        WVTR_pkg,req = ΔM_H2O / t_target  [g H2O / package / day]

    Normalized WVTR (if package area A is specified):
        WVTR_area,req = WVTR_pkg,req / A  [g H2O / (m² · day)]

    Moisture-Limited Shelf Life (if package WVTR is specified):
        t_shelf,moisture = ΔM_H2O / WVTR_pkg  [days]

Scientific Sources:
    - Labuza, T. P., & Contreras-Medellin, R. (1981). Prediction of moisture protection
      requirements for foods. Cereal Foods World, 26(7), 335-343.
    - Robertson, G. L. (2012). Food Packaging: Principles and Practice (3rd Ed.), CRC Press.
    - Bell, L. N., & Labuza, T. P. (2000). Moisture Sorption: Practical Aspects of Isotherm
      Measurement and Use (2nd Ed.). AACC International.
"""

from typing import Any, Dict, List, Optional, Tuple

from app.schemas.packaging_requirements import MoistureRequirement
from app.schemas.physics import CalculationStatus, ScientificResult
from scientific_engine.physics.applicability import (
    validate_relative_humidity,
    validate_temperature_range,
    validate_water_activity,
)
from scientific_engine.physics.base import (
    food_surface_vapor_pressure_kpa,
    water_saturation_vapor_pressure_kpa,
    water_vapor_pressure_kpa,
)
from scientific_engine.physics.sorption import MoistureSorptionModel
from scientific_engine.physics.traceability import make_traceability


class MoistureTransferModel:
    """
    Computes vapor pressure gradients and required water vapor barrier requirements.
    """

    MODEL_NAME = "VaporPressureMoistureTransfer"

    def calculate_moisture_requirements(
        self,
        initial_water_activity: Optional[float] = None,
        critical_water_activity: Optional[float] = None,
        initial_moisture_percent: Optional[float] = None,
        critical_moisture_percent: Optional[float] = None,
        storage_temperature_c: Optional[float] = 20.0,
        relative_humidity_percent: Optional[float] = 65.0,
        target_shelf_life_days: Optional[int] = None,
        dry_mass_g: Optional[float] = None,
        package_area_m2: Optional[float] = None,
        package_wvtr_g_pkg_day: Optional[float] = None,
        sorption_model: Optional[MoistureSorptionModel] = None,
    ) -> MoistureRequirement:
        """
        Calculate moisture requirements based on thermodynamics and water activity gradients.
        """
        warnings: List[str] = []
        assumptions: List[str] = []

        # 1. Validation of environmental parameters
        if storage_temperature_c is not None:
            warnings.extend(validate_temperature_range(storage_temperature_c, min_c=-20.0, max_c=50.0, model_name=self.MODEL_NAME))
        if relative_humidity_percent is not None:
            warnings.extend(validate_relative_humidity(relative_humidity_percent, model_name=self.MODEL_NAME))
        if initial_water_activity is not None:
            warnings.extend(validate_water_activity(initial_water_activity, model_name=self.MODEL_NAME))
        if critical_water_activity is not None:
            warnings.extend(validate_water_activity(critical_water_activity, model_name=self.MODEL_NAME))

        # Check if water activity or moisture is known
        if initial_water_activity is None and initial_moisture_percent is None:
            return MoistureRequirement(
                status=CalculationStatus.UNKNOWN,
                initial_water_activity=None,
                critical_water_activity=critical_water_activity,
                warnings=["Initial water activity (aw) and moisture content are both UNKNOWN."],
                traceability=make_traceability(
                    model_name=self.MODEL_NAME,
                    equation_form="Δp_w = |(RH_ext/100) * Psat(T) - aw * Psat(T)|",
                    failure_or_unknown_reason="Missing initial water activity and moisture content.",
                ),
            )

        temp_c = storage_temperature_c if storage_temperature_c is not None else 20.0
        rh_pct = relative_humidity_percent if relative_humidity_percent is not None else 65.0

        # 2. Compute equilibrium vapor pressure and driving force Δp_w if aw is available
        p_sat = water_saturation_vapor_pressure_kpa(temp_c)
        p_ext = water_vapor_pressure_kpa(temp_c, rh_pct)

        aw_est = initial_water_activity
        delta_p_result = None

        if aw_est is not None:
            p_food = food_surface_vapor_pressure_kpa(temp_c, aw_est)
            delta_p = abs(p_ext - p_food)
            delta_p_trace = make_traceability(
                model_name=self.MODEL_NAME,
                equation_form="Δp_w = |(RH_ext/100)*Psat(T) - aw*Psat(T)|",
                equation_reference="Tetens (1930); Labuza & Contreras-Medellin (1981)",
                inputs_used={"aw": aw_est, "temperature_c": temp_c, "relative_humidity_percent": rh_pct},
                parameters_used={"Psat_kPa": round(p_sat, 4)},
                units_used={"Δp_w": "kPa", "Psat": "kPa", "p_ext": "kPa", "p_food": "kPa"},
                assumptions=["Raoult's law equilibrium at food-headspace boundary."],
            )
            delta_p_result = ScientificResult(
                status=CalculationStatus.CALCULATED,
                value=round(delta_p, 4),
                unit="kPa",
                traceability=delta_p_trace,
            )
        else:
            warnings.append("Initial water activity aw is unmeasured; vapor pressure gradient cannot be fully determined.")

        # 3. Moisture gain/loss calculation
        m_init = initial_moisture_percent
        m_crit = critical_moisture_percent

        if m_init is None and sorption_model is not None and aw_est is not None:
            m_res = sorption_model.calculate_moisture_content(aw_est, temp_c)
            if m_res.status == CalculationStatus.CALCULATED and m_res.value is not None:
                m_init = m_res.value

        if m_crit is None and sorption_model is not None and critical_water_activity is not None:
            m_crit_res = sorption_model.calculate_moisture_content(critical_water_activity, temp_c)
            if m_crit_res.status == CalculationStatus.CALCULATED and m_crit_res.value is not None:
                m_crit = m_crit_res.value

        # Check if we have complete information for required WVTR
        if m_init is not None and m_crit is not None and dry_mass_g is not None:
            delta_m_percent = abs(m_crit - m_init)
            delta_m_grams_h2o = delta_m_percent * (dry_mass_g / 100.0)

            wvtr_pkg_result = None
            wvtr_area_result = None
            allowable_flux_g_day = None

            if target_shelf_life_days is not None and target_shelf_life_days > 0:
                allowable_flux_g_day = delta_m_grams_h2o / float(target_shelf_life_days)
                required_wvtr_pkg = allowable_flux_g_day

                wvtr_trace = make_traceability(
                    model_name=self.MODEL_NAME,
                    equation_form="WVTR_req = [|m_crit - m_init| * (M_dry / 100)] / t_target",
                    equation_reference="Labuza, T. P. (1984) Moisture Sorption",
                    inputs_used={
                        "m_init_%": m_init,
                        "m_crit_%": m_crit,
                        "dry_mass_g": dry_mass_g,
                        "target_shelf_life_days": target_shelf_life_days,
                    },
                    units_used={"WVTR_pkg_req": "g H2O / package / day", "ΔM_H2O": "g"},
                    assumptions=[f"Dry solid product mass = {dry_mass_g} g.", f"Target shelf life = {target_shelf_life_days} days."],
                )

                wvtr_pkg_result = ScientificResult(
                    status=CalculationStatus.CALCULATED,
                    value=round(required_wvtr_pkg, 4),
                    unit="g H2O / package / day",
                    traceability=wvtr_trace,
                )

                if package_area_m2 is not None and package_area_m2 > 0:
                    norm_wvtr = required_wvtr_pkg / package_area_m2
                    wvtr_area_result = ScientificResult(
                        status=CalculationStatus.CALCULATED,
                        value=round(norm_wvtr, 3),
                        unit="g / (m² · day)",
                        traceability=wvtr_trace,
                    )

            # If existing package WVTR was supplied, calculate moisture shelf-life
            shelf_life_res = None
            if package_wvtr_g_pkg_day is not None and package_wvtr_g_pkg_day > 0:
                t_moisture = delta_m_grams_h2o / package_wvtr_g_pkg_day
                sl_trace = make_traceability(
                    model_name=self.MODEL_NAME,
                    equation_form="t_shelf = ΔM_H2O / WVTR_pkg",
                    equation_reference="Labuza & Contreras-Medellin (1981)",
                    inputs_used={"ΔM_H2O_g": delta_m_grams_h2o, "WVTR_pkg": package_wvtr_g_pkg_day},
                    units_used={"t_shelf": "days"},
                )
                shelf_life_res = ScientificResult(
                    status=CalculationStatus.CALCULATED,
                    value=round(t_moisture, 1),
                    unit="days",
                    traceability=sl_trace,
                )

            # Determine overall status
            overall_status = CalculationStatus.CALCULATED if (wvtr_pkg_result or shelf_life_res) else CalculationStatus.PARTIALLY_CALCULATED

            main_trace = wvtr_pkg_result.traceability if wvtr_pkg_result else (shelf_life_res.traceability if shelf_life_res else delta_p_result.traceability if delta_p_result else make_traceability(model_name=self.MODEL_NAME, equation_form="ΔM_H2O"))

            return MoistureRequirement(
                status=overall_status,
                initial_water_activity=aw_est,
                critical_water_activity=critical_water_activity,
                water_vapor_pressure_gradient_kpa=delta_p_result,
                moisture_transfer_rate_g_day=ScientificResult(
                    status=CalculationStatus.CALCULATED,
                    value=round(allowable_flux_g_day, 4),
                    unit="g H2O / day",
                    traceability=main_trace,
                ) if allowable_flux_g_day else None,
                required_wvtr_g_per_pkg_day=wvtr_pkg_result,
                required_wvtr_per_area=wvtr_area_result,
                moisture_limited_shelf_life_days=shelf_life_res,
                traceability=main_trace,
                warnings=warnings,
            )

        # Incomplete inputs for full WVTR calculation (e.g. dry mass or critical moisture missing)
        return MoistureRequirement(
            status=CalculationStatus.PARTIALLY_CALCULATED,
            initial_water_activity=aw_est,
            critical_water_activity=critical_water_activity,
            water_vapor_pressure_gradient_kpa=delta_p_result,
            warnings=warnings + ["Critical moisture limit or dry product mass missing: required WVTR is PARTIALLY_CALCULATED."],
            traceability=delta_p_result.traceability if delta_p_result else make_traceability(model_name=self.MODEL_NAME, equation_form="Δp_w"),
        )
