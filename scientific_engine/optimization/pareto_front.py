"""
M6-B4B: Pareto Front Construction.

Filters a population of evaluated candidates down to the non-dominated set
using the verified M6-B4A `dominates()` primitive.
"""
import uuid
from datetime import datetime, timezone
import time
from typing import List

from app.schemas.optimization import ParetoCandidate, ParetoFront, OptimizationMetadata
from app.schemas.physics import CalculationStatus
from scientific_engine.optimization.pareto import dominates

class ParetoFrontConstructor:
    """
    Deterministic, stateless Pareto front construction.
    """
    
    def __init__(self, run_id: str = None, policy_version: str = "1.0"):
        self.run_id = run_id or str(uuid.uuid4())
        self.policy_version = policy_version

    def filter_non_dominated(self, candidates: List[ParetoCandidate]) -> List[ParetoCandidate]:
        """
        O(N^2) exact dominance filtering using M6-B4A primitives.
        """
        non_dominated = []
        for i, cand_i in enumerate(candidates):
            # Check eligibility: If any objective is UNKNOWN, it cannot enter the deterministic front
            if any(obj.status == CalculationStatus.UNKNOWN for obj in cand_i.objective_values.values()):
                continue
                
            is_dominated = False
            for j, cand_j in enumerate(candidates):
                if i == j:
                    continue
                # If cand_j is ineligible, it cannot dominate anything anyway, 
                # but dominates() handles this correctly.
                if dominates(cand_j.objective_values, cand_i.objective_values):
                    is_dominated = True
                    break
            
            if not is_dominated:
                non_dominated.append(cand_i)
                
        return non_dominated

    def construct_front(self, candidates: List[ParetoCandidate]) -> ParetoFront:
        """
        Constructs the formal ParetoFront object from a list of candidates.
        """
        start_t = time.perf_counter()
        
        front_candidates = self.filter_non_dominated(candidates)
        
        exec_ms = (time.perf_counter() - start_t) * 1000.0
        
        meta = OptimizationMetadata(
            algorithm_name="exact_pairwise_dominance",
            iterations_completed=1,
            execution_time_ms=exec_ms,
            cache_hit=False
        )
        
        return ParetoFront(
            optimization_run_id=self.run_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            candidate_count=len(front_candidates),
            candidates=front_candidates,
            solver_metadata=meta,
            constraint_policy_version=self.policy_version
        )
