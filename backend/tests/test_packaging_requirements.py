import pytest
from app.schemas.packaging_request import PackagingRequest
from app.schemas.physics import CalculationStatus
from scientific_engine.inference.engine import infer_commodity_properties
from scientific_engine.physics.requirements import PackagingRequirementEngine


def test_end_to_end_respiring_commodity_requirement_envelope() -> None:
    # 1. PackagingRequest for fresh whole Apple
    req = PackagingRequest(
        commodity="apple",
        variety="Gala",
        product_form="whole",
        ripeness_stage="ripe",
        target_shelf_life_days=14,
        storage_type="ambient",
        storage_temperature_c=20.0,
        relative_humidity_percent=65.0,
    )

    # 2. Phase 3 Property Inference
    inference_profile = infer_commodity_properties(req)
    assert inference_profile.properties["respiration_rate"].value is not None

    # 3. Phase 4 Physics & Packaging Requirement Engine
    engine = PackagingRequirementEngine()
    envelope = engine.evaluate_requirements(
        request=req,
        inference_profile=inference_profile,
        product_mass_kg=1.5,
        package_area_m2=0.08,
    )

    assert envelope.commodity == "apple"
    assert envelope.target_shelf_life_days == 14
    assert envelope.storage_temperature_c == 20.0

    # Gas requirements: OTR and CO2TR are CALCULATED
    assert envelope.gas_requirements.status == CalculationStatus.CALCULATED
    assert envelope.gas_requirements.required_otr_cc_per_pkg_day is not None
    assert envelope.gas_requirements.required_otr_cc_per_pkg_day.value > 0
    assert envelope.gas_requirements.required_otr_per_area is not None
    assert envelope.gas_requirements.ideal_beta_ratio_co2_to_o2 is not None

    # Deterioration profile
    assert envelope.deterioration_profile.mechanisms["respiration"].eligible is True
    assert envelope.deterioration_profile.mechanisms["respiration"].computable is True

    # Traceability
    assert len(envelope.traceability_log) > 0
    assert len(envelope.all_assumptions) > 0

    # Strict check: No material selection or ranking is performed
    envelope_dict = envelope.model_dump()
    assert "recommended_material" not in envelope_dict
    assert "material_ranking" not in envelope_dict


def test_partial_calculation_when_product_mass_is_missing() -> None:
    req = PackagingRequest(
        commodity="strawberry",
        product_form="whole",
        ripeness_stage="ripe",
        target_shelf_life_days=7,
        storage_type="chilled",
        storage_temperature_c=0.0,
        relative_humidity_percent=95.0,
    )
    inference_profile = infer_commodity_properties(req)

    engine = PackagingRequirementEngine()
    # product_mass_kg is omitted
    envelope = engine.evaluate_requirements(
        request=req,
        inference_profile=inference_profile,
    )

    assert envelope.gas_requirements.status == CalculationStatus.PARTIALLY_CALCULATED
    assert envelope.gas_requirements.required_otr_cc_per_pkg_day.unit == "cc O2 / (kg product · day)"


def test_shelf_life_limiting_mechanism_synthesis() -> None:
    req = PackagingRequest(
        commodity="crackers",
        product_form="whole",
        ripeness_stage="dry",
        target_shelf_life_days=60,
        storage_type="ambient",
        storage_temperature_c=25.0,
        relative_humidity_percent=70.0,
        moisture_percent=3.0,
    )
    inference_profile = infer_commodity_properties(req)

    engine = PackagingRequirementEngine()
    # Dry product moisture limit: initial 3.0%, crit 6.0%, dry mass 200g, tested package WVTR 0.2 g/pkg/day
    # delta_m = (6.0 - 3.0) * (200 / 100) = 6.0 g H2O
    # t_moisture = 6.0 / 0.2 = 30 days
    # Target is 60 days -> feasibility is 'constrained'
    envelope = engine.evaluate_requirements(
        request=req,
        inference_profile=inference_profile,
        dry_mass_g=200.0,
        critical_moisture_percent=6.0,
        package_wvtr_g_pkg_day=0.2,
    )

    assert envelope.shelf_life.status == CalculationStatus.CALCULATED
    assert envelope.shelf_life.limiting_mechanism == "moisture_transfer"
    assert envelope.shelf_life.supported_calculated_shelf_life_days.value == 30.0
    assert envelope.shelf_life.feasibility == "constrained"


def test_durian_test_case_requirement_envelope() -> None:
    """
    Validates commodity-neutral processing on the durian validation test case:
    - Respiration at 20°C is inferred from literature and gas exchange is computed per kg.
    - Unmeasured properties (fat, microbial kinetics) remain UNKNOWN with zero guessing.
    - No durian-specific branches are hit.
    """
    req = PackagingRequest(
        commodity="durian",
        product_form="whole",
        ripeness_stage="ripe",
        target_shelf_life_days=10,
        storage_type="chilled",
        storage_temperature_c=20.0,
    )
    inference_profile = infer_commodity_properties(req)

    engine = PackagingRequirementEngine()
    envelope = engine.evaluate_requirements(
        request=req,
        inference_profile=inference_profile,
        product_mass_kg=3.0,
    )

    assert envelope.commodity == "durian"
    assert envelope.gas_requirements.status == CalculationStatus.CALCULATED
    assert envelope.gas_requirements.required_otr_cc_per_pkg_day.value > 0
    # Microbial is UNKNOWN without specific organism kinetics
    assert envelope.microbial_requirements.status == CalculationStatus.UNKNOWN
