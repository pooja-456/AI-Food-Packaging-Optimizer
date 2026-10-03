import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from app.schemas.food_evidence import FoodEvidenceRecord, FoodEvidenceDataset
from app.schemas.property_status import PropertyStatusEnum
from app.schemas.vocabularies import (
    FoodProperty,
    CommodityCategory,
    ProcessingState,
    ProductForm,
    MaturityStage,
)


# ---------------------------------------------------------------------------
# Test 1: Multiple commodities can be represented
# ---------------------------------------------------------------------------

def test_multiple_commodities_representation() -> None:
    commodities = ["apple", "strawberry", "salmon", "durian", "mango", "lettuce", "cheese"]
    records = [
        FoodEvidenceRecord(
            commodity=comm,
            property="respiration_rate" if comm in ["apple", "strawberry", "durian", "mango", "lettuce"] else "moisture_content",
            value=10.0,
            unit="mg CO2/kg/hr" if comm in ["apple", "strawberry", "durian", "mango", "lettuce"] else "%",
        )
        for comm in commodities
    ]
    dataset = FoodEvidenceDataset(records=records)
    unique_commodities = dataset.get_commodities()

    for comm in commodities:
        assert comm in unique_commodities


# ---------------------------------------------------------------------------
# Test 2: Multiple varieties/cultivars can be represented
# ---------------------------------------------------------------------------

def test_multiple_varieties_representation() -> None:
    rec_gala = FoodEvidenceRecord(
        commodity="apple",
        variety="Gala",
        property="ph",
        value=3.9,
        unit="pH",
        status=PropertyStatusEnum.literature,
    )
    rec_granny = FoodEvidenceRecord(
        commodity="apple",
        variety="Granny Smith",
        property="ph",
        value=3.3,
        unit="pH",
        status=PropertyStatusEnum.literature,
    )
    dataset = FoodEvidenceDataset(records=[rec_gala, rec_granny])

    gala_results = dataset.query(commodity="apple", variety="Gala")
    granny_results = dataset.query(commodity="apple", variety="Granny Smith")

    assert len(gala_results) == 1
    assert gala_results[0].value == 3.9
    assert len(granny_results) == 1
    assert granny_results[0].value == 3.3


# ---------------------------------------------------------------------------
# Test 3: Multiple product forms can be represented
# ---------------------------------------------------------------------------

def test_multiple_product_forms_representation() -> None:
    rec_whole = FoodEvidenceRecord(
        commodity="apple",
        product_form=ProductForm.WHOLE.value,
        processing_state=ProcessingState.RAW.value,
        property="respiration_rate",
        value=4.5,
        unit="mg CO2/kg/hr",
        temperature=0.0,
    )
    rec_sliced = FoodEvidenceRecord(
        commodity="apple",
        product_form=ProductForm.SLICED.value,
        processing_state=ProcessingState.FRESH_CUT.value,
        property="respiration_rate",
        value=15.0,
        unit="mg CO2/kg/hr",
        temperature=5.0,
    )
    rec_puree = FoodEvidenceRecord(
        commodity="apple",
        product_form=ProductForm.PUREE.value,
        processing_state=ProcessingState.PASTEURIZED.value,
        property="moisture_content",
        value=88.2,
        unit="%",
    )

    dataset = FoodEvidenceDataset(records=[rec_whole, rec_sliced, rec_puree])

    whole_query = dataset.query(commodity="apple", product_form="whole")
    sliced_query = dataset.query(commodity="apple", product_form="sliced")

    assert len(whole_query) == 1
    assert whole_query[0].value == 4.5
    assert len(sliced_query) == 1
    assert sliced_query[0].value == 15.0


# ---------------------------------------------------------------------------
# Test 4: Different experimental contexts can coexist
# ---------------------------------------------------------------------------

def test_different_experimental_contexts_coexistence() -> None:
    # Same commodity and variety measured at different temperatures and maturities
    rec_low_temp = FoodEvidenceRecord(
        commodity="strawberry",
        variety="Camarosa",
        maturity_stage=MaturityStage.RIPE.value,
        property="respiration_rate",
        value=15.0,
        unit="mg CO2/kg/hr",
        temperature=0.0,
        relative_humidity=95.0,
        source_title="Postharvest Handbook 2002",
    )
    rec_high_temp = FoodEvidenceRecord(
        commodity="strawberry",
        variety="Camarosa",
        maturity_stage=MaturityStage.RIPE.value,
        property="respiration_rate",
        value=150.0,
        unit="mg CO2/kg/hr",
        temperature=20.0,
        relative_humidity=70.0,
        source_title="Postharvest Handbook 2002",
    )

    dataset = FoodEvidenceDataset(records=[rec_low_temp, rec_high_temp])
    assert len(dataset.records) == 2

    # Querying temperature sub-range preserves context
    cold_results = dataset.query(commodity="strawberry", temperature_max=5.0)
    assert len(cold_results) == 1
    assert cold_results[0].temperature == 0.0
    assert cold_results[0].value == 15.0

    warm_results = dataset.query(commodity="strawberry", temperature_min=15.0)
    assert len(warm_results) == 1
    assert warm_results[0].temperature == 20.0
    assert warm_results[0].value == 150.0


# ---------------------------------------------------------------------------
# Test 5: Conflicting scientific observations are preserved independently
# ---------------------------------------------------------------------------

def test_conflicting_observations_preserved_without_averaging() -> None:
    # Study A reports moisture 84.5%
    rec_study_a = FoodEvidenceRecord(
        commodity="apple",
        variety="Fuji",
        property="moisture_content",
        value=84.5,
        unit="%",
        source_title="Journal of Food Science 2015",
        publication_year=2015,
        DOI="10.1111/1750-3841.12345",
    )
    # Study B reports moisture 87.2% for the same variety under different harvest year
    rec_study_b = FoodEvidenceRecord(
        commodity="apple",
        variety="Fuji",
        property="moisture_content",
        value=87.2,
        unit="%",
        source_title="Postharvest Biology and Technology 2018",
        publication_year=2018,
        DOI="10.1016/j.postharvbio.2018.54321",
    )

    dataset = FoodEvidenceDataset()
    dataset.add_record(rec_study_a)
    dataset.add_record(rec_study_b)

    results = dataset.query(commodity="apple", property_name="moisture_content")
    assert len(results) == 2

    # Verify both values exist intact and are NOT averaged to 85.85%
    values = [r.value for r in results]
    assert 84.5 in values
    assert 87.2 in values
    assert 85.85 not in values


# ---------------------------------------------------------------------------
# Test 6: Missing values remain NULL/None
# ---------------------------------------------------------------------------

def test_missing_values_remain_null() -> None:
    # Minimal record with only mandatory commodity and property
    rec = FoodEvidenceRecord(
        commodity="papaya",
        property="ethylene_production",
    )
    assert rec.value is None
    assert rec.unit is None
    assert rec.minimum_value is None
    assert rec.maximum_value is None
    assert rec.temperature is None
    assert rec.relative_humidity is None
    assert rec.storage_duration is None
    assert rec.measurement_method is None
    assert rec.source_title is None
    assert rec.publication_year is None
    assert rec.DOI is None
    assert rec.URL is None
    assert rec.source_type is None
    assert rec.evidence_strength is None
    assert rec.notes is None
    assert rec.confidence is None
    assert rec.uncertainty_range is None


# ---------------------------------------------------------------------------
# Test 7: Epistemic status values are distinct and supported
# ---------------------------------------------------------------------------

def test_epistemic_status_distinguishable() -> None:
    rec_measured = FoodEvidenceRecord(
        commodity="mango",
        property="ph",
        value=4.6,
        status=PropertyStatusEnum.measured,
        measurement_method="Direct glass electrode",
    )
    rec_literature = FoodEvidenceRecord(
        commodity="mango",
        property="ph",
        value=4.7,
        status=PropertyStatusEnum.literature,
        source_title="Handbook of Tropical Fruits",
    )
    rec_inferred = FoodEvidenceRecord(
        commodity="mango",
        property="ph",
        value=4.65,
        status=PropertyStatusEnum.inferred,
        notes="Inferred from titratable acidity curve",
    )
    rec_unknown = FoodEvidenceRecord(
        commodity="mango",
        property="aroma_volatility",
        status=PropertyStatusEnum.unknown,
    )

    assert rec_measured.status == PropertyStatusEnum.measured
    assert rec_literature.status == PropertyStatusEnum.literature
    assert rec_inferred.status == PropertyStatusEnum.inferred
    assert rec_unknown.status == PropertyStatusEnum.unknown


# ---------------------------------------------------------------------------
# Test 8: Schema contains NO commodity-specific hardcoding
# ---------------------------------------------------------------------------

def test_schema_is_commodity_agnostic() -> None:
    # Schema must accept arbitrary valid food commodities, categories, and properties
    rec = FoodEvidenceRecord(
        commodity="quinoa",
        commodity_category=CommodityCategory.BAKERY_CEREAL.value,
        variety="Real Bolivian",
        product_form=ProductForm.POWDER.value,
        processing_state=ProcessingState.DRIED.value,
        property=FoodProperty.WATER_ACTIVITY.value,
        value=0.45,
        unit="aw",
        status=PropertyStatusEnum.literature,
    )
    assert rec.commodity == "quinoa"
    assert rec.property == "water_activity"
    assert rec.value == 0.45


# ---------------------------------------------------------------------------
# Test 9: Reference dataset JSON parses and validates correctly
# ---------------------------------------------------------------------------

def test_reference_food_evidence_json_validity() -> None:
    ref_path = Path(__file__).resolve().parent.parent.parent / "data" / "reference" / "food_evidence.json"
    assert ref_path.exists(), f"Reference file not found at {ref_path}"

    with open(ref_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) > 0

    records = [FoodEvidenceRecord(**item) for item in data]
    dataset = FoodEvidenceDataset(records=records)

    # Verify multiple commodities are present in reference dataset
    commodities = dataset.get_commodities()
    assert "apple" in commodities
    assert "strawberry" in commodities
    assert "durian" in commodities
    assert "salmon" in commodities


# ---------------------------------------------------------------------------
# Test 10: DV4 - FOOD-7 and FOOD-8 volumetric respiration rate unit correction
# ---------------------------------------------------------------------------

def test_dv4_food_7_and_food_8_volumetric_unit_correction() -> None:
    ref_path = Path(__file__).resolve().parent.parent.parent / "data" / "reference" / "food_evidence.json"
    with open(ref_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Index 6 is FOOD-7 (Strawberry respiration rate at 0°C)
    food_7 = data[6]
    assert food_7["commodity"] == "strawberry"
    assert food_7["temperature"] == 0.0
    assert food_7["property"] == "respiration_rate"
    assert food_7["unit"] == "mL CO2/kg/hr"
    assert food_7["minimum_value"] == 6.0
    assert food_7["maximum_value"] == 9.0
    assert food_7["value"] == 7.5
    assert food_7["uncertainty_range"] == [6.0, 9.0]
    assert "DV4 CONTROLLED CORRECTION" in food_7["notes"]

    # Index 7 is FOOD-8 (Strawberry respiration rate at 20°C)
    food_8 = data[7]
    assert food_8["commodity"] == "strawberry"
    assert food_8["temperature"] == 20.0
    assert food_8["property"] == "respiration_rate"
    assert food_8["unit"] == "mL CO2/kg/hr"
    assert food_8["minimum_value"] == 50.0
    assert food_8["maximum_value"] == 100.0
    assert food_8["value"] == 75.0
    assert food_8["uncertainty_range"] == [50.0, 100.0]
    assert "DV4 CONTROLLED CORRECTION" in food_8["notes"]


# ---------------------------------------------------------------------------
# Test 11: DV5-C - FOOD-7 volumetric respiration safety guard regression
# ---------------------------------------------------------------------------

def test_dv5c_food_7_safety_guard_regression() -> None:
    from app.schemas.packaging_request import PackagingRequest
    from app.schemas.physics import CalculationStatus
    from scientific_engine.inference.engine import infer_commodity_properties
    from scientific_engine.physics.respiration import RespirationKineticsModel

    req = PackagingRequest(
        commodity="strawberry",
        product_form="whole",
        ripeness_stage="ripe",
        target_shelf_life_days=7,
        storage_type="chilled",
        storage_temperature_c=0.0,
    )
    profile = infer_commodity_properties(req)

    # 1. Evidence retrieved
    resp_prop = profile.properties["respiration_rate"]
    assert resp_prop.value == 7.5

    # 2. CO2 unit unchanged
    assert resp_prop.unit == "mL CO2/kg/hr"

    # 3. Range unchanged
    assert resp_prop.uncertainty_range == (6.0, 9.0)

    # 4. Source attached
    assert any("Kader" in cit for cit in resp_prop.citations)

    # 5. Physics model calculation
    model = RespirationKineticsModel()
    res = model.calculate_respiration(inferred_respiration=resp_prop, temperature_c=0.0)

    # 6. Result is UNKNOWN where O2 consumption rate is required without authorized RQ
    assert res.status == CalculationStatus.UNKNOWN

    # 7. No numeric O2 value is fabricated
    assert res.value is None
    assert res.uncertainty_range == (6.0, 9.0)


# ---------------------------------------------------------------------------
# Test 12: DV5-C - FOOD-8 volumetric respiration safety guard regression
# ---------------------------------------------------------------------------

def test_dv5c_food_8_safety_guard_regression() -> None:
    from app.schemas.packaging_request import PackagingRequest
    from app.schemas.physics import CalculationStatus
    from scientific_engine.inference.engine import infer_commodity_properties
    from scientific_engine.physics.respiration import RespirationKineticsModel

    req = PackagingRequest(
        commodity="strawberry",
        product_form="whole",
        ripeness_stage="ripe",
        target_shelf_life_days=2,
        storage_type="ambient",
        storage_temperature_c=20.0,
    )
    profile = infer_commodity_properties(req)

    # 1. Evidence retrieved
    resp_prop = profile.properties["respiration_rate"]
    assert resp_prop.value == 75.0

    # 2. CO2 unit unchanged
    assert resp_prop.unit == "mL CO2/kg/hr"

    # 3. Range unchanged
    assert resp_prop.uncertainty_range == (50.0, 100.0)

    # 4. Source attached
    assert any("Kader" in cit for cit in resp_prop.citations)

    # 5. Physics model calculation
    model = RespirationKineticsModel()
    res = model.calculate_respiration(inferred_respiration=resp_prop, temperature_c=20.0)

    # 6. Result is UNKNOWN where O2 consumption rate is required without authorized RQ
    assert res.status == CalculationStatus.UNKNOWN

    # 7. No numeric O2 value is fabricated
    assert res.value is None
    assert res.uncertainty_range == (50.0, 100.0)


