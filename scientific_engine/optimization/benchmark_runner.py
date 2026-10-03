"""
M7-E4: Algorithm-Neutral Benchmark Execution Runner.

Implements the 12-step algorithm-neutral benchmark execution lifecycle per M7-E3:
Scenario validation -> Isolated context init -> Adapter init -> Telemetry timer start ->
Step loop -> Evaluation boundary counting -> Pareto front structural validation -> Result recording.

Defaults strictly to cold-start execution. Zero Tier-1 cache reuse, zero Tier-2 warm-start.
"""

import uuid
import time
from typing import Dict, List, Optional

from app.schemas.optimization import (
    PackagingCandidate,
    ParetoCandidate,
    ParetoFront,
    CandidateScientificEvaluationRequest,
    EvidenceTier,
    UncertaintyProfile,
    UncertaintyType,
    ExplanationPayload,
)
from scientific_engine.optimization.benchmark_contracts import (
    BenchmarkScenario,
    BenchmarkAlgorithmConfig,
    BenchmarkRunResult,
    BenchmarkExecutionStatus,
    IOptimizerAdapter,
    RepeatabilityMetadata,
    REFERENCE_PARETO_FRONT_NOT_AUTHORIZED,
)
from scientific_engine.optimization.benchmark_metrics import (
    MonotonicTimerAuditor,
    FeasibleDiscoveryTracker,
    PeakRamAuditor,
    collect_reproducibility_metadata,
)
from scientific_engine.optimization.benchmark_validation import (
    validate_benchmark_scenario,
    validate_pareto_front_structure,
    ScenarioValidationError,
)
from scientific_engine.optimization.candidate_evaluator import CandidateScientificEvaluator
from scientific_engine.optimization.objective_evaluator import ObjectiveEvaluator
from scientific_engine.optimization.pareto_front import ParetoFrontConstructor


class BenchmarkEvaluationPipelineHarness:
    """
    Evaluation boundary wrapper. Enforces the frozen M6 pipeline:
    B2A Candidate Construction -> B2B Scientific Evaluation -> Phase 5 Hard Constraints -> M6-B3 Objectives.
    Audits exact scientific evaluation counts without double-counting.
    """

    def __init__(
        self,
        scenario: BenchmarkScenario,
        discovery_tracker: FeasibleDiscoveryTracker,
    ) -> None:
        self.scenario = scenario
        self.discovery_tracker = discovery_tracker
        self.evaluator = CandidateScientificEvaluator()
        self.objective_evaluator = ObjectiveEvaluator()
        self.scientific_evaluations_count: int = 0

    def evaluate_candidate(self, candidate: PackagingCandidate) -> ParetoCandidate:
        """
        Executes single scientific evaluation call through the project's scientific engine.
        Increments scientific_evaluations_count by exactly 1.
        """
        self.scientific_evaluations_count += 1

        # 1. B2B Scientific Evaluation & Phase 5 Hard Constraints
        eval_req = CandidateScientificEvaluationRequest(
            candidate=candidate,
            base_requirement_envelope=self.scenario.requirement_envelope,
            package_geometry=self.scenario.package_geometry,
        )
        eval_result = self.evaluator.evaluate_candidate(eval_req)

        # Audit feasible discovery
        is_feasible = (
            eval_result.constraint_profile is not None
            and eval_result.constraint_profile.all_hard_constraints_satisfied
        )
        self.discovery_tracker.record_candidate_evaluation(
            is_feasible=is_feasible,
            cumulative_evals=self.scientific_evaluations_count,
        )

        # 2. M6-B3 Objective Evaluation
        objectives = self.objective_evaluator.evaluate_objectives(
            candidate=candidate,
            scientific_result=eval_result,
        )
        if self.scenario.active_objectives:
            objectives = {k: v for k, v in objectives.items() if k in self.scenario.active_objectives}

        evidence_tier = EvidenceTier.TIER_1_EMPIRICAL
        if candidate.provenance and candidate.provenance.evidence_classification == "MODEL_PREDICTED":
            evidence_tier = EvidenceTier.TIER_2_PREDICTIVE_QSAR

        uncertainty_profile = eval_result.uncertainty_profile or UncertaintyProfile(
            uncertainty_type=UncertaintyType.DETERMINISTIC_POINT
        )

        explanation = ExplanationPayload(
            trade_off_summary="Benchmark evaluation pipeline candidate result.",
            limiting_barrier="WVTR" if candidate.barrier_properties.wvtr else "UNKNOWN",
            primary_strength="Empirical evidence baseline",
        )

        pareto_candidate = ParetoCandidate(
            pareto_candidate_id=candidate.candidate_id,
            candidate_design=candidate,
            objective_values=objectives,
            constraint_compliance_summary=eval_result.constraint_profile,
            uncertainty_profile=uncertainty_profile,
            evidence_tier=evidence_tier,
            traceability=eval_result.traceability,
            explanation_payload=explanation,
        )

        return pareto_candidate


class BenchmarkRunner:
    """
    Algorithm-neutral benchmark runner executing isolated cold-start runs.
    """

    def __init__(self) -> None:
        pass

    def run_benchmark(
        self,
        scenario: BenchmarkScenario,
        eligible_candidates: List[PackagingCandidate],
        adapter: IOptimizerAdapter,
        config: BenchmarkAlgorithmConfig,
    ) -> BenchmarkRunResult:
        """
        Executes a single benchmark run across the 12-step lifecycle.
        """
        run_id = str(uuid.uuid4())

        # Step 1: Scenario Identity Validation & Canonical Representation
        try:
            canonical_identity = validate_benchmark_scenario(scenario)
        except ScenarioValidationError as e:
            repro_meta = collect_reproducibility_metadata(config.random_seed)
            return BenchmarkRunResult(
                run_id=run_id,
                scenario_id=scenario.scenario_id,
                canonical_identity="INVALID_SCENARIO_IDENTITY",
                algorithm_id=config.algorithm_id,
                configuration_name=config.configuration_name,
                random_seed=config.random_seed,
                execution_status=BenchmarkExecutionStatus.INVALID_RESULT,
                error_message=f"Scenario validation failed: {str(e)}",
                repeatability=RepeatabilityMetadata(
                    run_id=run_id,
                    scenario_id=scenario.scenario_id,
                    algorithm_id=config.algorithm_id,
                    configuration_name=config.configuration_name,
                    random_seed=config.random_seed,
                ),
                reproducibility=repro_meta,
            )

        # Map eligible candidates by candidate_id for fast lookup & validation
        eligible_map: Dict[str, PackagingCandidate] = {
            c.candidate_id: c for c in eligible_candidates
        }

        # Step 2: Initialize Isolated Telemetry Context & Auditors
        timer = MonotonicTimerAuditor()
        discovery_tracker = FeasibleDiscoveryTracker(timer)
        ram_auditor = PeakRamAuditor()
        pipeline_harness = BenchmarkEvaluationPipelineHarness(scenario, discovery_tracker)

        ram_auditor.start()
        timer.start()

        # Step 3: Initialize Adapter & Reset Solver State
        try:
            adapter.initialize(
                scenario=scenario,
                eligible_candidates=eligible_candidates,
                config=config,
            )
        except Exception as e:
            timer.stop()
            peak_ram, ram_status = ram_auditor.get_peak_ram()
            ram_auditor.stop()
            repro_meta = collect_reproducibility_metadata(config.random_seed)
            return BenchmarkRunResult(
                run_id=run_id,
                scenario_id=scenario.scenario_id,
                canonical_identity=canonical_identity,
                algorithm_id=config.algorithm_id,
                configuration_name=config.configuration_name,
                random_seed=config.random_seed,
                execution_status=BenchmarkExecutionStatus.INFRASTRUCTURE_FAILURE,
                error_message=f"Adapter initialization failed: {str(e)}",
                repeatability=RepeatabilityMetadata(
                    run_id=run_id,
                    scenario_id=scenario.scenario_id,
                    algorithm_id=config.algorithm_id,
                    configuration_name=config.configuration_name,
                    random_seed=config.random_seed,
                ),
                reproducibility=repro_meta,
                peak_ram_bytes=peak_ram,
                peak_ram_status=ram_status,
            )

        # Step 4–7: Execute Step Loop until Adapter Termination
        solver_failed = False
        error_msg = None

        try:
            while not adapter.is_terminated():
                adapter.step()
        except Exception as e:
            solver_failed = True
            error_msg = f"Solver execution crashed: {str(e)}"

        wall_clock_ns = timer.stop()
        peak_ram, ram_status = ram_auditor.get_peak_ram()
        ram_auditor.stop()

        repro_meta = collect_reproducibility_metadata(config.random_seed)
        repeat_meta = RepeatabilityMetadata(
            run_id=run_id,
            scenario_id=scenario.scenario_id,
            algorithm_id=config.algorithm_id,
            configuration_name=config.configuration_name,
            random_seed=config.random_seed,
        )

        evals_count = adapter.get_evaluations_count()
        if hasattr(adapter, "discovery_tracker") and adapter.discovery_tracker is not None:
            feasible_rec = adapter.discovery_tracker.get_record()
        else:
            feasible_rec = discovery_tracker.get_record()

        if solver_failed:
            return BenchmarkRunResult(
                run_id=run_id,
                scenario_id=scenario.scenario_id,
                canonical_identity=canonical_identity,
                algorithm_id=config.algorithm_id,
                configuration_name=config.configuration_name,
                random_seed=config.random_seed,
                execution_status=BenchmarkExecutionStatus.FAILED,
                scientific_evaluations_count=evals_count,
                wall_clock_ns=wall_clock_ns,
                feasible_discovery=feasible_rec,
                repeatability=repeat_meta,
                reproducibility=repro_meta,
                peak_ram_bytes=peak_ram,
                peak_ram_status=ram_status,
                error_message=error_msg,
            )

        # Step 8–9: Retrieve Raw Pareto Front & Validate Front Structure
        raw_front = adapter.get_current_pareto_front()
        val_result = validate_pareto_front_structure(
            pareto_front=raw_front,
            scenario=scenario,
            eligible_candidates_map=eligible_map,
        )

        if not val_result.is_valid:
            return BenchmarkRunResult(
                run_id=run_id,
                scenario_id=scenario.scenario_id,
                canonical_identity=canonical_identity,
                algorithm_id=config.algorithm_id,
                configuration_name=config.configuration_name,
                random_seed=config.random_seed,
                execution_status=BenchmarkExecutionStatus.INVALID_RESULT,
                scientific_evaluations_count=evals_count,
                wall_clock_ns=wall_clock_ns,
                feasible_discovery=feasible_rec,
                repeatability=repeat_meta,
                reproducibility=repro_meta,
                peak_ram_bytes=peak_ram,
                peak_ram_status=ram_status,
                pareto_front=raw_front,
                error_message=f"Pareto front structural validation failed: {'; '.join(val_result.errors)}",
            )

        # Step 10–12: Assign Final Status & Construct Result Record
        if not feasible_rec.first_feasible_found and (raw_front is None or len(raw_front.candidates) == 0):
            status = BenchmarkExecutionStatus.NO_FEASIBLE_SOLUTION
        else:
            status = BenchmarkExecutionStatus.COMPLETED

        return BenchmarkRunResult(
            run_id=run_id,
            scenario_id=scenario.scenario_id,
            canonical_identity=canonical_identity,
            algorithm_id=config.algorithm_id,
            configuration_name=config.configuration_name,
            random_seed=config.random_seed,
            execution_status=status,
            scientific_evaluations_count=evals_count,
            wall_clock_ns=wall_clock_ns,
            feasible_discovery=feasible_rec,
            pareto_coverage_status=REFERENCE_PARETO_FRONT_NOT_AUTHORIZED,
            repeatability=repeat_meta,
            reproducibility=repro_meta,
            peak_ram_bytes=peak_ram,
            peak_ram_status=ram_status,
            robustness_status=status.value,
            pareto_front=raw_front,
        )
