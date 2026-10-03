"""
Tests for M6-B5 Lattice Contracts.
"""
import pytest
from app.schemas.lattice import (
    LatticeCoordinate, LatticeMetadata, LatticePoint, 
    LatticeLookupResult, LatticeLookupStatus
)
from app.schemas.optimization import ParetoFront, OptimizationMetadata

def _mock_pareto_front():
    meta = OptimizationMetadata(
        algorithm_name="mock",
        iterations_completed=1,
        execution_time_ms=10.0,
        cache_hit=False
    )
    return ParetoFront(
        optimization_run_id="run-123",
        timestamp="2026-01-01T00:00:00Z",
        candidate_count=0,
        candidates=[],
        solver_metadata=meta,
        constraint_policy_version="1.0"
    )

def test_lattice_coordinate_deterministic_key():
    c1 = LatticeCoordinate(
        commodity="Durian", 
        target_shelf_life_days_bin=14, 
        storage_temperature_c_bin=4.0, 
        relative_humidity_percent_bin=90.0
    )
    c2 = LatticeCoordinate(
        commodity="durian  ", 
        target_shelf_life_days_bin=14, 
        storage_temperature_c_bin=4.00, 
        relative_humidity_percent_bin=90.00
    )
    assert c1.canonical_key == c2.canonical_key

def test_different_coordinate_different_key():
    c1 = LatticeCoordinate(
        commodity="Apple", 
        target_shelf_life_days_bin=14, 
        storage_temperature_c_bin=4.0, 
        relative_humidity_percent_bin=90.0
    )
    c2 = LatticeCoordinate(
        commodity="Apple", 
        target_shelf_life_days_bin=30, 
        storage_temperature_c_bin=4.0, 
        relative_humidity_percent_bin=90.0
    )
    assert c1.canonical_key != c2.canonical_key

def test_lattice_point_preserves_pareto_front():
    c = LatticeCoordinate(
        commodity="Apple", 
        target_shelf_life_days_bin=14, 
        storage_temperature_c_bin=4.0, 
        relative_humidity_percent_bin=90.0
    )
    meta = LatticeMetadata(
        lattice_version="1.0",
        physics_model_version="1.2",
        evidence_database_version="v5"
    )
    front = _mock_pareto_front()
    point = LatticePoint(
        coordinate=c,
        canonical_key=c.canonical_key,
        pareto_front=front,
        metadata=meta
    )
    assert point.pareto_front.optimization_run_id == "run-123"

def test_lattice_lookup_result_preserves_original_values():
    c = LatticeCoordinate(
        commodity="Apple", 
        target_shelf_life_days_bin=14, 
        storage_temperature_c_bin=5.0, 
        relative_humidity_percent_bin=90.0
    )
    res = LatticeLookupResult(
        status=LatticeLookupStatus.HIT,
        original_commodity="Apple",
        original_target_shelf_life_days=15,  # Original 15
        original_storage_temperature_c=4.8,  # Original 4.8
        original_relative_humidity_percent=88.5, # Original 88.5
        matched_coordinate=c,
        pareto_front=_mock_pareto_front()
    )
    
    assert res.original_target_shelf_life_days == 15
    assert res.matched_coordinate.target_shelf_life_days_bin == 14
    assert res.original_storage_temperature_c == 4.8
    assert res.matched_coordinate.storage_temperature_c_bin == 5.0
    
def test_lattice_lookup_miss():
    res = LatticeLookupResult(
        status=LatticeLookupStatus.MISS,
        original_commodity="Strawberry",
        original_target_shelf_life_days=7,
        original_storage_temperature_c=2.0,
        original_relative_humidity_percent=95.0
    )
    assert res.status == LatticeLookupStatus.MISS
    assert res.matched_coordinate is None
    assert res.pareto_front is None
