"""
Generic scientific data model for packaging materials, multi-layer designs,
coatings, active packaging functionalities, and test-conditioned barrier properties.

Does NOT assign arbitrary barrier values, rankings, or universal superiority.
Every property measurement preserves experimental test conditions (ASTM/ISO standard,
temperature, relative humidity) and literature/measurement provenance.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.property_status import PropertyStatusEnum


class MaterialPropertyEvidence(BaseModel):
    """
    A single evidence-backed property measurement or specification for a material.

    Preserves test conditions (temperature, RH, test standard) because barrier
    metrics (OTR, WVTR) are strongly dependent on environmental conditions.
    """

    property: str = Field(
        ...,
        description="Standard property name (e.g. 'oxygen_transmission_rate', 'water_vapor_transmission_rate')."
    )
    value: Optional[float] = Field(
        default=None,
        description="Measured or reported property value."
    )
    unit: Optional[str] = Field(
        default=None,
        description="Measurement unit (e.g. 'cc/(m^2·day·atm)', 'g/(m^2·day)', 'MPa', '°C')."
    )
    value_type: Optional[str] = Field(
        default=None,
        description="Nature of value: 'mean', 'point_estimate', 'range', 'min', 'max', 'nominal'."
    )
    minimum_value: Optional[float] = Field(
        default=None,
        description="Lower bound if reported as a range."
    )
    maximum_value: Optional[float] = Field(
        default=None,
        description="Upper bound if reported as a range."
    )

    # --- Test / Environmental Conditions ---
    test_temperature_c: Optional[float] = Field(
        default=None,
        description="Temperature in °C during standard permeability/mechanical testing."
    )
    test_relative_humidity_percent: Optional[float] = Field(
        default=None,
        description="Relative humidity in % during standard testing (crucial for WVTR, EVOH OTR)."
    )
    test_standard: Optional[str] = Field(
        default=None,
        description="Standardized testing method (e.g. 'ASTM D3985', 'ASTM F1249', 'ISO 15106-2', 'ASTM D882')."
    )

    # --- Provenance ---
    source_title: Optional[str] = Field(
        default=None,
        description="Technical data sheet, standard handbook, or peer-reviewed publication."
    )
    publication_year: Optional[int] = Field(
        default=None,
        description="Publication year."
    )
    DOI: Optional[str] = Field(
        default=None,
        description="DOI identifier if sourced from peer-reviewed literature."
    )
    URL: Optional[str] = Field(
        default=None,
        description="URL to verified datasheet or publication."
    )
    source_type: Optional[str] = Field(
        default=None,
        description="'technical_datasheet', 'handbook', 'journal_article', 'laboratory_measurement'."
    )
    status: PropertyStatusEnum = Field(
        default=PropertyStatusEnum.literature,
        description="Epistemic status ('measured', 'literature', 'inferred', 'unknown')."
    )
    notes: Optional[str] = Field(
        default=None,
        description="Conditioning details, orientation, sample preparation notes."
    )


class LayerSpec(BaseModel):
    """Specification for an individual layer within a multi-layer or laminated structure."""

    material_type: str = Field(
        ...,
        description="Polymer or material designation (e.g. 'PET', 'Aluminium', 'LDPE', 'EVOH', 'PLA', 'Paper')."
    )
    thickness_um: Optional[float] = Field(
        default=None,
        description="Layer thickness in micrometers (µm)."
    )
    density_g_cm3: Optional[float] = Field(
        default=None,
        description="Material density in g/cm³."
    )
    function: Optional[str] = Field(
        default=None,
        description="Layer purpose (e.g. 'outer_print_layer', 'barrier_core', 'sealant_layer', 'tie_layer')."
    )
    notes: Optional[str] = Field(
        default=None,
        description="Copolymer composition, orientation (e.g. BOPP, BOPET, cast)."
    )


class CoatingSpec(BaseModel):
    """Specification for surface coatings applied to a film or substrate."""

    coating_type: str = Field(
        ...,
        description="Coating chemistry (e.g. 'AlOx', 'SiOx', 'PVDC', 'nanocellulose', 'chitosan', 'antifog')."
    )
    dry_thickness_um: Optional[float] = Field(
        default=None,
        description="Dry coating thickness in micrometers (µm)."
    )
    coat_weight_gsm: Optional[float] = Field(
        default=None,
        description="Coat weight in grams per square meter (g/m²)."
    )
    carrier_substrate: Optional[str] = Field(
        default=None,
        description="Substrate upon which coating is deposited (e.g. 'BOPET', 'Kraft paper')."
    )
    notes: Optional[str] = Field(default=None)


class ActiveFunctionalitySpec(BaseModel):
    """Specification for active packaging mechanisms (scavengers, emitters, absorbers)."""

    active_type: str = Field(
        ...,
        description="Type of active mechanism (e.g. 'oxygen_scavenger', 'moisture_absorber', 'ethylene_scavenger', 'antimicrobial')."
    )
    active_agent: Optional[str] = Field(
        default=None,
        description="Chemical or biological agent (e.g. 'ferrous iron', 'silica gel', 'potassium permanganate', 'thymol')."
    )
    capacity: Optional[float] = Field(
        default=None,
        description="Absorption / scavenging capacity."
    )
    capacity_unit: Optional[str] = Field(
        default=None,
        description="Capacity unit (e.g. 'mL O2/package', 'g H2O/g sachet')."
    )
    mechanism: Optional[str] = Field(
        default=None,
        description="Operating mechanism (e.g. 'chemical oxidation', 'adsorption', 'controlled release')."
    )
    food_contact_side: Optional[bool] = Field(
        default=None,
        description="Whether active layer is in direct contact with food or behind a permeable membrane."
    )
    notes: Optional[str] = Field(default=None)


class PackagingMaterialSpec(BaseModel):
    """
    Generic representation of a packaging material or engineered multi-layer structure.

    Supports monolayer polymers, coextruded films, adhesive laminates, foil structures,
    paper-based packaging, bio-polymers, coated substrates, and active packaging systems.
    """

    material_id: str = Field(
        ...,
        description="Unique identifier for the material specification (e.g. 'MAT-LDPE-50UM', 'MAT-PET-ALU-PE-TRIPLEX')."
    )
    material_name: str = Field(
        ...,
        description="Descriptive name of the material or composite structure."
    )
    material_category: str = Field(
        ...,
        description="Structural category (e.g. 'mono_polymer', 'coextruded_multilayer', 'laminated_multilayer', 'bio_based_polymer')."
    )
    structure_type: str = Field(
        ...,
        description="Physical format (e.g. 'monolayer_film', 'coextruded_film', 'adhesive_laminate', 'coated_paper', 'rigid_tray')."
    )
    total_thickness_um: Optional[float] = Field(
        default=None,
        description="Total nominal thickness in micrometers (µm)."
    )

    # --- Structural Composition ---
    layers: Optional[List[LayerSpec]] = Field(
        default=None,
        description="Layer stack for multi-layer films or laminates."
    )
    coatings: Optional[List[CoatingSpec]] = Field(
        default=None,
        description="Applied surface or barrier coatings."
    )
    active_functionalities: Optional[List[ActiveFunctionalitySpec]] = Field(
        default=None,
        description="Embedded active packaging mechanisms."
    )

    # --- Evidence-Backed Properties (grouped by property name) ---
    properties: Dict[str, List[MaterialPropertyEvidence]] = Field(
        default_factory=dict,
        description="Dictionary mapping property names to lists of contextual evidence observations."
    )

    # --- Regulatory, Safety & Sustainability Attributes ---
    food_contact_status: Optional[str] = Field(
        default=None,
        description="Compliance status (e.g. 'FDA_21CFR_compliant', 'EU_10_2011_compliant', 'non_food_contact')."
    )
    recyclability_class: Optional[str] = Field(
        default=None,
        description="Recyclability classification (e.g. 'mono_material_pe_stream', 'multi_material_non_recyclable')."
    )
    biodegradability_certified: Optional[bool] = Field(
        default=None,
        description="Whether certified biodegradable under industrial/home conditions."
    )
    compostability_standard: Optional[str] = Field(
        default=None,
        description="Applicable compostability certification standard (e.g. 'ASTM_D6400', 'EN_13432')."
    )
    notes: Optional[str] = Field(
        default=None,
        description="General application notes, commercial trade names, manufacturer details."
    )

    def add_property_evidence(self, evidence: MaterialPropertyEvidence) -> None:
        """Add a property measurement observation without overwriting existing test data."""
        if evidence.property not in self.properties:
            self.properties[evidence.property] = []
        self.properties[evidence.property].append(evidence)

    def get_property_evidence(self, property_name: str) -> List[MaterialPropertyEvidence]:
        """Retrieve all contextual observations for a specific property."""
        return self.properties.get(property_name, [])
