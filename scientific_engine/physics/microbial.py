"""
Model D — Evidence-Gated Predictive Microbial Growth Framework.

Calculates microbial growth kinetics, adaptation lag phases, and microbial-limited
shelf life when verified organism parameters (N0, Ncrit, µmax, lag) exist.

Equations:
    Primary Growth Kinetics (Linear log-phase with lag):
        For t <= λ:
            log10(N(t)) = log10(N0)
        For t > λ:
            log10(N(t)) = log10(N0) + (µmax / ln(10)) * (t - λ)

    Time to Reach Spoilage / Safety Limit:
        t_microbial = λ + [log10(Ncrit) - log10(N0)] / (µmax / ln(10))  [days]

    Secondary Temperature Dependence (Ratkowsky Square-Root Model):
        sqrt(µmax(T)) = b * (T - Tmin)

Scientific Sources:
    - Baranyi, J., & Roberts, T. A. (1994). A dynamic approach to predicting bacterial growth
      in food. International Journal of Food Microbiology, 23(3-4), 277-294.
    - Ratkowsky, D. A., Olley, J., McMeekin, T. A., & Ball, A. (1982). Relationship between
      temperature and growth rate of bacterial cultures. Journal of Bacteriology, 149(1), 1-5.
    - McMeekin, T. A., et al. (1993). Predictive Microbiology: Theory and Application. Research Studies Press.
"""

import math
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.packaging_requirements import MicrobialRequirement
from app.schemas.physics import CalculationStatus, ScientificResult
from scientific_engine.physics.applicability import validate_temperature_range, validate_water_activity
from scientific_engine.physics.traceability import make_traceability


class MicrobialGrowthModel:
    """
    Evidence-gated predictive microbial growth calculator.

    Strictly returns status=UNKNOWN unless verified organism-specific parameters exist.
    """

    MODEL_NAME = "PredictiveMicrobialGrowthFramework"

    def calculate_microbial_limits(
        self,
        target_microorganism: Optional[str] = None,
        initial_count_log_cfu: Optional[float] = None,
        critical_count_log_cfu: Optional[float] = None,
        growth_rate_per_day: Optional[float] = None,
        lag_time_days: Optional[float] = 0.0,
        temperature_c: Optional[float] = None,
        ph: Optional[float] = None,
        water_activity: Optional[float] = None,
        ratkowsky_b: Optional[float] = None,
        ratkowsky_tmin_c: Optional[float] = None,
        co2_inhibition_factor: Optional[float] = None,
        parameter_sources: Optional[Dict[str, str]] = None,
    ) -> MicrobialRequirement:
        """
        Evaluate microbial proliferation and shelf-life limit.
        """
        warnings: List[str] = []
        assumptions: List[str] = []
        param_sources = parameter_sources or {}

        if temperature_c is not None:
            warnings.extend(validate_temperature_range(temperature_c, min_c=-5.0, max_c=45.0, model_name=self.MODEL_NAME))
        if water_activity is not None:
            warnings.extend(validate_water_activity(water_activity, model_name=self.MODEL_NAME))

        # Check for minimum required parameters: target organism, initial count, critical count, growth rate
        if target_microorganism is None or initial_count_log_cfu is None or critical_count_log_cfu is None:
            return MicrobialRequirement(
                status=CalculationStatus.UNKNOWN,
                target_microorganism=target_microorganism,
                initial_count_log_cfu=initial_count_log_cfu,
                critical_count_log_cfu=critical_count_log_cfu,
                warnings=["Target microorganism, initial count (log CFU/g), or critical threshold is UNKNOWN."],
                traceability=make_traceability(
                    model_name=self.MODEL_NAME,
                    equation_form="t_microbial = λ + [log10(Ncrit) - log10(N0)] / (µmax / ln(10))",
                    failure_or_unknown_reason="Missing organism-specific baseline parameters (N0, Ncrit, or µmax).",
                ),
            )

        # Growth rate derivation: direct µmax or Ratkowsky square-root model
        mu = growth_rate_per_day
        if mu is None and ratkowsky_b is not None and ratkowsky_tmin_c is not None and temperature_c is not None:
            if temperature_c <= ratkowsky_tmin_c:
                mu = 0.0
                assumptions.append(f"Temperature ({temperature_c}°C) <= Tmin ({ratkowsky_tmin_c}°C); no growth.")
            else:
                sqrt_mu = ratkowsky_b * (temperature_c - ratkowsky_tmin_c)
                mu = sqrt_mu * sqrt_mu
                assumptions.append("Growth rate derived via Ratkowsky square-root temperature model.")

        if mu is None or mu < 0:
            return MicrobialRequirement(
                status=CalculationStatus.PARTIALLY_CALCULATED,
                target_microorganism=target_microorganism,
                initial_count_log_cfu=initial_count_log_cfu,
                critical_count_log_cfu=critical_count_log_cfu,
                warnings=warnings + ["Specific growth rate (µmax) could not be evaluated from evidence."],
                traceability=make_traceability(
                    model_name=self.MODEL_NAME,
                    equation_form="sqrt(µmax) = b * (T - Tmin)",
                    failure_or_unknown_reason="Missing specific growth rate µmax or Ratkowsky parameters.",
                ),
            )

        # Atmosphere inhibition factor (e.g. high CO2 reduces µmax by factor)
        if co2_inhibition_factor is not None and 0.0 < co2_inhibition_factor <= 1.0:
            mu = mu * co2_inhibition_factor
            assumptions.append(f"Growth rate adjusted by CO2 hurdle inhibition factor = {co2_inhibition_factor}.")

        lag = lag_time_days if lag_time_days is not None else 0.0
        delta_log = critical_count_log_cfu - initial_count_log_cfu

        if delta_log <= 0:
            warnings.append(f"Initial count ({initial_count_log_cfu}) already exceeds critical limit ({critical_count_log_cfu}).")
            t_microbial: Optional[float] = 0.0
        elif mu == 0.0:
            t_microbial = None
            assumptions.append("Growth rate is zero (e.g. T <= Tmin); microbial proliferation is completely arrested and does not constrain shelf life.")
        else:
            # µmax is in base e (1/day), so rate in log10 per day is µmax / ln(10)
            log10_rate = mu / math.log(10)
            t_microbial = lag + (delta_log / log10_rate)

        trace = make_traceability(
            model_name=self.MODEL_NAME,
            equation_form="t_microbial = λ + [log10(Ncrit) - log10(N0)] / (µmax / ln(10))",
            equation_reference="Baranyi & Roberts (1994) Int. J. Food Microbiol. 23:277-294",
            scientific_sources=["McMeekin et al. (1993) Predictive Microbiology"],
            inputs_used={
                "target_microorganism": target_microorganism,
                "initial_count_log_cfu": initial_count_log_cfu,
                "critical_count_log_cfu": critical_count_log_cfu,
                "temperature_c": temperature_c,
            },
            parameters_used={"µmax_per_day": round(mu, 4), "lag_days": lag, "co2_inhibition": co2_inhibition_factor},
            parameter_sources=param_sources,
            units_used={"µmax": "1/day", "lag": "days", "shelf_life": "days"},
            assumptions=assumptions + [f"Target organism = {target_microorganism}."],
            warnings=warnings,
        )

        mu_result = ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=round(mu, 4),
            unit="1/day",
            traceability=trace,
        )
        lag_result = ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=round(lag, 2),
            unit="days",
            traceability=trace,
        )
        shelf_life_result = ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=round(t_microbial, 1) if t_microbial is not None else None,
            unit="days" if t_microbial is not None else None,
            traceability=trace,
        )

        return MicrobialRequirement(
            status=CalculationStatus.CALCULATED,
            target_microorganism=target_microorganism,
            initial_count_log_cfu=initial_count_log_cfu,
            critical_count_log_cfu=critical_count_log_cfu,
            growth_rate_per_day=mu_result,
            lag_time_days=lag_result,
            microbial_shelf_life_days=shelf_life_result,
            atmosphere_inhibition_factor=co2_inhibition_factor,
            traceability=trace,
            warnings=warnings,
        )
