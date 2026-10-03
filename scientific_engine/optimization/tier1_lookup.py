"""
M6-H (B5D): Exact Tier-1 Lookup Engine Implementation.

Provides exact lookup against stored PrecomputedOptimizationState records.

Adheres strictly to docs/m6b5d_exact_tier1_lookup_contract.md:
- Compares all four frozen identity components via M6-F canonical representation.
- EXACT_HIT: Returns verbatim stored ParetoFront with solver_metadata.cache_hit = True.
- EXACT_MISS: Returns EXACT_MISS without attempting similarity search or optimization.
- ZERO float rounding, epsilon tolerances, nearest-neighbor, or store mutation.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from app.schemas.optimization import (
    OptimizationInputEnvelope,
    PackageGeometry,
    PackagingCandidate,
    ParetoFront
)
from app.schemas.packaging_requirements import PackagingRequirementEnvelope
from scientific_engine.optimization.canonical_representation import (
    build_canonical_representation
)
from scientific_engine.optimization.precomputed_store import (
    BaseOptimizationStateStore,
    PrecomputedOptimizationState
)


class Tier1LookupStatus(str, Enum):
    """Result status of Tier-1 exact lookup execution."""
    EXACT_HIT = "EXACT_HIT"
    EXACT_MISS = "EXACT_MISS"


class Tier1LookupResult(BaseModel):
    """Result payload returned by Tier-1 exact lookup."""

    status: Tier1LookupStatus = Field(
        ...,
        description="Lookup outcome (EXACT_HIT or EXACT_MISS)."
    )
    precomputed_state: Optional[PrecomputedOptimizationState] = Field(
        default=None,
        description="Retrieved precomputed state object on EXACT_HIT, None on EXACT_MISS."
    )
    pareto_front: Optional[ParetoFront] = Field(
        default=None,
        description="Verbatim ParetoFront object on EXACT_HIT (with cache_hit=True), None on EXACT_MISS."
    )


class Tier1ExactLookupEngine:
    """
    Tier-1 Exact Lookup Engine.
    Performs exact deterministic matching of the frozen Optimization-State Identity.
    """

    def __init__(self, store: BaseOptimizationStateStore) -> None:
        self.store = store

    def lookup(
        self,
        requirement_envelope: PackagingRequirementEnvelope,
        package_geometry: PackageGeometry,
        active_objectives: List[str],
        eligible_candidate_materials: Union[List[PackagingCandidate], List[str]]
    ) -> Tier1LookupResult:
        """
        Execute exact Tier-1 lookup.
        Compares all 4 frozen identity components using M6-F canonical representation.
        Does NOT mutate the store, recalculate objectives, or perform similarity matching.
        """
        canon_repr = build_canonical_representation(
            requirement_envelope=requirement_envelope,
            package_geometry=package_geometry,
            active_objectives=active_objectives,
            eligible_candidate_materials=eligible_candidate_materials
        )
        
        canon_json = canon_repr.to_canonical_json()
        stored_state = self.store.get_by_canonical_json(canon_json)

        if stored_state is None:
            return Tier1LookupResult(
                status=Tier1LookupStatus.EXACT_MISS,
                precomputed_state=None,
                pareto_front=None
            )

        # EXACT_HIT: return deep copies and set cache_hit = True on returned ParetoFront metadata copy
        result_state = stored_state.model_copy(deep=True)
        pareto_front_copy = result_state.pareto_front.model_copy(deep=True)
        pareto_front_copy.solver_metadata.cache_hit = True

        return Tier1LookupResult(
            status=Tier1LookupStatus.EXACT_HIT,
            precomputed_state=result_state,
            pareto_front=pareto_front_copy
        )

    def lookup_from_input_envelope(
        self,
        envelope: OptimizationInputEnvelope
    ) -> Tier1LookupResult:
        """
        Execute exact lookup directly from an OptimizationInputEnvelope.
        Extracts ONLY the 4 frozen identity components.
        """
        return self.lookup(
            requirement_envelope=envelope.packaging_requirement_envelope,
            package_geometry=envelope.package_geometry,
            active_objectives=envelope.active_objectives,
            eligible_candidate_materials=envelope.eligible_candidate_materials
        )
