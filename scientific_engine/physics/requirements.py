"""
Packaging Requirement Engine (Phase 4 Orchestrator).

Synthesizes:
    PackagingRequest (User input)
        ↓
    PropertyInferenceProfile (Phase 3 scientific inference)
        ↓
    Deterioration-Mode Assessment (Mechanism eligibility & computability)
        ↓
    Scientific Models Execution (Respiration, Gas Exchange, Moisture Transfer, Microbial Hurdles)
        ↓
    PackagingRequirementEnvelope (Comprehensive required barrier profile)

Strictly outputs performance requirements (OTR, CO2TR, WVTR, aw, atmospheres).
Contains absolutely NO material selection, material ranking, or optimization logic.
"""

from typing import Any, Dict, List, Optional, Tuple

from app.schemas.inference import PropertyInferenceProfile
from app.schemas.packaging_request import PackagingRequest
from app.schemas.packaging_requirements import (
    DeteriorationMechanismStatus,
    DeteriorationProfile,
    GasExchangeRequirement,
    MicrobialRequirement,
    MoistureRequirement,
    PackagingRequirementEnvelope,
    ShelfLifeRequirement,
)
from app.schemas.physics import CalculationStatus, ScientificResult, ScientificTraceability
from scientific_engine.physics.gas_exchange import GasExchangeModel
from scientific_engine.physics.microbial import MicrobialGrowthModel
from scientific_engine.physics.moisture import MoistureTransferModel
from scientific_engine.physics.respiration import RespirationKineticsModel
from scientific_engine.physics.sorption import MoistureSorptionModel
from scientific_engine.physics.traceability import make_traceability


class PackagingRequirementEngine:
    """
    Mechanism-aware physics and packaging requirement engine.
    """

    def __init__(self) -> None:
        self.respiration_model = RespirationKineticsModel()
        self.gas_exchange_model = GasExchangeModel()
        self.moisture_model = MoistureTransferModel()
        self.microbial_model = MicrobialGrowthModel()

    def evaluate_requirements(
        self,
        request: PackagingRequest,
        inference_profile: PropertyInferenceProfile,
        product_mass_kg: Optional[float] = None,
        package_area_m2: Optional[float] = None,
        dry_mass_g: Optional[float] = None,
        critical_water_activity: Optional[float] = None,
        critical_moisture_percent: Optional[float] = None,
        package_wvtr_g_pkg_day: Optional[float] = None,
        sorption_model: Optional[MoistureSorptionModel] = None,
        target_microorganism: Optional[str] = None,
        initial_microbial_count_log: Optional[float] = None,
        critical_microbial_count_log: Optional[float] = None,
        microbial_growth_rate: Optional[float] = None,
        microbial_lag_days: Optional[float] = None,
    ) -> PackagingRequirementEnvelope:
        """
        Evaluate and construct the complete scientific packaging requirement envelope.
        """
        all_warnings: List[str] = []
        all_assumptions: List[str] = []
        traceability_log: List[ScientificTraceability] = []

        # -------------------------------------------------------------
        # Step 1: Deterioration Mode Identification
        # -------------------------------------------------------------
        det_profile = self._assess_deterioration_modes(
            request=request,
            profile=inference_profile,
        )

        # -------------------------------------------------------------
        # Step 2: Respiration & Gas Exchange Evaluation
        # -------------------------------------------------------------
        resp_prop = inference_profile.properties.get("respiration_rate")
        temp_c = request.storage_temperature_c

        respiration_result = self.respiration_model.calculate_respiration(
            inferred_respiration=resp_prop,
            temperature_c=temp_c,
        )
        traceability_log.append(respiration_result.traceability)
        all_assumptions.extend(respiration_result.traceability.assumptions)
        all_warnings.extend(respiration_result.traceability.warnings)

        gas_req = self.gas_exchange_model.calculate_gas_requirements(
            respiration_result=respiration_result,
            product_mass_kg=product_mass_kg,
            package_area_m2=package_area_m2,
        )
        if gas_req.traceability:
            traceability_log.append(gas_req.traceability)
            all_assumptions.extend(gas_req.traceability.assumptions)
            all_warnings.extend(gas_req.warnings)

        # -------------------------------------------------------------
        # Step 3: Moisture Transfer Evaluation
        # -------------------------------------------------------------
        moisture_prop = inference_profile.properties.get("moisture_percent")
        aw_prop = inference_profile.properties.get("water_activity")

        init_moisture_val = moisture_prop.value if moisture_prop else None
        init_aw_val = aw_prop.value if aw_prop else None

        moisture_req = self.moisture_model.calculate_moisture_requirements(
            initial_water_activity=init_aw_val,
            critical_water_activity=critical_water_activity,
            initial_moisture_percent=init_moisture_val,
            critical_moisture_percent=critical_moisture_percent,
            storage_temperature_c=temp_c,
            relative_humidity_percent=request.relative_humidity_percent,
            target_shelf_life_days=request.target_shelf_life_days,
            dry_mass_g=dry_mass_g,
            package_area_m2=package_area_m2,
            package_wvtr_g_pkg_day=package_wvtr_g_pkg_day,
            sorption_model=sorption_model,
        )
        if moisture_req.traceability:
            traceability_log.append(moisture_req.traceability)
            all_assumptions.extend(moisture_req.traceability.assumptions)
            all_warnings.extend(moisture_req.warnings)

        # -------------------------------------------------------------
        # Step 4: Microbial Safety & Proliferation Evaluation
        # -------------------------------------------------------------
        ph_prop = inference_profile.properties.get("ph")
        ph_val = ph_prop.value if ph_prop else None

        microbial_req = self.microbial_model.calculate_microbial_limits(
            target_microorganism=target_microorganism,
            initial_count_log_cfu=initial_microbial_count_log,
            critical_count_log_cfu=critical_microbial_count_log,
            growth_rate_per_day=microbial_growth_rate,
            lag_time_days=microbial_lag_days,
            temperature_c=temp_c,
            ph=ph_val,
            water_activity=init_aw_val,
        )
        if microbial_req.traceability:
            traceability_log.append(microbial_req.traceability)
            all_assumptions.extend(microbial_req.traceability.assumptions)
            all_warnings.extend(microbial_req.warnings)

        # -------------------------------------------------------------
        # Step 5: Multi-Mechanism Shelf-Life Assessment
        # -------------------------------------------------------------
        shelf_life_req = self._assess_shelf_life_feasibility(
            target_days=request.target_shelf_life_days,
            gas_req=gas_req,
            moisture_req=moisture_req,
            microbial_req=microbial_req,
            det_profile=det_profile,
        )
        if shelf_life_req.traceability:
            traceability_log.append(shelf_life_req.traceability)

        # -------------------------------------------------------------
        # Step 6: Overall Envelope Status Synthesis
        # -------------------------------------------------------------
        statuses = [gas_req.status, moisture_req.status, microbial_req.status]
        if all(s == CalculationStatus.CALCULATED for s in statuses):
            overall_status = CalculationStatus.CALCULATED
        elif any(s in [CalculationStatus.CALCULATED, CalculationStatus.PARTIALLY_CALCULATED] for s in statuses):
            overall_status = CalculationStatus.PARTIALLY_CALCULATED
        else:
            overall_status = CalculationStatus.UNKNOWN

        # Deduplicate warnings and assumptions while preserving order
        clean_warnings = list(dict.fromkeys(all_warnings))
        clean_assumptions = list(dict.fromkeys(all_assumptions))

        return PackagingRequirementEnvelope(
            commodity=request.commodity,
            target_shelf_life_days=request.target_shelf_life_days,
            storage_temperature_c=request.storage_temperature_c,
            relative_humidity_percent=request.relative_humidity_percent,
            deterioration_profile=det_profile,
            gas_requirements=gas_req,
            moisture_requirements=moisture_req,
            microbial_requirements=microbial_req,
            shelf_life=shelf_life_req,
            overall_status=overall_status,
            temperature_effects={"storage_temperature_c": temp_c},
            all_assumptions=clean_assumptions,
            all_warnings=clean_warnings,
            traceability_log=traceability_log,
        )

    def _assess_deterioration_modes(
        self,
        request: PackagingRequest,
        profile: PropertyInferenceProfile,
    ) -> DeteriorationProfile:
        """
        Assess which deterioration pathways physically apply to this commodity
        and whether scientific evidence permits their computation.
        """
        mechanisms: Dict[str, DeteriorationMechanismStatus] = {}
        vulnerabilities: List[str] = []

        # 1. Respiration
        resp_prop = profile.properties.get("respiration_rate")
        has_resp_val = resp_prop is not None and resp_prop.value is not None and resp_prop.value > 0
        resp_status = resp_prop.status.value if resp_prop else "unknown"

        # Plant tissue or respiring produce
        resp_eligible = has_resp_val or request.storage_type in ["ambient", "chilled"]
        resp_computable = has_resp_val and resp_status in ["measured", "literature", "inferred"]
        mechanisms["respiration"] = DeteriorationMechanismStatus(
            mechanism="respiration",
            eligible=resp_eligible,
            computable=resp_computable,
            status=CalculationStatus.CALCULATED if resp_computable else CalculationStatus.UNKNOWN,
            reason=None if resp_computable else "Respiration rate not found in scientific evidence.",
            evidence_references=resp_prop.citations if resp_prop else [],
        )
        if resp_computable:
            vulnerabilities.append("aerobic_respiration_metabolism")

        # 2. Moisture Transfer
        moisture_prop = profile.properties.get("moisture_percent")
        aw_prop = profile.properties.get("water_activity")
        has_moisture = bool((moisture_prop and moisture_prop.value is not None) or (aw_prop and aw_prop.value is not None))
        moist_computable = bool(has_moisture and request.storage_temperature_c is not None)
        mechanisms["moisture_transfer"] = DeteriorationMechanismStatus(
            mechanism="moisture_transfer",
            eligible=True,
            computable=moist_computable,
            status=CalculationStatus.PARTIALLY_CALCULATED if moist_computable else CalculationStatus.UNKNOWN,
            reason=None if moist_computable else "Initial moisture/aw or temperature missing.",
            evidence_references=moisture_prop.citations if moisture_prop else [],
        )
        if has_moisture:
            vulnerabilities.append("moisture_transpiration_or_gain")

        # 3. Microbial Proliferation
        ph_prop = profile.properties.get("ph")
        has_ph = ph_prop and ph_prop.value is not None
        microbial_eligible = True
        # Computable only when organism-specific kinetics are supplied to engine
        mechanisms["microbial_growth"] = DeteriorationMechanismStatus(
            mechanism="microbial_growth",
            eligible=microbial_eligible,
            computable=False,
            status=CalculationStatus.UNKNOWN,
            reason="Organism-specific growth kinetics (N0, µmax, Ncrit) required for quantitative calculation.",
            evidence_references=ph_prop.citations if ph_prop else [],
        )

        # 4. Lipid Oxidation
        fat_prop = profile.properties.get("fat_percent")
        has_fat = fat_prop and fat_prop.value is not None and fat_prop.value >= 5.0
        mechanisms["lipid_oxidation"] = DeteriorationMechanismStatus(
            mechanism="lipid_oxidation",
            eligible=bool(has_fat),
            computable=False,
            status=CalculationStatus.UNKNOWN,
            reason="Lipid oxidation kinetics model belongs to future phases.",
            evidence_references=fat_prop.citations if fat_prop else [],
        )
        if has_fat:
            vulnerabilities.append("oxidative_rancidity_risk")

        return DeteriorationProfile(
            commodity=request.commodity,
            mechanisms=mechanisms,
            primary_vulnerabilities=vulnerabilities,
        )

    def _assess_shelf_life_feasibility(
        self,
        target_days: int,
        gas_req: GasExchangeRequirement,
        moisture_req: MoistureRequirement,
        microbial_req: MicrobialRequirement,
        det_profile: DeteriorationProfile,
    ) -> ShelfLifeRequirement:
        """
        Assess overall shelf-life feasibility from computed mechanisms without
        falsely claiming uncomputed mechanisms are satisfied.
        """
        computed_limits: List[Tuple[str, float]] = []

        if moisture_req.moisture_limited_shelf_life_days and moisture_req.moisture_limited_shelf_life_days.value:
            computed_limits.append(("moisture_transfer", moisture_req.moisture_limited_shelf_life_days.value))

        if microbial_req.microbial_shelf_life_days and microbial_req.microbial_shelf_life_days.value:
            computed_limits.append(("microbial_growth", microbial_req.microbial_shelf_life_days.value))

        if not computed_limits:
            return ShelfLifeRequirement(
                target_days=target_days,
                limiting_mechanism=None,
                supported_calculated_shelf_life_days=None,
                feasibility="uncertain",
                status=CalculationStatus.PARTIALLY_CALCULATED if gas_req.status != CalculationStatus.UNKNOWN else CalculationStatus.UNKNOWN,
                traceability=make_traceability(
                    model_name="MultiMechanismShelfLifeSynthesizer",
                    equation_form="t_shelf = min(t_moisture, t_microbial, t_respiration)",
                    failure_or_unknown_reason="No finite mechanism-specific shelf life limits were fully computed.",
                ),
            )

        earliest_mechanism, min_days = min(computed_limits, key=lambda x: x[1])
        feasibility = "achievable" if min_days >= target_days else "constrained"

        trace = make_traceability(
            model_name="MultiMechanismShelfLifeSynthesizer",
            equation_form="t_shelf = min(t_moisture, t_microbial)",
            inputs_used={"target_days": target_days, "computed_limits": dict(computed_limits)},
            units_used={"shelf_life": "days"},
            assumptions=["Limiting shelf life governed by earliest reaching threshold among computed degradation pathways."],
        )

        return ShelfLifeRequirement(
            target_days=target_days,
            limiting_mechanism=earliest_mechanism,
            supported_calculated_shelf_life_days=ScientificResult(
                status=CalculationStatus.CALCULATED,
                value=min_days,
                unit="days",
                traceability=trace,
            ),
            feasibility=feasibility,
            status=CalculationStatus.CALCULATED,
            traceability=trace,
        )
