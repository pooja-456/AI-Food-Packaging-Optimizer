import pytest
from pydantic import ValidationError

from app.schemas.packaging_request import PackagingRequest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MINIMUM_VALID = {
    "commodity": "apple",
    "product_form": "whole",
    "ripeness_stage": "mature",
    "target_shelf_life_days": 14,
    "storage_type": "chilled",
}


def make_request(**overrides) -> dict:
    data = {**MINIMUM_VALID, **overrides}
    return data


# ---------------------------------------------------------------------------
# Valid request
# ---------------------------------------------------------------------------

def test_valid_minimum_request() -> None:
    req = PackagingRequest(**MINIMUM_VALID)
    assert req.commodity == "apple"
    assert req.target_shelf_life_days == 14
    # All optional scientific fields default to None
    assert req.moisture_percent is None
    assert req.fat_percent is None
    assert req.ph is None
    assert req.respiration_rate is None
    assert req.storage_temperature_c is None
    assert req.relative_humidity_percent is None


def test_valid_full_request() -> None:
    req = PackagingRequest(**make_request(
        variety="Granny Smith",
        transportation_type="refrigerated_truck",
        transportation_duration_days=2.0,
        storage_temperature_c=4.0,
        relative_humidity_percent=90.0,
        moisture_percent=85.0,
        fat_percent=0.2,
        ph=3.5,
        respiration_rate=12.5,
    ))
    assert req.variety == "Granny Smith"
    assert req.storage_temperature_c == 4.0


# ---------------------------------------------------------------------------
# Missing optional scientific properties (Durian test case)
# ---------------------------------------------------------------------------

def test_durian_incomplete_request() -> None:
    """
    A real-world user who knows very little about packaging science.
    Scientific properties must remain unknown (None) — never fabricated.
    """
    req = PackagingRequest(
        commodity="durian",
        product_form="cut",
        ripeness_stage="ripe",
        target_shelf_life_days=10,
        storage_type="chilled",
    )
    assert req.commodity == "durian"
    assert req.product_form == "cut"
    assert req.ripeness_stage == "ripe"
    assert req.target_shelf_life_days == 10
    assert req.storage_type == "chilled"

    # All scientific properties must remain unknown
    assert req.moisture_percent is None
    assert req.fat_percent is None
    assert req.ph is None
    assert req.respiration_rate is None
    assert req.storage_temperature_c is None
    assert req.relative_humidity_percent is None


# ---------------------------------------------------------------------------
# Invalid shelf life
# ---------------------------------------------------------------------------

def test_invalid_shelf_life_zero() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PackagingRequest(**make_request(target_shelf_life_days=0))
    assert "target_shelf_life_days" in str(exc_info.value)


def test_invalid_shelf_life_negative() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PackagingRequest(**make_request(target_shelf_life_days=-5))
    assert "target_shelf_life_days" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Invalid relative humidity
# ---------------------------------------------------------------------------

def test_invalid_humidity_above_100() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PackagingRequest(**make_request(relative_humidity_percent=101.0))
    assert "relative_humidity_percent" in str(exc_info.value)


def test_invalid_humidity_below_0() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PackagingRequest(**make_request(relative_humidity_percent=-1.0))
    assert "relative_humidity_percent" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Invalid moisture percentage
# ---------------------------------------------------------------------------

def test_invalid_moisture_above_100() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PackagingRequest(**make_request(moisture_percent=105.0))
    assert "moisture_percent" in str(exc_info.value)


def test_invalid_moisture_below_0() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PackagingRequest(**make_request(moisture_percent=-10.0))
    assert "moisture_percent" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Invalid fat percentage
# ---------------------------------------------------------------------------

def test_invalid_fat_above_100() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PackagingRequest(**make_request(fat_percent=200.0))
    assert "fat_percent" in str(exc_info.value)


def test_invalid_fat_below_0() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PackagingRequest(**make_request(fat_percent=-5.0))
    assert "fat_percent" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Invalid pH
# ---------------------------------------------------------------------------

def test_invalid_ph_above_14() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PackagingRequest(**make_request(ph=15.0))
    assert "ph" in str(exc_info.value)


def test_invalid_ph_below_0() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PackagingRequest(**make_request(ph=-1.0))
    assert "ph" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Invalid transportation duration
# ---------------------------------------------------------------------------

def test_invalid_transportation_duration_negative() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PackagingRequest(**make_request(transportation_duration_days=-1.0))
    assert "transportation_duration_days" in str(exc_info.value)


def test_valid_transportation_duration_zero() -> None:
    req = PackagingRequest(**make_request(transportation_duration_days=0.0))
    assert req.transportation_duration_days == 0.0


# ---------------------------------------------------------------------------
# Invalid respiration rate
# ---------------------------------------------------------------------------

def test_invalid_respiration_rate_negative() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PackagingRequest(**make_request(respiration_rate=-0.1))
    assert "respiration_rate" in str(exc_info.value)


def test_valid_respiration_rate_zero() -> None:
    req = PackagingRequest(**make_request(respiration_rate=0.0))
    assert req.respiration_rate == 0.0


# ---------------------------------------------------------------------------
# storage_temperature_c — numeric only, no range restriction in Phase 1
# ---------------------------------------------------------------------------

def test_storage_temperature_accepts_any_numeric() -> None:
    req = PackagingRequest(**make_request(storage_temperature_c=-40.0))
    assert req.storage_temperature_c == -40.0

    req2 = PackagingRequest(**make_request(storage_temperature_c=100.0))
    assert req2.storage_temperature_c == 100.0
