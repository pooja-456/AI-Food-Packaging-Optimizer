from typing import Optional
from pydantic import BaseModel, field_validator


class PackagingRequest(BaseModel):
    """
    Structured input model for a food packaging recommendation request.

    Required fields capture logistics and handling intent.
    Optional scientific fields are left to the caller; they are never
    fabricated or inferred at this stage.
    """

    # --- Required logistics fields ---
    commodity: str
    product_form: str
    ripeness_stage: str
    target_shelf_life_days: int
    storage_type: str

    # --- Optional logistics fields ---
    variety: Optional[str] = None
    transportation_type: Optional[str] = None
    transportation_duration_days: Optional[float] = None

    # --- Optional scientific / environmental fields ---
    storage_temperature_c: Optional[float] = None
    relative_humidity_percent: Optional[float] = None

    # --- Optional food-science properties ---
    moisture_percent: Optional[float] = None
    fat_percent: Optional[float] = None
    ph: Optional[float] = None
    respiration_rate: Optional[float] = None

    # --- Optional package geometry / product mass fields ---
    package_surface_area_m2: Optional[float] = None
    package_headspace_volume_cm3: Optional[float] = None
    product_mass_kg: Optional[float] = None

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("target_shelf_life_days")
    @classmethod
    def shelf_life_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("target_shelf_life_days must be a positive integer.")
        return v

    @field_validator("relative_humidity_percent")
    @classmethod
    def humidity_in_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError("relative_humidity_percent must be between 0 and 100.")
        return v

    @field_validator("moisture_percent")
    @classmethod
    def moisture_in_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError("moisture_percent must be between 0 and 100.")
        return v

    @field_validator("fat_percent")
    @classmethod
    def fat_in_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError("fat_percent must be between 0 and 100.")
        return v

    @field_validator("ph")
    @classmethod
    def ph_in_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 14.0):
            raise ValueError("ph must be between 0 and 14.")
        return v

    @field_validator("transportation_duration_days")
    @classmethod
    def transportation_duration_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("transportation_duration_days must not be negative.")
        return v

    @field_validator("respiration_rate")
    @classmethod
    def respiration_rate_not_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("respiration_rate must not be negative.")
        return v
