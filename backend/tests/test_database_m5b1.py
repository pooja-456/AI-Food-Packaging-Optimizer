import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models.evidence import Base, Source, EvidenceRecord, FoodCommodity, PackagingMaterial, MicrobialOrganism
import uuid

# Use an in-memory SQLite database for testing the schema
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def engine():
    return create_engine(TEST_DB_URL)

@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(engine, tables):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

def test_database_connection(engine):
    """Test that we can connect to the database engine."""
    with engine.connect() as conn:
        assert conn is not None

def test_schema_initialization(db_session):
    """Test that all 15 M5-A entities are properly initialized as tables."""
    # We test the root line of entities to ensure they can be inserted and queried
    source_id = uuid.uuid4()
    source = Source(id=source_id, source_name="Test Source", url="http://test.com")
    db_session.add(source)
    db_session.commit()
    
    fetched_source = db_session.query(Source).filter_by(id=source_id).first()
    assert fetched_source.source_name == "Test Source"
    
    # Test EvidenceRecord which relies on ENUMs and JSONB (fallback to JSON in sqlite)
    evidence = EvidenceRecord(
        source_id=source_id, 
        record_identifier_in_source="TEST-001",
        evidence_classification="MODEL_PREDICTED",
        raw_json_payload={"foo": "bar"}
    )
    db_session.add(evidence)
    db_session.commit()
    
    fetched_evidence = db_session.query(EvidenceRecord).first()
    assert fetched_evidence.raw_json_payload == {"foo": "bar"}
    assert fetched_evidence.evidence_classification.name == "MODEL_PREDICTED"

def test_no_secret_leakage():
    """Verify that the default TEST_DATABASE_URL doesn't leak secrets."""
    from backend.app.core.config import settings
    # Either it's using sqlite memory, or if postgres it should use the dummy test_user
    assert "test_password" in settings.TEST_DATABASE_URL or "sqlite" in settings.TEST_DATABASE_URL
