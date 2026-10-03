"""
Repository Verification Script for PostgreSQL Integration.

Verifies:
1. PostgreSQL reachable on 127.0.0.1:5432
2. Correct database (food_packaging_db)
3. Alembic head and current revision consistency (b7e4a1c92d3f)
4. Presence of all 18 canonical tables
5. SELECT 1 execution via project database configuration
6. Core canonical table row counts matching ingestion requirements
7. Execution of canonical DataIngestionPipeline (idempotency check)
8. Execution of POST /api/v1/recommend endpoint against PostgreSQL
9. Pytest module collection
"""

import sys
import os
import socket
from pathlib import Path

# Add project root to sys.path
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import sqlalchemy
from sqlalchemy import inspect, text
from alembic.config import Config
from alembic import script
from alembic.runtime import migration
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.core.database import engine, SessionLocal
from backend.app.models import (
    Source, EvidenceRecord, FoodCommodity, FoodObservation,
    RespirationObservation, PostharvestStorageLimits, PostharvestGasTolerances,
    PackagingMaterial, MaterialBarrierObservation, MicrobialOrganism,
    MicrobialCardinalParameters, MicrobialGrowthKinetics, MicrobialGasInhibitionResponse,
    ValidationResult, DataTransformation
)
from backend.app.ingestion.pipeline import DataIngestionPipeline
from backend.app.main import app


def verify_postgresql_integration():
    print("=" * 60)
    print("AI-Food-Packaging-Optimizer PostgreSQL Integration Verification")
    print("=" * 60)

    # 1. PostgreSQL Reachability
    host = "127.0.0.1"
    port = 5432
    print(f"\n1. Testing PostgreSQL TCP reachability ({host}:{port})...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3.0)
    try:
        sock.connect((host, port))
        print("   -> TCP Connection Successful: TRUE")
    except Exception as e:
        print(f"   -> TCP Connection FAILED: {e}")
        sys.exit(1)
    finally:
        sock.close()

    # 2. Database Name & Connection
    print(f"\n2. Testing Database Connection ({settings.DATABASE_URL})...")
    with engine.connect() as conn:
        db_name = conn.execute(text("SELECT current_database()")).scalar()
        print(f"   -> Connected Database Name: {db_name}")
        assert db_name == "food_packaging_db", f"Expected 'food_packaging_db', got '{db_name}'"

    # 3. Alembic Head & Current Consistency
    print("\n3. Verifying Alembic Migration Head vs Current...")
    alembic_cfg = Config("alembic.ini")
    script_dir = script.ScriptDirectory.from_config(alembic_cfg)
    head_revision = script_dir.get_current_head()

    with engine.connect() as conn:
        context = migration.MigrationContext.configure(conn)
        current_revision = context.get_current_revision()

    print(f"   -> Alembic Script Head: {head_revision}")
    print(f"   -> Alembic Database Current: {current_revision}")
    assert head_revision == "b7e4a1c92d3f", f"Expected head 'b7e4a1c92d3f', got '{head_revision}'"
    assert current_revision == head_revision, f"Current ({current_revision}) != Head ({head_revision})"
    print("   -> Alembic Revisions are CONSISTENT.")

    # 4. Table Presence
    print("\n4. Verifying Expected Live PostgreSQL Tables...")
    inspector = inspect(engine)
    live_tables = set(inspector.get_table_names())
    expected_tables = {
        'alembic_version', 'data_transformation', 'evidence_record', 'food_commodity',
        'food_observation', 'material_barrier_observation', 'microbial_cardinal_parameters',
        'microbial_gas_inhibition_response', 'microbial_growth_kinetics', 'microbial_organism',
        'model_update_candidate', 'packaging_feedback_record', 'packaging_material',
        'postharvest_gas_tolerances', 'postharvest_storage_limits', 'respiration_observation',
        'source', 'validation_result'
    }

    missing_tables = expected_tables - live_tables
    print(f"   -> Total Live Tables Found: {len(live_tables)}")
    if missing_tables:
        print(f"   -> MISSING TABLES: {missing_tables}")
        sys.exit(1)
    print("   -> All 18 expected tables exist in public schema.")

    # 5. SELECT 1 Execution
    print("\n5. Executing 'SELECT 1' via Project Engine...")
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1")).scalar()
        print(f"   -> SELECT 1 Result: {res}")
        assert res == 1

    # 6. Canonical Table Row Counts Verification
    print("\n6. Verifying Canonical Data Row Counts in PostgreSQL...")
    db = SessionLocal()
    try:
        expected_counts = {
            "Source": (db.query(Source).count(), 9),
            "EvidenceRecord": (db.query(EvidenceRecord).count(), 47),
            "FoodCommodity": (db.query(FoodCommodity).count(), 17),
            "FoodObservation": (db.query(FoodObservation).count(), 20),
            "RespirationObservation": (db.query(RespirationObservation).count(), 38),
            "PostharvestStorageLimits": (db.query(PostharvestStorageLimits).count(), 15),
            "PostharvestGasTolerances": (db.query(PostharvestGasTolerances).count(), 13),
            "PackagingMaterial": (db.query(PackagingMaterial).count(), 11),
            "MaterialBarrierObservation": (db.query(MaterialBarrierObservation).count(), 34),
            "MicrobialOrganism": (db.query(MicrobialOrganism).count(), 5),
            "MicrobialCardinalParameters": (db.query(MicrobialCardinalParameters).count(), 5),
            "MicrobialGrowthKinetics": (db.query(MicrobialGrowthKinetics).count(), 6),
            "MicrobialGasInhibitionResponse": (db.query(MicrobialGasInhibitionResponse).count(), 5),
            "ValidationResult": (db.query(ValidationResult).count(), 9),
            "DataTransformation": (db.query(DataTransformation).count(), 14),
        }

        all_matched = True
        for entity, (actual, expected) in expected_counts.items():
            status_str = "MATCHED" if actual == expected else "MISMATCH"
            print(f"   -> {entity:32s}: {actual:2d} (Expected: {expected:2d}) [{status_str}]")
            if actual != expected:
                all_matched = False

        assert all_matched, "One or more table row counts did not match target canonical dataset."
    finally:
        db.close()

    # 7. Ingestion Pipeline Idempotency
    print("\n7. Testing DataIngestionPipeline Idempotency...")
    db = SessionLocal()
    try:
        pipeline = DataIngestionPipeline(db)
        stats = pipeline.run()
        print(f"   -> Re-run Total Inserted: {stats['total_inserted']}, Total Skipped: {stats['total_skipped']}")
        assert stats['total_inserted'] == 0, "Idempotency check failed: records were re-inserted."
        print("   -> Ingestion Pipeline is IDEMPOTENT.")
    finally:
        db.close()

    # 8. Recommendation Endpoint Verification
    print("\n8. Executing Real POST /api/v1/recommend Endpoint against PostgreSQL...")
    client = TestClient(app)
    payload = {
        'commodity': 'blueberry',
        'product_form': 'WHOLE',
        'ripeness_stage': 'RIPE',
        'storage_type': 'REFRIGERATED',
        'product_mass_kg': 0.5,
        'target_shelf_life_days': 14.0,
        'storage_temperature_c': 4.0,
        'relative_humidity_percent': 90.0,
        'package_surface_area_m2': 0.06,
        'package_headspace_volume_cm3': 500.0
    }
    response = client.post('/api/v1/recommend', json=payload)
    print(f"   -> HTTP Response Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    rec_data = response.json()
    print(f"   -> Recommendation Run ID: {rec_data.get('recommendation_run_id')}")
    print(f"   -> Total Candidates Evaluated: {rec_data.get('total_candidates_evaluated')}")
    print("   -> Recommendation Endpoint Test PASSED.")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE: ALL 8 INTEGRATION CHECKS PASSED SUCCESSFULLY.")
    print("=" * 60)


if __name__ == "__main__":
    verify_postgresql_integration()
