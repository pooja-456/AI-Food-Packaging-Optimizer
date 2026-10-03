"""
M6-B4A: Pareto Dominance Primitive.

Evaluates if Candidate A mathematically dominates Candidate B in multi-objective space,
incorporating interval bounding for uncertain values as explicitly defined by M6-A.
"""

from typing import Dict
from app.schemas.optimization import ObjectiveValue, ObjectiveDirection
from app.schemas.physics import CalculationStatus

def dominates(
    objectives_a: Dict[str, ObjectiveValue],
    objectives_b: Dict[str, ObjectiveValue]
) -> bool:
    """
    Evaluates whether Candidate A strictly dominates Candidate B.
    
    A dominates B iff:
    1. A is no worse than B in EVERY objective (using conservative interval worst-cases).
    2. A is strictly better than B in AT LEAST ONE objective.
    
    If either A or B contains UNKNOWN objectives, dominance cannot be established
    and returns False. INFEASIBLE candidates should have UNKNOWN objectives per B3.
    """
    # M6-A active objectives
    active_keys = ["f_thickness", "f_moisture_margin", "f_gas_alignment", "f_shelf_life_margin"]
    
    # Must have all objectives
    for k in active_keys:
        if k not in objectives_a or k not in objectives_b:
            return False
            
    strictly_better_once = False
    
    for k in active_keys:
        obj_a = objectives_a[k]
        obj_b = objectives_b[k]
        
        # If any objective is UNKNOWN, we cannot establish dominance
        if obj_a.status == CalculationStatus.UNKNOWN or obj_b.status == CalculationStatus.UNKNOWN:
            return False
            
        # Extract worst-case A and best-case B
        if obj_a.direction == ObjectiveDirection.MINIMIZE:
            wc_a = obj_a.value_max if obj_a.is_interval and obj_a.value_max is not None else obj_a.value
            bc_b = obj_b.value_min if obj_b.is_interval and obj_b.value_min is not None else obj_b.value
            
            if wc_a is None or bc_b is None:
                return False
                
            if wc_a > bc_b:
                return False # A is worse than B in this objective
                
            if wc_a < bc_b:
                strictly_better_once = True
                
        elif obj_a.direction == ObjectiveDirection.MAXIMIZE:
            wc_a = obj_a.value_min if obj_a.is_interval and obj_a.value_min is not None else obj_a.value
            bc_b = obj_b.value_max if obj_b.is_interval and obj_b.value_max is not None else obj_b.value
            
            if wc_a is None or bc_b is None:
                return False
                
            if wc_a < bc_b:
                return False # A is worse than B in this objective
                
            if wc_a > bc_b:
                strictly_better_once = True
                
    return strictly_better_once
