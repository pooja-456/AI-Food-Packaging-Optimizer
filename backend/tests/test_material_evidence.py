import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from app.schemas.material_evidence import (
    PackagingMaterialSpec,
    MaterialPropertyEvidence,
    LayerSpec,
    CoatingSpec,
    ActiveFunctionalitySpec,
)
from app.schemas.property_status import PropertyStatusEnum
from app.schemas.vocabularies import (
    MaterialCategory,
    PackagingProperty,
)


# ---------------------------------------------------------------------------
# Test 1: Monolayer polymer representation
# ---------------------------------------------------------------------------

def test_monolayer_material_representation() -> None:
    mat = PackagingMaterialSpec(
        material_id="MAT-HDPE-50UM",
        material_name="High-Density Polyethylene Film",
        material_category=MaterialCategory.MONO_POLYMER.value,
        structure_type="monolayer_film",
        total_thickness_um=50.0,
        layers=[
            LayerSpec(
                material_type="HDPE",
                thickness_um=50.0,
                density_g_cm3=0.955,
                function="bulk_and_moisture_barrier",
            )
        ],
    )
    mat.add_property_evidence(
        MaterialPropertyEvidence(
            property=PackagingProperty.WVTR.value,
            value=5.0,
            unit="g/(m^2·day)",
            test_temperature_c=38.0,
            test_relative_humidity_percent=90.0,
            test_standard="ASTM F1249",
            status=PropertyStatusEnum.literature,
        )
    )

    assert mat.material_id == "MAT-HDPE-50UM"
    assert len(mat.layers) == 1
    assert mat.layers[0].material_type == "HDPE"
    wvtr_records = mat.get_property_evidence("water_vapor_transmission_rate")
    assert len(wvtr_records) == 1
    assert wvtr_records[0].value == 5.0
    assert wvtr_records[0].test_standard == "ASTM F1249"


# ---------------------------------------------------------------------------
# Test 2: Multilayer triplex laminate representation
# ---------------------------------------------------------------------------

def test_multilayer_laminate_representation() -> None:
    mat = PackagingMaterialSpec(
        material_id="MAT-PET-ALU-PE",
        material_name="PET/Alu/LDPE Triplex Barrier Laminate",
        material_category=MaterialCategory.FOIL_LAMINATE.value,
        structure_type="laminated_multilayer",
        total_thickness_um=71.0,
        layers=[
            LayerSpec(material_type="BOPET", thickness_um=12.0, function="outer_print"),
            LayerSpec(material_type="Aluminium", thickness_um=9.0, function="gas_barrier_core"),
            LayerSpec(material_type="LDPE", thickness_um=50.0, function="sealant"),
        ],
        food_contact_status="FDA_21CFR_compliant",
        recyclability_class="multi_material_non_recyclable",
    )

    assert len(mat.layers) == 3
    assert mat.layers[1].material_type == "Aluminium"
    assert mat.total_thickness_um == 71.0
    assert mat.food_contact_status == "FDA_21CFR_compliant"


# ---------------------------------------------------------------------------
# Test 3: Bio-based and compostable material representation
# ---------------------------------------------------------------------------

def test_biobased_material_representation() -> None:
    mat = PackagingMaterialSpec(
        material_id="MAT-PLA-30UM",
        material_name="Polylactic Acid Film",
        material_category=MaterialCategory.BIODEGRADABLE_POLYMER.value,
        structure_type="monolayer_film",
        total_thickness_um=30.0,
        biodegradability_certified=True,
        compostability_standard="ASTM_D6400_EN_13432",
    )
    mat.add_property_evidence(
        MaterialPropertyEvidence(
            property="biobased_content",
            value=100.0,
            unit="%",
            status=PropertyStatusEnum.literature,
        )
    )

    assert mat.biodegradability_certified is True
    assert mat.compostability_standard == "ASTM_D6400_EN_13432"
    assert mat.get_property_evidence("biobased_content")[0].value == 100.0


# ---------------------------------------------------------------------------
# Test 4: Active packaging and coated substrate representation
# ---------------------------------------------------------------------------

def test_active_and_coated_packaging_representation() -> None:
    mat = PackagingMaterialSpec(
        material_id="MAT-ACTIVE-SCAVENGER-TRAY",
        material_name="O2-Scavenging Coated Barrier Tray",
        material_category=MaterialCategory.ACTIVE_FUNCTIONAL.value,
        structure_type="coated_thermoformed_tray",
        coatings=[
            CoatingSpec(
                coating_type="AlOx",
                dry_thickness_um=0.05,
                carrier_substrate="PET",
                notes="Ultra-thin transparent ceramic barrier layer",
            )
        ],
        active_functionalities=[
            ActiveFunctionalitySpec(
                active_type="oxygen_scavenger",
                active_agent="ferrous_iron_complex",
                capacity=50.0,
                capacity_unit="mL O2/tray",
                mechanism="chemical_oxidation",
                food_contact_side=False,
            )
        ],
    )

    assert len(mat.coatings) == 1
    assert mat.coatings[0].coating_type == "AlOx"
    assert len(mat.active_functionalities) == 1
    assert mat.active_functionalities[0].active_type == "oxygen_scavenger"
    assert mat.active_functionalities[0].capacity == 50.0


# ---------------------------------------------------------------------------
# Test 5: Environmental dependence of barrier properties (EVOH RH sensitivity)
# ---------------------------------------------------------------------------

def test_barrier_environmental_dependence_coexistence() -> None:
    mat = PackagingMaterialSpec(
        material_id="MAT-EVOH-15UM",
        material_name="EVOH Copolymer Film (15 µm)",
        material_category=MaterialCategory.MONO_POLYMER.value,
        structure_type="monolayer_film",
        total_thickness_um=15.0,
    )
    # Dry test condition: 23°C, 0% RH
    mat.add_property_evidence(
        MaterialPropertyEvidence(
            property="oxygen_transmission_rate",
            value=0.4,
            unit="cc/(m^2·day·atm)",
            test_temperature_c=23.0,
            test_relative_humidity_percent=0.0,
            test_standard="ASTM D3985",
            status=PropertyStatusEnum.literature,
        )
    )
    # Humid test condition: 23°C, 85% RH
    mat.add_property_evidence(
        MaterialPropertyEvidence(
            property="oxygen_transmission_rate",
            value=5.2,
            unit="cc/(m^2·day·atm)",
            test_temperature_c=23.0,
            test_relative_humidity_percent=85.0,
            test_standard="ASTM D3985",
            status=PropertyStatusEnum.literature,
        )
    )

    otr_list = mat.get_property_evidence("oxygen_transmission_rate")
    assert len(otr_list) == 2

    # Both distinct measurements coexist with their respective RH conditions
    rh_0 = [e for e in otr_list if e.test_relative_humidity_percent == 0.0][0]
    rh_85 = [e for e in otr_list if e.test_relative_humidity_percent == 85.0][0]

    assert rh_0.value == 0.4
    assert rh_85.value == 5.2


# ---------------------------------------------------------------------------
# Test 6: Missing properties remain NULL/None
# ---------------------------------------------------------------------------

def test_missing_material_fields_remain_null() -> None:
    mat = PackagingMaterialSpec(
        material_id="MAT-GENERIC",
        material_name="Generic Test Material",
        material_category="generic",
        structure_type="film",
    )
    assert mat.total_thickness_um is None
    assert mat.layers is None
    assert mat.coatings is None
    assert mat.active_functionalities is None
    assert mat.food_contact_status is None
    assert mat.recyclability_class is None
    assert mat.biodegradability_certified is None
    assert mat.compostability_standard is None
    assert mat.properties == {}


# ---------------------------------------------------------------------------
# Test 7: Reference dataset JSON parses and validates correctly
# ---------------------------------------------------------------------------

def test_reference_packaging_materials_json_validity() -> None:
    ref_path = Path(__file__).resolve().parent.parent.parent / "data" / "reference" / "packaging_materials.json"
    assert ref_path.exists(), f"Reference file not found at {ref_path}"

    with open(ref_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) > 0

    materials = [PackagingMaterialSpec(**item) for item in data]
    mat_ids = [m.material_id for m in materials]

    assert "MAT-LDPE-50UM" in mat_ids
    assert "MAT-BOPET-12UM" in mat_ids
    assert "MAT-EVOH-15UM" in mat_ids
    assert "MAT-TRIPLEX-PET-ALU-PE" in mat_ids
    assert "MAT-PLA-30UM" in mat_ids
