import json
import pytest
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
PROCESSED_DIR = ROOT_DIR / "data/processed"

def test_source_metadata_retained():
    p_path = PROCESSED_DIR / "materials/cirad_wur/cirad_wur_packaging_dataset.json"
    assert p_path.exists(), "Processed CIRAD file missing"
    with open(p_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "source_metadata" in data
    assert "url" in data["source_metadata"]

def test_numeric_parsing_applied():
    p_path = PROCESSED_DIR / "postharvest/uc_davis/uc_davis_produce_facts.json"
    with open(p_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data.get("records", [])
    assert len(records) > 0
    for rec in records:
        for rp in rec.get("respiration_profile", []):
            if "co2_production_rate_max_mg_kg_h" in rp:
                assert "co2_production_rate_max_mg_kg_h_parsed" in rp
                assert rp["co2_production_rate_max_mg_kg_h_parsed"]["operator"] == "="

def test_respiration_no_blind_units():
    p_path = PROCESSED_DIR / "postharvest/usda/usda_handbook_66_respiration.json"
    with open(p_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for rec in data.get("records", []):
        for rp in rec.get("respiration_measurements", []):
            assert "unit_tag" not in rp

def test_polyid_predictive_vs_experimental():
    p_path = PROCESSED_DIR / "materials/polyid/polyid_experimental_vs_predicted.json"
    with open(p_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "experimental_observations" in data
    assert "predicted_values" in data
    assert len(data["experimental_observations"]) == 2
    assert len(data["predicted_values"]) == 2
