import pytest
from pydantic import ValidationError

from app.schemas.property_status import PropertyStatus, PropertyStatusEnum


# ---------------------------------------------------------------------------
# Default / unknown property
# ---------------------------------------------------------------------------

def test_unknown_property_defaults() -> None:
    prop = PropertyStatus(property="moisture_content", unit="%")
    assert prop.value is None
    assert prop.status == PropertyStatusEnum.unknown
    assert prop.source is None
    assert prop.confidence is None
    assert prop.uncertainty_range is None
    assert prop.acquisition_method is None


def test_unknown_property_matches_spec_example() -> None:
    """Matches the exact example given in the Phase 1 specification."""
    prop = PropertyStatus(property="moisture_content", unit="%")
    assert prop.property == "moisture_content"
    assert prop.value is None
    assert prop.unit == "%"
    assert prop.status == PropertyStatusEnum.unknown
    assert prop.source is None
    assert prop.confidence is None
    assert prop.uncertainty_range is None
    assert prop.acquisition_method is None


# ---------------------------------------------------------------------------
# All four status values are accepted
# ---------------------------------------------------------------------------

def test_status_measured() -> None:
    prop = PropertyStatus(
        property="ph",
        value=4.5,
        unit="pH",
        status=PropertyStatusEnum.measured,
        source="Lab measurement",
        confidence=0.98,
        uncertainty_range=(4.3, 4.7),
        acquisition_method="electrode pH meter",
    )
    assert prop.status == PropertyStatusEnum.measured
    assert prop.value == 4.5
    assert prop.confidence == 0.98
    assert prop.uncertainty_range == (4.3, 4.7)


def test_status_literature() -> None:
    prop = PropertyStatus(
        property="respiration_rate",
        value=25.0,
        unit="mL CO2/kg/hr",
        status=PropertyStatusEnum.literature,
        source="ASHRAE Handbook",
    )
    assert prop.status == PropertyStatusEnum.literature


def test_status_inferred() -> None:
    prop = PropertyStatus(
        property="fat_percent",
        value=0.3,
        unit="%",
        status=PropertyStatusEnum.inferred,
    )
    assert prop.status == PropertyStatusEnum.inferred


def test_status_unknown() -> None:
    prop = PropertyStatus(property="moisture_content")
    assert prop.status == PropertyStatusEnum.unknown


# ---------------------------------------------------------------------------
# Invalid status value is rejected
# ---------------------------------------------------------------------------

def test_invalid_status_rejected() -> None:
    with pytest.raises(ValidationError):
        PropertyStatus(property="moisture_content", status="fabricated")


# ---------------------------------------------------------------------------
# Property field is required
# ---------------------------------------------------------------------------

def test_property_name_is_required() -> None:
    with pytest.raises(ValidationError):
        PropertyStatus()
