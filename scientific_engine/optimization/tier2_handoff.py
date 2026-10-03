"""
M6-J (B5E): Tier-2 Warm-Start Handoff Interface Implementation.

Establishes the formal boundary between Tier-1 exact precomputed-state reuse
and Tier-2 warm-start refinement.

Adheres strictly to docs/m6b5e_tier2_warm_start_state_selection_contract.md:
- Only triggered upon Tier-1 EXACT_MISS.
- Preserves target Optimization-State Identity verbatim (Phase 4 Envelope, Geometry, Active Objectives, Eligible Candidate IDs).
- Exposes unranked, unselected available stored states without performing similarity search, nearest-neighbor, ranking, or distance calculations.
- Enforces mandatory target re-evaluation flag for future Tier-2 refinement components.
- Pure handoff DTO/factory layer: ZERO optimization, ZERO physics recalculation, ZERO Phase 5 evaluation, ZERO Pareto recalculation.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from app.schemas.optimization import PackageGeometry, PackagingCandidate
from app.schemas.packaging_requirements import PackagingRequirementEnvelope
from scientific_engine.optimization.canonical_representation import (
    CanonicalOptimizationState,
    build_canonical_representation
)
from scientific_engine.optimization.tier1_lookup import (
    Tier1LookupResult,
    Tier1LookupStatus
)

if TYPE_CHECKING:
    from scientific_engine.optimization.precomputed_store import (
        BaseOptimizationStateStore,
        PrecomputedOptimizationState
    )


class Tier2HandoffRequest(BaseModel):
    """
    Typed payload representing a Tier-2 warm-start handoff request.
    Encapsulates the target optimization state identity, lookup status, and unranked available states.
    """

    tier1_lookup_status: Tier1LookupStatus = Field(
        ...,
        description="Lookup status from Tier-1 (must be EXACT_MISS)."
    )
    requirement_envelope: PackagingRequirementEnvelope = Field(
        ...,
        description="Target Phase 4 PackagingRequirementEnvelope preserved verbatim."
    )
    package_geometry: PackageGeometry = Field(
        ...,
        description="Target PackageGeometry preserved verbatim."
    )
    active_objectives: List[str] = Field(
        ...,
        description="Target active objective set preserved verbatim."
    )
    eligible_candidate_materials: List[PackagingCandidate] = Field(
        ...,
        description="Target eligible PackagingCandidate materials preserved verbatim."
    )
    target_canonical_representation: CanonicalOptimizationState = Field(
        ...,
        description="Derived M6-F canonical representation for target state."
    )
    available_stored_states: List[Any] = Field(
        default_factory=list,
        description="Unranked, unselected collection of available stored states from the precomputed store."
    )
    requires_target_reevaluation: bool = Field(
        default=True,
        description="Mandatory architectural flag: any extracted seed state MUST undergo target search-space filtering, Phase 5 hard constraint re-evaluation, M6-B2B candidate evaluation, and M6-B3 objective evaluation before warm-start refinement."
    )

    def get_target_eligible_candidate_ids(self) -> List[str]:
        """Extract candidate IDs from target eligible materials list."""
        return [cand.candidate_id for cand in self.eligible_candidate_materials]


class Tier2HandoffEngine:
    """
    Tier-2 Warm-Start Handoff Boundary.
    Packages a Tier-1 EXACT_MISS into a structured Tier2HandoffRequest for future selection/refinement.
    Does NOT select, rank, sort, or score candidate states.
    """

    def create_handoff_request(
        self,
        tier1_result: Tier1LookupResult,
        requirement_envelope: PackagingRequirementEnvelope,
        package_geometry: PackageGeometry,
        active_objectives: List[str],
        eligible_candidate_materials: Union[List[PackagingCandidate], List[str]],
        store: Optional[BaseOptimizationStateStore] = None
    ) -> Tier2HandoffRequest:
        """
        Create a Tier-2 handoff request following a Tier-1 EXACT_MISS.
        Raises ValueError if tier1_result is EXACT_HIT.
        """
        if tier1_result.status == Tier1LookupStatus.EXACT_HIT:
            raise ValueError(
                "Tier-2 warm-start handoff is not permitted when Tier-1 exact lookup yields EXACT_HIT."
            )

        if tier1_result.status != Tier1LookupStatus.EXACT_MISS:
            raise ValueError(
                f"Invalid Tier-1 status for Tier-2 handoff: {tier1_result.status}"
            )

        # Build canonical representation for target identity
        target_canon = build_canonical_representation(
            requirement_envelope=requirement_envelope,
            package_geometry=package_geometry,
            active_objectives=active_objectives,
            eligible_candidate_materials=eligible_candidate_materials
        )

        # Preserve target candidate materials list
        candidates_list: List[PackagingCandidate] = []
        if eligible_candidate_materials and isinstance(eligible_candidate_materials[0], str):
            for cid in eligible_candidate_materials:
                candidates_list.append(
                    PackagingCandidate(
                        candidate_id=cid,  # type: ignore
                        material_spec=None,  # type: ignore
                        decision_variables=None  # type: ignore
                    )
                )
        else:
            candidates_list = list(eligible_candidate_materials)  # type: ignore

        # Expose available stored states unranked and unselected
        available_states: List[Any] = []
        if store is not None:
            available_states = store.list_all_states()

        return Tier2HandoffRequest(
            tier1_lookup_status=Tier1LookupStatus.EXACT_MISS,
            requirement_envelope=requirement_envelope.model_copy(deep=True),
            package_geometry=package_geometry.model_copy(deep=True),
            active_objectives=list(active_objectives),
            eligible_candidate_materials=[c.model_copy(deep=True) for c in candidates_list],
            target_canonical_representation=target_canon,
            available_stored_states=available_states,
            requires_target_reevaluation=True
        )


def create_tier2_handoff_request(
    tier1_result: Tier1LookupResult,
    requirement_envelope: PackagingRequirementEnvelope,
    package_geometry: PackageGeometry,
    active_objectives: List[str],
    eligible_candidate_materials: Union[List[PackagingCandidate], List[str]],
    store: Optional[BaseOptimizationStateStore] = None
) -> Tier2HandoffRequest:
    """Convenience function to create a Tier-2 warm-start handoff request."""
    engine = Tier2HandoffEngine()
    return engine.create_handoff_request(
        tier1_result=tier1_result,
        requirement_envelope=requirement_envelope,
        package_geometry=package_geometry,
        active_objectives=active_objectives,
        eligible_candidate_materials=eligible_candidate_materials,
        store=store
    )
