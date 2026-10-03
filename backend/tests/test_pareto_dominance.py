"""
Tests for M6-B4A Pareto Dominance Engine.
"""

import pytest

from app.schemas.optimization import ObjectiveValue, ObjectiveDirection
from app.schemas.physics import CalculationStatus
from scientific_engine.optimization.pareto import dominates

def _obj(name: str, val: float, direction: ObjectiveDirection) -> ObjectiveValue:
    return ObjectiveValue(
        objective_name=name,
        direction=direction,
        value=val,
        unit="unit",
        status=CalculationStatus.CALCULATED
    )

def _interval_obj(name: str, val_min: float, val_max: float, direction: ObjectiveDirection) -> ObjectiveValue:
    return ObjectiveValue(
        objective_name=name,
        direction=direction,
        value_min=val_min,
        value_max=val_max,
        is_interval=True,
        unit="unit",
        status=CalculationStatus.CALCULATED
    )

def _unknown_obj(name: str, direction: ObjectiveDirection) -> ObjectiveValue:
    return ObjectiveValue(
        objective_name=name,
        direction=direction,
        status=CalculationStatus.UNKNOWN,
        unit="unit"
    )

def _build_vector(t: float, m: float, g: float, s: float):
    return {
        "f_thickness": _obj("f_thickness", t, ObjectiveDirection.MINIMIZE),
        "f_moisture_margin": _obj("f_moisture_margin", m, ObjectiveDirection.MAXIMIZE),
        "f_gas_alignment": _obj("f_gas_alignment", g, ObjectiveDirection.MINIMIZE),
        "f_shelf_life_margin": _obj("f_shelf_life_margin", s, ObjectiveDirection.MAXIMIZE)
    }

def test_strictly_dominates():
    # A is better in all
    a = _build_vector(10.0, 0.9, 0.1, 5.0)
    b = _build_vector(20.0, 0.5, 0.4, 2.0)
    assert dominates(a, b) is True
    assert dominates(b, a) is False

def test_dominates_equal_mixed():
    # A is equal in 3, strictly better in 1
    a = _build_vector(10.0, 0.5, 0.4, 2.0)
    b = _build_vector(20.0, 0.5, 0.4, 2.0)
    assert dominates(a, b) is True
    assert dominates(b, a) is False

def test_no_dominance_mixed():
    # A better in thickness, B better in moisture
    a = _build_vector(10.0, 0.5, 0.4, 2.0)
    b = _build_vector(20.0, 0.9, 0.4, 2.0)
    assert dominates(a, b) is False
    assert dominates(b, a) is False

def test_equality_does_not_dominate():
    a = _build_vector(10.0, 0.5, 0.4, 2.0)
    b = _build_vector(10.0, 0.5, 0.4, 2.0)
    assert dominates(a, b) is False
    assert dominates(b, a) is False

def test_unknown_does_not_dominate():
    a = _build_vector(10.0, 0.5, 0.4, 2.0)
    b = _build_vector(20.0, 0.5, 0.4, 2.0)
    b["f_thickness"] = _unknown_obj("f_thickness", ObjectiveDirection.MINIMIZE)
    
    assert dominates(a, b) is False
    assert dominates(b, a) is False

def test_interval_dominance():
    # A's worst case (max 15) is better than B's best case (min 20)
    # So A dominates B
    a = {
        "f_thickness": _interval_obj("f_thickness", 10.0, 15.0, ObjectiveDirection.MINIMIZE),
        "f_moisture_margin": _obj("f_moisture_margin", 0.9, ObjectiveDirection.MAXIMIZE),
        "f_gas_alignment": _obj("f_gas_alignment", 0.1, ObjectiveDirection.MINIMIZE),
        "f_shelf_life_margin": _obj("f_shelf_life_margin", 5.0, ObjectiveDirection.MAXIMIZE)
    }
    
    b = {
        "f_thickness": _interval_obj("f_thickness", 20.0, 25.0, ObjectiveDirection.MINIMIZE),
        "f_moisture_margin": _obj("f_moisture_margin", 0.5, ObjectiveDirection.MAXIMIZE),
        "f_gas_alignment": _obj("f_gas_alignment", 0.4, ObjectiveDirection.MINIMIZE),
        "f_shelf_life_margin": _obj("f_shelf_life_margin", 2.0, ObjectiveDirection.MAXIMIZE)
    }
    assert dominates(a, b) is True
    assert dominates(b, a) is False

def test_interval_overlap_no_dominance():
    # A's worst case (max 22) is NOT better than B's best case (min 18)
    a = _build_vector(10.0, 0.9, 0.1, 5.0)
    a["f_thickness"] = _interval_obj("f_thickness", 10.0, 22.0, ObjectiveDirection.MINIMIZE)
    
    b = _build_vector(10.0, 0.5, 0.4, 2.0)
    b["f_thickness"] = _interval_obj("f_thickness", 18.0, 25.0, ObjectiveDirection.MINIMIZE)
    
    # Neither dominates
    assert dominates(a, b) is False
    assert dominates(b, a) is False
