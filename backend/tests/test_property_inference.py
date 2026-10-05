import pytest
from app.schemas.food_evidence import FoodEvidenceDataset, FoodEvidenceRecord
from app.schemas.inference import (
    InferenceResolutionLevel,
    PropertyInferenceProfile,
)
from app.schemas.packaging_request import PackagingRequest
from app.schemas.property_status import PropertyStatusEnum
from scientific_engine.inference.engine import (
    PropertyInferenceEngine,
    infer_commodity_properties,
)


# ---------------------------------------------------------------------------
# Test 1: User-supplied property values have absolute precedence
# ---------------------------------------------------------------------------

def test_user_supplied_property_precedence() -> None:
    req = PackagingRequest(
        commodity="apple",
        product_form="whole",
        ripeness_stage="ripe",
        target_shelf_life_days=14,
        storage_type="chilled",
        moisture_percent=78.5,  # Explicitly supplied by user
    )
    profile = infer_commodity_properties(req)

    moisture = profile.properties["moisture_percent"]
    assert moisture.value == 78.5
    assert moisture.status == PropertyStatusEnum.measured
    assert moisture.resolution_level == InferenceResolutionLevel.USER_SUPPLIED
    assert moisture.confidence == 1.0
    assert moisture.uncertainty_range == (78.5, 78.5)
    assert len(moisture.warnings) == 0


# ---------------------------------------------------------------------------
# Test 2: Exact context match from reference literature
# ---------------------------------------------------------------------------

def test_exact_context_match_retrieval() -> None:
    req = PackagingRequest(
        commodity="apple",
        variety="Gala",
        product_form="whole",
        ripeness_stage="ripe",
        target_shelf_life_days=14,
        storage_type="ambient",
        storage_temperature_c=20.0,
    )
    profile = infer_commodity_properties(req)

    # 1. Moisture from USDA Gala entry
    moisture = profile.properties["moisture_percent"]
    assert moisture.value == 84.65
    assert moisture.status == PropertyStatusEnum.literature
    assert moisture.uncertainty_range == (83.89, 85.63)
    assert any("USDA FoodData Central" in cit for cit in moisture.citations)

    # 2. Respiration rate at 20°C from Kader (2002) (Reclassified in DV2 to generic apple, causing Gala request to fall back to generic commodity evidence)
    resp = profile.properties["respiration_rate"]
    assert resp.value == 35.0
    assert resp.uncertainty_range == (25.0, 50.0)
    assert resp.status == PropertyStatusEnum.inferred
    assert resp.resolution_level == InferenceResolutionLevel.VARIETY_FALLBACK


# ---------------------------------------------------------------------------
# Test 3: Cultivar/Variety fallback hierarchy
# ---------------------------------------------------------------------------

def test_variety_fallback_resolution() -> None:
    req = PackagingRequest(
        commodity="apple",
        variety="Honeycrisp",  # Variety not in reference database
        product_form="whole",
        ripeness_stage="ripe",
        target_shelf_life_days=14,
        storage_type="chilled",
    )
    profile = infer_commodity_properties(req)

    moisture = profile.properties["moisture_percent"]
    # Falls back to species-level apple data
    assert moisture.value is not None
    assert moisture.resolution_level == InferenceResolutionLevel.VARIETY_FALLBACK
    assert moisture.status == PropertyStatusEnum.inferred
    assert any(w.code == "VARIETY_FALLBACK" for w in moisture.warnings)
    # Confidence is discounted due to fallback
    assert moisture.confidence is not None
    assert moisture.confidence < 0.95


# ---------------------------------------------------------------------------
# Test 4: Product form fallback hierarchy
# ---------------------------------------------------------------------------

def test_product_form_fallback_resolution() -> None:
    req = PackagingRequest(
        commodity="salmon",
        product_form="ground",  # Only 'fillet' is in reference data
        ripeness_stage="fresh",
        target_shelf_life_days=5,
        storage_type="chilled",
    )
    profile = infer_commodity_properties(req)

    fat = profile.properties["fat_percent"]
    assert fat.value == 12.35
    assert fat.resolution_level == InferenceResolutionLevel.FORM_FALLBACK
    assert any(w.code == "FORM_FALLBACK" for w in fat.warnings)


# ---------------------------------------------------------------------------
# Test 5: Temperature-conditioned matching and nearest bound
# ---------------------------------------------------------------------------

def test_temperature_matching_and_nearest_bound() -> None:
    # 5a. Near 0°C -> matches cold storage respiration (ASHRAE 0°C: 3-6 mg/kg/hr)
    req_cold = PackagingRequest(
        commodity="apple",
        variety="Gala",
        product_form="whole",
        ripeness_stage="mature_green",
        target_shelf_life_days=30,
        storage_type="chilled",
        storage_temperature_c=0.0,
    )
    profile_cold = infer_commodity_properties(req_cold)
    resp_cold = profile_cold.properties["respiration_rate"]
    assert resp_cold.value == 4.5
    assert resp_cold.uncertainty_range == (3.0, 6.0)

    # 5b. Intermediate temperature (10°C) with no exact literature entry
    # Finds closest temperature bound without fabricating an unverified formula
    req_mid = PackagingRequest(
        commodity="apple",
        variety="Gala",
        product_form="whole",
        ripeness_stage="ripe",
        target_shelf_life_days=14,
        storage_type="ambient",
        storage_temperature_c=10.0,
    )
    profile_mid = infer_commodity_properties(req_mid)
    resp_mid = profile_mid.properties["respiration_rate"]
    assert resp_mid.value is not None
    assert resp_mid.resolution_level == InferenceResolutionLevel.CLOSEST_TEMPERATURE_BOUND
    assert any(w.code == "TEMP_BOUND_DIFFERENCE" for w in resp_mid.warnings)


# ---------------------------------------------------------------------------
# Test 6: Conflicting scientific evidence uncertainty spanning
# ---------------------------------------------------------------------------

def test_conflicting_evidence_uncertainty_spanning() -> None:
    custom_records = [
        FoodEvidenceRecord(
            commodity="blueberry",
            property="moisture_content",
            value=83.0,
            minimum_value=81.0,
            maximum_value=85.0,
            unit="%",
            source_title="Study 1 (2015)",
        ),
        FoodEvidenceRecord(
            commodity="blueberry",
            property="moisture_content",
            value=87.0,
            minimum_value=86.0,
            maximum_value=89.0,
            unit="%",
            source_title="Study 2 (2020)",
        ),
    ]
    dataset = FoodEvidenceDataset(records=custom_records)
    engine = PropertyInferenceEngine(dataset=dataset)

    req = PackagingRequest(
        commodity="blueberry",
        product_form="whole",
        ripeness_stage="ripe",
        target_shelf_life_days=10,
        storage_type="chilled",
    )
    profile = engine.infer_profile(req)
    moisture = profile.properties["moisture_percent"]

    # Minimum should be 81.0, maximum should be 89.0
    assert moisture.minimum_value == 81.0
    assert moisture.maximum_value == 89.0
    assert moisture.uncertainty_range == (81.0, 89.0)
    # Point estimate is average of point values (83.0 + 87.0) / 2 = 85.0
    assert moisture.value == 85.0
    assert len(moisture.citations) == 2


# ---------------------------------------------------------------------------
# Test 7: Strict unknown handling for unrecorded commodities / properties
# ---------------------------------------------------------------------------

def test_strict_unknown_handling() -> None:
    req = PackagingRequest(
        commodity="dragonfruit",  # Absent from reference data
        product_form="whole",
        ripeness_stage="ripe",
        target_shelf_life_days=10,
        storage_type="ambient",
    )
    profile = infer_commodity_properties(req)

    for prop_name in ["moisture_percent", "fat_percent", "ph", "respiration_rate"]:
        p = profile.properties[prop_name]
        assert p.value is None
        assert p.status == PropertyStatusEnum.unknown
        assert p.resolution_level == InferenceResolutionLevel.UNKNOWN
        assert p.confidence is None
        assert p.uncertainty_range is None
        assert any(w.code == "NO_EVIDENCE" for w in p.warnings)

    assert profile.overall_confidence is None


# ---------------------------------------------------------------------------
# Test 8: Durian test case (incomplete real-world user input)
# ---------------------------------------------------------------------------

def test_durian_incomplete_input_inference() -> None:
    """
    Validates incomplete real-world input:
    - Known logistics are preserved.
    - Respiration rate at 20°C is inferred from verified literature (Voon/Ketsa 1995).
    - Unrecorded properties (fat_percent, ph) remain strictly UNKNOWN with value=None.
    """
    req = PackagingRequest(
        commodity="durian",
        product_form="whole",
        ripeness_stage="ripe",
        target_shelf_life_days=10,
        storage_type="chilled",
        storage_temperature_c=20.0,
    )
    profile = infer_commodity_properties(req)

    # 1. Respiration rate is resolved from literature
    resp = profile.properties["respiration_rate"]
    assert resp.value == 375.0
    assert resp.uncertainty_range == (300.0, 450.0)
    assert resp.status == PropertyStatusEnum.literature
    assert any("Physiological changes during ripening of durian" in cit for cit in resp.citations)

    # 2. Fat percent and pH have no literature entry in dataset -> MUST remain UNKNOWN
    fat = profile.properties["fat_percent"]
    assert fat.value is None
    assert fat.status == PropertyStatusEnum.unknown

    ph = profile.properties["ph"]
    assert ph.value is None
    assert ph.status == PropertyStatusEnum.unknown
