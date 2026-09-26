"""
Generic, context-aware scientific evidence data model for food commodities.

Food properties vary significantly depending on cultivar, product form,
processing state, physiological maturity, temperature, relative humidity,
and duration. Every observation must preserve its context.

Conflicting observations from different sources must coexist as separate
records and are NOT averaged or aggregated prematurely.
"""

from typing import Any, List, Optional
from pydantic import BaseModel, Field

from app.schemas.property_status import PropertyStatusEnum


class FoodEvidenceRecord(BaseModel):
    """
    A single scientific observation or literature report for a food property.

    Retains full context (cultivar, maturity, processing, temperature, RH,
    measurement method, citation) to prevent misleading generalization.
    """

    # --- Commodity Taxonomy & State ---
    commodity: str = Field(
        ...,
        description="Standard common commodity name (e.g. 'apple', 'durian', 'salmon', 'strawberry')."
    )
    commodity_category: Optional[str] = Field(
        default=None,
        description="Broad category (e.g. 'fruit', 'vegetable', 'meat_poultry', 'seafood', 'dairy')."
    )
    variety: Optional[str] = Field(
        default=None,
        description="Cultivar or botanical variety (e.g. 'Fuji', 'Monthong', 'Hass', 'Atlantic')."
    )
    product_form: Optional[str] = Field(
        default=None,
        description="Physical state/geometry (e.g. 'whole', 'sliced', 'diced', 'fillet', 'puree')."
    )
    processing_state: Optional[str] = Field(
        default=None,
        description="Processing level (e.g. 'raw', 'fresh_cut', 'pasteurized', 'frozen', 'dried')."
    )
    maturity_stage: Optional[str] = Field(
        default=None,
        description="Ripeness or physiological maturity (e.g. 'unripe', 'mature_green', 'ripe')."
    )

    # --- Property & Measurement ---
    property: str = Field(
        ...,
        description="Standard property identifier (e.g. 'moisture_content', 'respiration_rate', 'ph')."
    )
    value: Optional[float] = Field(
        default=None,
        description="Point estimate or representative value. NULL if only a range is reported."
    )
    unit: Optional[str] = Field(
        default=None,
        description="SI or standard scientific unit (e.g. '%', 'mg CO2/kg/hr', 'dimensionless')."
    )
    value_type: Optional[str] = Field(
        default=None,
        description="Nature of value: 'mean', 'median', 'point_estimate', 'range', 'min', 'max'."
    )
    minimum_value: Optional[float] = Field(
        default=None,
        description="Lower bound of reported range or measurement confidence interval."
    )
    maximum_value: Optional[float] = Field(
        default=None,
        description="Upper bound of reported range or measurement confidence interval."
    )

    # --- Environmental & Experimental Context ---
    temperature: Optional[float] = Field(
        default=None,
        description="Temperature in °C at which the property was measured or observed."
    )
    relative_humidity: Optional[float] = Field(
        default=None,
        description="Relative humidity in % during measurement or storage."
    )
    storage_duration: Optional[float] = Field(
        default=None,
        description="Duration of storage prior to or during measurement (e.g. days or hours)."
    )
    measurement_method: Optional[str] = Field(
        default=None,
        description="Experimental assay or protocol (e.g. 'AOAC 934.01', 'Gas chromatography')."
    )

    # --- Provenance & Evidence Strength ---
    source_title: Optional[str] = Field(
        default=None,
        description="Title of published paper, book chapter, standard, or database entry."
    )
    publication_year: Optional[int] = Field(
        default=None,
        description="Year of publication."
    )
    DOI: Optional[str] = Field(
        default=None,
        description="Digital Object Identifier (e.g. '10.1016/j.postharvbio.2020.111222')."
    )
    URL: Optional[str] = Field(
        default=None,
        description="Direct stable URL to source or database record."
    )
    source_type: Optional[str] = Field(
        default=None,
        description="Origin type: 'journal_article', 'handbook', 'government_database', 'laboratory_measurement'."
    )
    evidence_strength: Optional[str] = Field(
        default=None,
        description="Evidence rating ('high', 'medium', 'low', 'unverified')."
    )
    notes: Optional[str] = Field(
        default=None,
        description="Specific experimental notes, cultivar origins, harvest conditions."
    )

    # --- Compatibility with PropertyStatus framework ---
    status: PropertyStatusEnum = Field(
        default=PropertyStatusEnum.literature,
        description="Epistemic status: 'measured', 'literature', 'inferred', 'unknown'."
    )
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score [0.0 - 1.0] if evaluated."
    )
    uncertainty_range: Optional[tuple[float, float]] = Field(
        default=None,
        description="Optional confidence interval (min, max)."
    )


class FoodEvidenceDataset(BaseModel):
    """
    Collection of scientific evidence records across multiple commodities.

    Enforces contextual preservation and non-destructive querying.
    """

    records: List[FoodEvidenceRecord] = Field(default_factory=list)

    def add_record(self, record: FoodEvidenceRecord) -> None:
        """Add an evidence record without overwriting existing observations."""
        self.records.append(record)

    def query(
        self,
        commodity: Optional[str] = None,
        property_name: Optional[str] = None,
        variety: Optional[str] = None,
        product_form: Optional[str] = None,
        temperature_min: Optional[float] = None,
        temperature_max: Optional[float] = None,
    ) -> List[FoodEvidenceRecord]:
        """
        Query matching evidence records while preserving all distinct observations.

        Returns all matching records without aggregating or averaging.
        """
        results: List[FoodEvidenceRecord] = []
        for r in self.records:
            if commodity and r.commodity.lower() != commodity.lower():
                continue
            if property_name and r.property.lower() != property_name.lower():
                continue
            if variety and r.variety and r.variety.lower() != variety.lower():
                continue
            if product_form and r.product_form and r.product_form.lower() != product_form.lower():
                continue
            if temperature_min is not None and (r.temperature is None or r.temperature < temperature_min):
                continue
            if temperature_max is not None and (r.temperature is None or r.temperature > temperature_max):
                continue
            results.append(r)
        return results

    def get_commodities(self) -> List[str]:
        """Return unique commodities present in the dataset."""
        return sorted(list({r.commodity for r in self.records}))
