"""
M7-E4: Benchmark Infrastructure Contracts & Data Models.

Defines the algorithm-neutral data models, scenario structures, execution status enums,
reproducibility metadata, and abstract solver adapter interface per M7-E3.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.optimization import (
    PackagingCandidate,
    PackageGeometry,
    ParetoFront,
    ObjectiveDirection,
)
from app.schemas.packaging_requirements import PackagingRequirementEnvelope

# Policy status strings for unauthorized items
NOT_YET_AUTHORIZED = "NOT_YET_AUTHORIZED"
REFERENCE_PARETO_FRONT_NOT_AUTHORIZED = "REFERENCE_PARETO_FRONT_NOT_AUTHORIZED"
REPEATED_RUN_COUNT_NOT_YET_AUTHORIZED = "REPEATED_RUN_COUNT_NOT_YET_AUTHORIZED"

# Authoritative M6-B3 Objective Contract Definitions
AUTHORITATIVE_OBJECTIVES: List[str] = [
    "f_thickness",
    "f_moisture_margin",
    "f_gas_alignment",
    "f_shelf_life_margin",
]

OBJECTIVE_DIRECTIONS: Dict[str, ObjectiveDirection] = {
    "f_thickness": ObjectiveDirection.MINIMIZE,
    "f_moisture_margin": ObjectiveDirection.MAXIMIZE,
    "f_gas_alignment": ObjectiveDirection.MINIMIZE,
    "f_shelf_life_margin": ObjectiveDirection.MAXIMIZE,
}


class BenchmarkExecutionStatus(str, Enum):
    """Execution status classification for a benchmark run."""
    COMPLETED = "COMPLETED"
    NO_FEASIBLE_SOLUTION = "NO_FEASIBLE_SOLUTION"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    INVALID_RESULT = "INVALID_RESULT"
    MEMORY_LIMIT_FAILURE = "MEMORY_LIMIT_FAILURE"
    INFRASTRUCTURE_FAILURE = "INFRASTRUCTURE_FAILURE"


class BenchmarkAlgorithmConfig(BaseModel):
    """Generic configuration for a candidate optimization algorithm."""
    algorithm_id: str
    configuration_name: str
    random_seed: Optional[int] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class BenchmarkScenario(BaseModel):
    """
    Typed benchmark scenario representation matching the frozen M6-A 4-part identity:
    Envelope + Geometry + Active Objectives + Eligible Candidate IDs.
    """
    scenario_id: str
    requirement_envelope: PackagingRequirementEnvelope
    package_geometry: PackageGeometry
    active_objectives: List[str]
    eligible_candidate_ids: List[str]
    scenario_origin: str = "REAL_SCIENTIFIC_STATE"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    canonical_identity: Optional[str] = None


class FeasibleDiscoveryRecord(BaseModel):
    """Instrumentation tracking discovery of the first Phase 5 FEASIBLE solution."""
    first_feasible_found: bool = False
    evaluations_to_first_feasible: Optional[int] = None
    wall_clock_ns_to_first_feasible: Optional[int] = None


class RepeatabilityMetadata(BaseModel):
    """Repeatability tracking schema for stochastic run comparison."""
    run_id: str
    scenario_id: str
    algorithm_id: str
    configuration_name: str
    random_seed: Optional[int] = None
    repeated_run_count_policy: str = REPEATED_RUN_COUNT_NOT_YET_AUTHORIZED


class ReproducibilityMetadata(BaseModel):
    """Scientific provenance & environment metadata for 100% run reproducibility."""
    git_commit_hash: str
    python_version: str
    platform_system: str
    execution_timestamp_utc: str
    random_seed: Optional[int] = None
    dependency_versions: Dict[str, str] = Field(default_factory=dict)


class BenchmarkRunResult(BaseModel):
    """Complete algorithm-neutral benchmark run record."""
    run_id: str
    scenario_id: str
    canonical_identity: str
    algorithm_id: str
    configuration_name: str
    random_seed: Optional[int] = None
    execution_status: BenchmarkExecutionStatus
    scientific_evaluations_count: int = 0
    wall_clock_ns: int = 0
    feasible_discovery: FeasibleDiscoveryRecord = Field(default_factory=FeasibleDiscoveryRecord)
    pareto_coverage_status: str = REFERENCE_PARETO_FRONT_NOT_AUTHORIZED
    repeatability: RepeatabilityMetadata
    reproducibility: ReproducibilityMetadata
    peak_ram_bytes: Optional[int] = None
    peak_ram_status: str = "NOT_AVAILABLE"
    robustness_status: str = "COMPLETED"
    pareto_front: Optional[ParetoFront] = None
    error_message: Optional[str] = None


class IOptimizerAdapter(ABC):
    """
    Abstract, algorithm-neutral adapter interface for candidate optimizer algorithms per M7-E3.
    """

    @abstractmethod
    def initialize(
        self,
        scenario: BenchmarkScenario,
        eligible_candidates: List[PackagingCandidate],
        config: BenchmarkAlgorithmConfig,
    ) -> None:
        """Initialize solver state, search space, and random seed."""
        pass

    @abstractmethod
    def step(self) -> Dict[str, Any]:
        """Execute one iteration / generation step of the solver."""
        pass

    @abstractmethod
    def get_current_pareto_front(self) -> ParetoFront:
        """Retrieve the current non-dominated Pareto front discovered by the solver."""
        pass

    @abstractmethod
    def is_terminated(self) -> bool:
        """Check if solver has reached its internal stopping condition."""
        pass

    @abstractmethod
    def get_evaluations_count(self) -> int:
        """Return cumulative count of scientific evaluations performed by solver."""
        pass
