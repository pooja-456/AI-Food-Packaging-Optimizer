"""
Tests for M8 End-to-End Recommendation Pipeline and API Endpoint.
"""

import pytest
import httpx
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.schemas.packaging_request import PackagingRequest
from backend.app.services.recommendation_service import RecommendationService
from backend.app.schemas.constraints import ConstraintStatus


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_service_end_to_end_flow(db_session: Session):
    req = PackagingRequest(
        commodity="apple",
        product_form="fresh",
        ripeness_stage="mature",
        target_shelf_life_days=14,
        storage_type="chilled",
        storage_temperature_c=4.0,
        relative_humidity_percent=90.0,
        package_surface_area_m2=0.06,
        package_headspace_volume_cm3=500.0,
        product_mass_kg=0.5
    )

    service = RecommendationService()
    res = service.generate_recommendation(req, db_session)

    # 1. Valid request reaches pipeline
    assert res.request.commodity == "apple"
    assert res.request.target_shelf_life_days == 14

    # 2. Property inference invoked
    assert res.inference_profile.commodity == "apple"
    assert res.inference_profile.overall_confidence > 0.0

    # 3. Phase 4 requirements generated
    assert res.requirement_envelope is not None
    assert res.requirement_envelope.target_shelf_life_days == 14

    # 4. Phase 5 constraints & candidate evaluation
    assert res.total_candidates_evaluated > 0
    assert len(res.candidate_summaries) == res.total_candidates_evaluated

    # 5. Objectives & Pareto front constructed
    assert res.pareto_front is not None
    assert res.pareto_front.solver_metadata.algorithm_name in ["DETERMINISTIC_EXHAUSTIVE_ENUMERATION_BASELINE", "M8_EXACT_PARETO_PIPELINE"]

    # 6. Check status counts match
    assert res.feasible_candidates_count + res.infeasible_candidates_count + res.unknown_candidates_count == res.total_candidates_evaluated


def test_unknown_not_converted_to_feasible(db_session: Session):
    req = PackagingRequest(
        commodity="apple",
        product_form="fresh",
        ripeness_stage="mature",
        target_shelf_life_days=14,
        storage_type="chilled",
        storage_temperature_c=4.0,
        relative_humidity_percent=90.0
    )

    service = RecommendationService()
    res = service.generate_recommendation(req, db_session)

    # Candidates marked UNKNOWN must NOT be in the feasible Pareto front
    unknown_summaries = [c for c in res.candidate_summaries if c.constraint_status == ConstraintStatus.UNKNOWN.value]
    pareto_cand_ids = {c.pareto_candidate_id for c in res.pareto_front.candidates}

    for unk in unknown_summaries:
        assert unk.candidate_id not in pareto_cand_ids


def test_interval_values_remain_intervals(db_session: Session):
    req = PackagingRequest(
        commodity="apple",
        product_form="fresh",
        ripeness_stage="mature",
        target_shelf_life_days=14,
        storage_type="chilled",
        storage_temperature_c=4.0,
        relative_humidity_percent=90.0
    )

    service = RecommendationService()
    res = service.generate_recommendation(req, db_session)

    # Check objective values across pareto candidates preserve interval metadata
    for p_cand in res.pareto_front.candidates:
        for obj_name, obj_val in p_cand.objective_values.items():
            assert hasattr(obj_val, "is_interval")
            assert hasattr(obj_val, "value_min")
            assert hasattr(obj_val, "value_max")


@pytest.mark.anyio
async def test_api_recommendation_endpoint(db_session: Session):
    payload = {
        "commodity": "apple",
        "product_form": "fresh",
        "ripeness_stage": "mature",
        "target_shelf_life_days": 14,
        "storage_type": "chilled",
        "storage_temperature_c": 4.0,
        "relative_humidity_percent": 90.0,
        "package_surface_area_m2": 0.06,
        "package_headspace_volume_cm3": 500.0,
        "product_mass_kg": 0.5
    }

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver"
    ) as client:
        response = await client.post("/api/v1/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["recommendation_run_id"].startswith("run-")
        assert data["request"]["commodity"] == "apple"
        assert "pareto_front" in data
        assert "total_candidates_evaluated" in data
        assert data["total_candidates_evaluated"] > 0
