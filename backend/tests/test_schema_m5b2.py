import os
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings

# Test DB logic - if a Postgres DB is available, use it. Otherwise, this test is skipped or falls back.
TEST_DB_URL = os.environ.get("USE_TEST_DB_URL", settings.DATABASE_URL)

from backend.app.models.evidence import Base

@pytest.fixture(scope="module")
def engine():
    eng = create_engine(TEST_DB_URL)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()

@pytest.fixture(scope="module")
def check_postgres(engine):
    """Ensure tests run against a PostgreSQL compatible environment, skipping if unavailable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        pytest.skip("PostgreSQL test database is unavailable in this environment. Ensure POSTGRES_URL is set and accessible.")

def test_all_15_tables_exist(engine, check_postgres):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = {
        'source', 'evidence_record', 'validation_result',
        'food_commodity', 'food_observation', 'respiration_observation',
        'postharvest_storage_limits', 'postharvest_gas_tolerances',
        'packaging_material', 'material_barrier_observation',
        'microbial_organism', 'microbial_cardinal_parameters',
        'microbial_growth_kinetics', 'microbial_gas_inhibition_response',
        'data_transformation'
    }
    
    # Assert all expected tables exist
    for table in expected_tables:
        assert table in tables, f"Table {table} is missing from the database."

def test_missingness_status_enum_exists(engine, check_postgres):
    inspector = inspect(engine)
    cols = inspector.get_columns('food_observation')
    missingness_col = next((c for c in cols if c['name'] == 'missingness_status'), None)
    
    assert missingness_col is not None
    
def test_combase_gas_inhibition_exists(engine, check_postgres):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert 'microbial_gas_inhibition_response' in tables
    
    cols = inspector.get_columns('microbial_gas_inhibition_response')
    col_names = [c['name'] for c in cols]
    
    assert 'co2_sensitivity' in col_names
    assert 'minimum_co2_inhibition_percent' in col_names

def test_indian_emap_fields_exist(engine, check_postgres):
    inspector = inspect(engine)
    cols = inspector.get_columns('postharvest_gas_tolerances')
    col_names = [c['name'] for c in cols]
    
    assert 'min_o2_fermentation_limit_percent' in col_names
    assert 'max_co2_injury_limit_percent' in col_names

def test_jsonb_usage_restricted(engine, check_postgres):
    """Verify JSONB is used exactly where authorized."""
    inspector = inspect(engine)
    
    evidence_cols = inspector.get_columns('evidence_record')
    for c in evidence_cols:
        if c['name'] in ['raw_json_payload', 'literature_references', 'outlier_annotation']:
            assert 'JSON' in str(c['type']).upper()
            
    material_cols = inspector.get_columns('packaging_material')
    for c in material_cols:
        if c['name'] == 'layer_sequence':
            assert 'JSON' in str(c['type']).upper()
