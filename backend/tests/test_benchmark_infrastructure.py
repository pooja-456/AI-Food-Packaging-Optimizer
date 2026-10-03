"""
M7-E4: Benchmark Infrastructure & Execution Harness Tests.

Focus unit and integration tests for scenario validation, objective contracts, adapter lifecycle,
run initialization, evaluation counting, first-feasible discovery, NO_FEASIBLE_SOLUTION,
wall-clock measurement, peak RAM auditing, run isolation, failure handling, Pareto structural validation,
UNKNOWN != FEASIBLE, interval preservation, reproducibility metadata, and algorithm neutrality.

IMPORTANT: All fake adapters in this file are labeled SYNTHETIC_TEST and used ONLY to test harness code.
They are NOT scientific evidence, NOT optimizer implementations, and NOT reported as empirical results.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple

from app.schemas.packaging_request import PackagingRequest
from app.schemas.physics import CalculationStatus, ScientificTraceability
from app.schemas.constraints import ConstraintStatus, ConditionMatchLevel
from app.schemas.optimization import (
    PackagingCandidate,
    PackageGeometry,
    CandidateDecisionVariables,
    CandidateBarrierProperties,
    BarrierPropertyMetric,
    CandidateEvidenceReference,
    ObjectiveValue,
    ObjectiveDirection,
    ParetoCandidate,
    ParetoFront,
    OptimizationMetadata,
    CandidateConstraintStatus,
    UncertaintyProfile,
    UncertaintyType,
    ExplanationPayload,
)
from scientific_engine.inference.engine import infer_commodity_properties
from scientific_engine.physics.requirements import PackagingRequirementEngine
from scientific_engine.optimization.benchmark_contracts import (
    BenchmarkScenario,
    BenchmarkAlgorithmConfig,
    BenchmarkExecutionStatus,
    IOptimizerAdapter,
    AUTHORITATIVE_OBJECTIVES,
    NOT_YET_AUTHORIZED,
    REFERENCE_PARETO_FRONT_NOT_AUTHORIZED,
    REPEATED_RUN_COUNT_NOT_YET_AUTHORIZED,
)
from scientific_engine.optimization.benchmark_validation import (
    validate_benchmark_scenario,
    validate_pareto_front_structure,
    ScenarioValidationError,
)
from scientific_engine.optimization.benchmark_metrics import (
    MonotonicTimerAuditor,
    FeasibleDiscoveryTracker,
    PeakRamAuditor,
    collect_reproducibility_metadata,
)
from scientific_engine.optimization.benchmark_runner import (
    BenchmarkRunner,
    BenchmarkEvaluationPipelineHarness,
)


# ---------------------------------------------------------------------------
# Synthetic Test Adapters (Labeled SYNTHETIC_TEST - Test Infrastructure Only)
# ---------------------------------------------------------------------------

class SyntheticDummyOptimizerAdapter(IOptimizerAdapter):
    """
    SYNTHETIC_TEST adapter simulating a candidate optimizer for harness testing.
    Does NOT implement an actual optimization algorithm.
    """

    def __init__(self, simulate_crash: bool = False, return_invalid_candidate: bool = False) -> None:
        self.simulate_crash = simulate_crash
        self.return_invalid_candidate = return_invalid_candidate
        self.scenario: Optional[BenchmarkScenario] = None
        self.candidates: List[PackagingCandidate] = []
        self.config: Optional[BenchmarkAlgorithmConfig] = None
        self.current_step: int = 0
        self.evaluations_count: int = 0
        self.evaluated_pareto_candidates: List[ParetoCandidate] = []
        self.harness: Optional[BenchmarkEvaluationPipelineHarness] = None
        self.timer = MonotonicTimerAuditor()
        self.discovery_tracker = FeasibleDiscoveryTracker(self.timer)

    def initialize(
        self,
        scenario: BenchmarkScenario,
        eligible_candidates: List[PackagingCandidate],
        config: BenchmarkAlgorithmConfig,
    ) -> None:
        if self.simulate_crash and config.parameters.get("crash_at_init"):
            raise RuntimeError("SYNTHETIC_TEST: Simulated crash during initialize().")

        self.scenario = scenario
        self.candidates = eligible_candidates
        self.config = config
        self.current_step = 0
        self.evaluations_count = 0
        self.evaluated_pareto_candidates = []
        self.harness = BenchmarkEvaluationPipelineHarness(scenario, self.discovery_tracker)

    def step(self) -> Dict[str, Any]:
        if self.simulate_crash and self.current_step == 1:
            raise RuntimeError("SYNTHETIC_TEST: Simulated crash during step().")

        if self.current_step < len(self.candidates):
            cand = self.candidates[self.current_step]
            pareto_cand = self.harness.evaluate_candidate(cand)
            self.evaluations_count = self.harness.scientific_evaluations_count
            self.evaluated_pareto_candidates.append(pareto_cand)

        self.current_step += 1
        return {"step": self.current_step, "evaluations": self.evaluations_count}

    def get_current_pareto_front(self) -> ParetoFront:
        from scientific_engine.optimization.pareto_front import ParetoFrontConstructor

        if self.return_invalid_candidate:
            # Construct invalid candidate with candidate_id not in eligible set
            invalid_cand = PackagingCandidate(
                candidate_id="INVALID_FAKE_ID_999",
                material_id="MAT-FAKE",
                material_name="Fake Material",
                decision_variables=CandidateDecisionVariables(
                    total_thickness_um=50.0, thickness_source="test"
                ),
                barrier_properties=CandidateBarrierProperties(),
                condition_match=ConditionMatchLevel.EXACT,
                provenance=CandidateEvidenceReference(
                    source_id="s1", source_name="sn", record_identifier_in_source="r1",
                    evidence_classification="TEST", verification_status="VERIFIED"
                )
            )
            fake_pareto = ParetoCandidate(
                pareto_candidate_id="INVALID_FAKE_ID_999",
                candidate_design=invalid_cand,
                objective_values={},
                constraint_compliance_summary=CandidateConstraintStatus(
                    all_hard_constraints_satisfied=True,
                    evaluations=[],
                    overall_status=ConstraintStatus.FEASIBLE,
                    condition_match=ConditionMatchLevel.EXACT,
                ),
                uncertainty_profile=UncertaintyProfile(uncertainty_type=UncertaintyType.DETERMINISTIC_POINT),
                evidence_tier=self.evaluated_pareto_candidates[0].evidence_tier if self.evaluated_pareto_candidates else "TIER_1_EMPIRICAL",
                traceability=ScientificTraceability(model_name="test", equation_form="test"),
                explanation_payload=ExplanationPayload(trade_off_summary="", limiting_barrier="", primary_strength="")
            )
            return ParetoFront(
                optimization_run_id="run_test",
                timestamp="2026-09-30T21:00:00Z",
                candidate_count=1,
                candidates=[fake_pareto],
                solver_metadata=OptimizationMetadata(
                    algorithm_name=self.config.algorithm_id if self.config else "SYNTHETIC_TEST",
                    iterations_completed=self.current_step,
                    execution_time_ms=1.0,
                    cache_hit=False,
                ),
                constraint_policy_version="1.0",
            )

        constructor = ParetoFrontConstructor(run_id="run_test")
        return constructor.construct_front(self.evaluated_pareto_candidates)

    def is_terminated(self) -> bool:
        return self.current_step >= max(1, len(self.candidates))

    def get_evaluations_count(self) -> int:
        return self.evaluations_count


# ---------------------------------------------------------------------------
# Test Fixture Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_benchmark_scenario() -> Tuple[BenchmarkScenario, List[PackagingCandidate]]:
    from app.schemas.physics import ScientificResult
    from scientific_engine.physics.traceability import make_traceability

    req = PackagingRequest(
        commodity="crackers",
        product_form="whole",
        ripeness_stage="dry",
        target_shelf_life_days=60,
        storage_type="ambient",
        storage_temperature_c=25.0,
        relative_humidity_percent=70.0,
        moisture_percent=3.0,
    )
    inference_profile = infer_commodity_properties(req)
    engine = PackagingRequirementEngine()
    envelope = engine.evaluate_requirements(
        request=req,
        inference_profile=inference_profile,
        dry_mass_g=200.0,
        critical_moisture_percent=6.0,
        package_area_m2=0.05,
    )

    trace = make_traceability(model_name="BenchmarkFixture", equation_form="fixture_setup")
    envelope.gas_requirements.status = CalculationStatus.CALCULATED
    envelope.gas_requirements.required_otr_per_area = ScientificResult(
        status=CalculationStatus.CALCULATED,
        value=100.0,
        unit="cc/(m2.day.atm)",
        minimum_value=100.0,
        maximum_value=100.0,
        traceability=trace,
    )
    envelope.gas_requirements.required_co2tr_per_area = ScientificResult(
        status=CalculationStatus.CALCULATED,
        value=100.0,
        unit="cc/(m2.day.atm)",
        minimum_value=100.0,
        maximum_value=100.0,
        traceability=trace,
    )

    geometry = PackageGeometry(
        surface_area_m2=0.05,
        headspace_volume_cm3=100.0,
        product_mass_kg=0.2,
    )

    cand1 = PackagingCandidate(
        candidate_id="MAT-1-50UM",
        material_id="MAT-1",
        material_name="LDPE Monolayer Film 50um",
        decision_variables=CandidateDecisionVariables(
            structure_type="MONOLAYER",
            layer_sequence=["LDPE"],
            total_thickness_um=50.0,
            thickness_source="observed_discrete_m5",
        ),
        barrier_properties=CandidateBarrierProperties(
            wvtr=BarrierPropertyMetric(
                value=0.5,
                unit="g/(m2.day)",
                value_min=0.4,
                value_max=0.6,
                is_range=True,
                test_temperature_c=25.0,
                test_rh_percent=70.0,
            ),
            otr=BarrierPropertyMetric(
                value=3500.0,
                unit="cc/(m2.day.atm)",
                test_temperature_c=25.0,
                test_rh_percent=70.0,
            ),
            co2tr=BarrierPropertyMetric(
                value=3500.0,
                unit="cc/(m2.day.atm)",
                test_temperature_c=25.0,
                test_rh_percent=70.0,
            ),
        ),
        condition_match=ConditionMatchLevel.EXACT,
        provenance=CandidateEvidenceReference(
            source_id="SRC-1",
            source_name="Polymer Permeability Handbook",
            record_identifier_in_source="REC-1",
            evidence_classification="EXPERIMENTAL_LITERATURE_DATA",
            verification_status="VERIFIED",
        ),
    )

    scenario = BenchmarkScenario(
        scenario_id="SCEN-TEST-001",
        requirement_envelope=envelope,
        package_geometry=geometry,
        active_objectives=list(AUTHORITATIVE_OBJECTIVES),
        eligible_candidate_ids=["MAT-1-50UM"],
    )

    return scenario, [cand1]



# ---------------------------------------------------------------------------
# Test Cases (A through T)
# ---------------------------------------------------------------------------

def test_A_scenario_validation_valid(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, _ = sample_benchmark_scenario
    canonical_identity = validate_benchmark_scenario(scenario)
    assert canonical_identity is not None
    assert "requirement_envelope" in canonical_identity
    assert "package_geometry" in canonical_identity
    assert "active_objectives" in canonical_identity
    assert "eligible_candidate_ids" in canonical_identity
    assert scenario.canonical_identity == canonical_identity


def test_B_objective_contract_validation(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, _ = sample_benchmark_scenario
    scenario.active_objectives = ["cost_usd_per_m2"]  # Unauthorized objective
    with pytest.raises(ScenarioValidationError, match="Unauthorized objective"):
        validate_benchmark_scenario(scenario)


def test_C_adapter_lifecycle(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    adapter = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")

    adapter.initialize(scenario, candidates, config)
    assert adapter.get_evaluations_count() == 0
    assert not adapter.is_terminated()

    res = adapter.step()
    assert res["step"] == 1
    assert adapter.get_evaluations_count() == 1
    assert adapter.is_terminated()


def test_D_run_initialization(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    runner = BenchmarkRunner()
    adapter = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg", random_seed=42)

    result = runner.run_benchmark(scenario, candidates, adapter, config)
    assert result.scenario_id == "SCEN-TEST-001"
    assert result.algorithm_id == "SYNTHETIC_DUMMY"
    assert result.random_seed == 42


def test_E_evaluation_counting(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    runner = BenchmarkRunner()
    adapter = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")

    result = runner.run_benchmark(scenario, candidates, adapter, config)
    assert result.scientific_evaluations_count == 1


def test_F_first_feasible_discovery(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    runner = BenchmarkRunner()
    adapter = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")

    result = runner.run_benchmark(scenario, candidates, adapter, config)
    rec = result.feasible_discovery
    assert rec.first_feasible_found is True
    assert rec.evaluations_to_first_feasible == 1
    assert rec.wall_clock_ns_to_first_feasible is not None
    assert rec.wall_clock_ns_to_first_feasible >= 0


def test_G_no_feasible_solution_handling(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    # Modify candidate WVTR so it violates required WVTR (e.g. 500.0 g/(m2.day) > 100.0 required)
    candidates[0].barrier_properties.wvtr.value = 500.0
    candidates[0].barrier_properties.wvtr.value_min = 400.0
    candidates[0].barrier_properties.wvtr.value_max = 600.0

    runner = BenchmarkRunner()
    adapter = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")

    result = runner.run_benchmark(scenario, candidates, adapter, config)
    assert result.execution_status in [BenchmarkExecutionStatus.COMPLETED, BenchmarkExecutionStatus.NO_FEASIBLE_SOLUTION]
    assert result.feasible_discovery.first_feasible_found is False


def test_H_wall_clock_measurement(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    runner = BenchmarkRunner()
    adapter = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")

    result = runner.run_benchmark(scenario, candidates, adapter, config)
    assert result.wall_clock_ns > 0


def test_I_peak_ram_behavior() -> None:
    auditor = PeakRamAuditor()
    auditor.start()
    ram, status = auditor.get_peak_ram()
    auditor.stop()
    assert status in ["MEASURED_TRACEMALLOC", "NOT_AVAILABLE"]


def test_J_run_isolation(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    runner = BenchmarkRunner()
    adapter1 = SyntheticDummyOptimizerAdapter()
    adapter2 = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")

    res1 = runner.run_benchmark(scenario, candidates, adapter1, config)
    res2 = runner.run_benchmark(scenario, candidates, adapter2, config)

    assert res1.run_id != res2.run_id
    assert res1.scientific_evaluations_count == res2.scientific_evaluations_count


def test_K_failure_status_handling(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    runner = BenchmarkRunner()
    adapter = SyntheticDummyOptimizerAdapter(simulate_crash=True)
    config = BenchmarkAlgorithmConfig(
        algorithm_id="SYNTHETIC_DUMMY",
        configuration_name="test_cfg",
        parameters={"crash_at_init": True},
    )

    result = runner.run_benchmark(scenario, candidates, adapter, config)
    assert result.execution_status == BenchmarkExecutionStatus.INFRASTRUCTURE_FAILURE
    assert "Adapter initialization failed" in result.error_message


def test_L_invalid_optimizer_output_handling(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    runner = BenchmarkRunner()
    adapter = SyntheticDummyOptimizerAdapter(return_invalid_candidate=True)
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")

    result = runner.run_benchmark(scenario, candidates, adapter, config)
    assert result.execution_status == BenchmarkExecutionStatus.INVALID_RESULT
    assert "Pareto front structural validation failed" in result.error_message


def test_M_pareto_front_structural_validation(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    adapter = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")
    adapter.initialize(scenario, candidates, config)
    adapter.step()

    front = adapter.get_current_pareto_front()
    cand_map = {c.candidate_id: c for c in candidates}
    val_res = validate_pareto_front_structure(front, scenario, cand_map)
    assert val_res.is_valid is True
    assert len(val_res.errors) == 0


def test_N_unknown_not_feasible_assertion(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    adapter = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")
    adapter.initialize(scenario, candidates, config)
    adapter.step()

    front = adapter.get_current_pareto_front()
    cand_map = {c.candidate_id: c for c in candidates}

    # Inject UNKNOWN objective status into front candidate
    front.candidates[0].objective_values["f_thickness"].status = CalculationStatus.UNKNOWN
    val_res = validate_pareto_front_structure(front, scenario, cand_map)
    assert val_res.is_valid is False
    assert any("UNKNOWN" in err for err in val_res.errors)


def test_O_interval_preservation(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    adapter = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")
    adapter.initialize(scenario, candidates, config)
    adapter.step()

    cand = adapter.evaluated_pareto_candidates[0]
    f_moisture = cand.objective_values["f_moisture_margin"]
    assert f_moisture.is_interval is True
    assert f_moisture.value_min is not None
    assert f_moisture.value_max is not None


def test_P_candidate_membership_validation(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    adapter = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")
    adapter.initialize(scenario, candidates, config)
    adapter.step()

    front = adapter.get_current_pareto_front()
    # Validate against empty candidates map
    val_res = validate_pareto_front_structure(front, scenario, {})
    assert val_res.is_valid is False
    assert any("does not belong" in err for err in val_res.errors)


def test_Q_synthetic_adapter_execution(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    runner = BenchmarkRunner()
    adapter = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")

    result = runner.run_benchmark(scenario, candidates, adapter, config)
    assert result.execution_status in [BenchmarkExecutionStatus.COMPLETED, BenchmarkExecutionStatus.NO_FEASIBLE_SOLUTION]


def test_R_reproducibility_metadata() -> None:
    meta = collect_reproducibility_metadata(random_seed=123)
    assert meta.random_seed == 123
    assert meta.python_version is not None
    assert meta.git_commit_hash is not None
    assert meta.execution_timestamp_utc is not None


def test_S_no_reference_pareto_front_calculation(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    runner = BenchmarkRunner()
    adapter = SyntheticDummyOptimizerAdapter()
    config = BenchmarkAlgorithmConfig(algorithm_id="SYNTHETIC_DUMMY", configuration_name="test_cfg")

    result = runner.run_benchmark(scenario, candidates, adapter, config)
    assert result.pareto_coverage_status == REFERENCE_PARETO_FRONT_NOT_AUTHORIZED


def test_T_no_algorithm_specific_coupling(sample_benchmark_scenario: Tuple[BenchmarkScenario, List[PackagingCandidate]]) -> None:
    scenario, candidates = sample_benchmark_scenario
    # Ensure runner works with any IOptimizerAdapter instance without inspecting concrete class type
    runner = BenchmarkRunner()
    adapter = SyntheticDummyOptimizerAdapter()
    assert isinstance(adapter, IOptimizerAdapter)
    config = BenchmarkAlgorithmConfig(algorithm_id="ANY_GENERIC_ALGORITHM", configuration_name="generic")

    result = runner.run_benchmark(scenario, candidates, adapter, config)
    assert result.algorithm_id == "ANY_GENERIC_ALGORITHM"
