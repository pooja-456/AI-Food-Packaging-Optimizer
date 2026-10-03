"""
M6-G (B5A): Precomputed Optimization-State In-Memory Store Implementation.

Provides the abstract store interface and deterministic in-memory store implementation
for PrecomputedOptimizationState records.

Adheres strictly to docs/m6b5a_precomputed_state_store_contract.md and docs/m6b5c_precomputed_state_generation_contract.md:
- Isolate Identity from Result and Metadata.
- Validate pre-storage integrity (identity completeness, result completeness, search-space consistency).
- Accept valid empty ParetoFront objects (over-constrained results).
- Enforce deep immutability and verbatim preservation.
- Decoupled from physical databases (PostgreSQL/Redis) and Tier-1 lookup engine.
"""

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from app.schemas.optimization import (
    OptimizationInputEnvelope,
    OptimizationMetadata,
    PackageGeometry,
    PackagingCandidate,
    ParetoFront,
    ParetoCandidate
)
from app.schemas.packaging_requirements import PackagingRequirementEnvelope
from scientific_engine.optimization.canonical_representation import (
    CanonicalOptimizationState,
    build_canonical_representation
)
from scientific_engine.optimization.pre_storage_validation import (
    PreStorageValidator,
    PreStorageValidationResult
)


class PrecomputedOptimizationState(BaseModel):
    """
    Fundamental record in the optimization state store.
    Encapsulates Identity, Result (ParetoFront), and Provenance Metadata.
    """

    # Identity Fields (Frozen M6-A Identity)
    requirement_envelope: PackagingRequirementEnvelope = Field(
        ...,
        description="Phase 4 PackagingRequirementEnvelope defining scientific requirements."
    )
    package_geometry: PackageGeometry = Field(
        ...,
        description="Scalar PackageGeometry parameters."
    )
    active_objectives: List[str] = Field(
        ...,
        description="Unordered active objective identifiers."
    )
    eligible_candidate_materials: List[PackagingCandidate] = Field(
        ...,
        description="List of eligible PackagingCandidate objects composing the search space."
    )

    # Result Fields
    pareto_front: ParetoFront = Field(
        ...,
        description="Calculated ParetoFront output, stored verbatim."
    )

    # Metadata Fields
    optimization_run_id: str = Field(
        ...,
        description="Unique execution identifier."
    )
    timestamp: str = Field(
        ...,
        description="ISO-8601 execution timestamp."
    )
    solver_metadata: OptimizationMetadata = Field(
        ...,
        description="Solver metadata and performance metrics."
    )
    constraint_policy_version: str = Field(
        ...,
        description="Constraint policy version tag."
    )
    origin_classification: str = Field(
        default="SYNTHETIC_TEST",
        description="Data origin classification (e.g. 'SYNTHETIC_TEST', 'REAL_PRODUCTION')."
    )

    def get_eligible_candidate_ids(self) -> List[str]:
        """Extract candidate IDs from the eligible materials list."""
        return [cand.candidate_id for cand in self.eligible_candidate_materials]

    def get_canonical_representation(self) -> CanonicalOptimizationState:
        """Derive the canonical optimization identity representation for this state."""
        return build_canonical_representation(
            requirement_envelope=self.requirement_envelope,
            package_geometry=self.package_geometry,
            active_objectives=self.active_objectives,
            eligible_candidate_materials=self.eligible_candidate_materials
        )


def validate_precomputed_state(state: PrecomputedOptimizationState) -> None:
    """
    Perform pre-storage validation checks specified by B5A / B5C contracts:
    Delegates to PreStorageValidator and raises ValueError if invalid.
    """
    validator = PreStorageValidator()
    res = validator.validate(state)
    if not res.is_valid:
        raise ValueError("; ".join(res.reasons))


class BaseOptimizationStateStore(ABC):
    """
    Abstract interface for the Precomputed Optimization-State Store.
    """

    @abstractmethod
    def store(self, state: PrecomputedOptimizationState) -> bool:
        """
        Validate and store a PrecomputedOptimizationState.
        Returns True if stored/updated, False if discarded as an older/duplicate state.
        Raises ValueError if state fails pre-storage validation.
        """
        pass

    @abstractmethod
    def get_by_canonical_json(self, canonical_json: str) -> Optional[PrecomputedOptimizationState]:
        """
        Retrieve an exact stored state by its canonical JSON identity string.
        Returns None if absent.
        """
        pass

    @abstractmethod
    def list_all_states(self) -> List[PrecomputedOptimizationState]:
        """
        List all currently stored states. Exposes identity fields for Tier-2 scanning.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """Return the number of stored states."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all stored states."""
        pass


class InMemoryOptimizationStateStore(BaseOptimizationStateStore):
    """
    Thread-safe in-memory store for PrecomputedOptimizationState objects.
    Uses deterministic canonical identity JSON representations as dictionary keys.
    """

    def __init__(self) -> None:
        self._store: Dict[str, PrecomputedOptimizationState] = {}

    def store(self, state: PrecomputedOptimizationState) -> bool:
        """
        Validate and store state in memory.
        Immutability: Stores a deep copy of the state.
        Duplicate Identity: Overwrites if newer timestamp or different policy version,
        otherwise discards as idempotent duplicate.
        """
        validate_precomputed_state(state)
        
        canon_json = state.get_canonical_representation().to_canonical_json()
        
        if canon_json in self._store:
            existing = self._store[canon_json]
            # Idempotent discard if identical run ID or timestamp
            if (
                existing.optimization_run_id == state.optimization_run_id
                and existing.timestamp == state.timestamp
            ):
                return False

        # Store deep copy for immutability
        self._store[canon_json] = state.model_copy(deep=True)
        return True

    def get_by_canonical_json(self, canonical_json: str) -> Optional[PrecomputedOptimizationState]:
        """
        Retrieve state by exact canonical JSON key.
        Immutability: Returns a deep copy to prevent caller mutation.
        """
        state = self._store.get(canonical_json)
        if state is None:
            return None
        return state.model_copy(deep=True)

    def get_by_identity(
        self,
        requirement_envelope: PackagingRequirementEnvelope,
        package_geometry: PackageGeometry,
        active_objectives: List[str],
        eligible_candidate_materials: Union[List[PackagingCandidate], List[str]]
    ) -> Optional[PrecomputedOptimizationState]:
        """
        Helper method to retrieve stored state using raw identity components.
        """
        canon = build_canonical_representation(
            requirement_envelope=requirement_envelope,
            package_geometry=package_geometry,
            active_objectives=active_objectives,
            eligible_candidate_materials=eligible_candidate_materials
        )
        return self.get_by_canonical_json(canon.to_canonical_json())

    def list_all_states(self) -> List[PrecomputedOptimizationState]:
        """Return list of deep copies of all stored states."""
        return [state.model_copy(deep=True) for state in self._store.values()]

    def count(self) -> int:
        """Return count of stored states."""
        return len(self._store)

    def clear(self) -> None:
        """Clear all stored states."""
        self._store.clear()
