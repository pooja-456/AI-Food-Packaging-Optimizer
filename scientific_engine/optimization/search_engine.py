"""
M9/M10/M11: Inverse-Design Search Engine Layer with Explainability & Counterfactual Integration.

Defines the algorithm-neutral search interface, the deterministic candidate
enumeration baseline engine (M9), the intelligent adaptive inverse-design search engine (M10),
and integrated explainability report generation (M11).

Pipeline flow:
Candidate Construction / OptimizationInputEnvelope
        ↓
Adaptive / Deterministic Candidate Proposal
        ↓
Candidate Scientific Evaluation (Phase 4 recalculation)
        ↓
Phase 5 Hard Constraints Filtering
        ↓
M6-B3 Objective Evaluation (4 objectives: f_thickness, f_moisture_margin, f_gas_alignment, f_shelf_life_margin)
        ↓
M6-B4A Pareto Dominance (exact pairwise dominates primitive)
        ↓
M6-B4B Pareto Front Construction
        ↓
M11 Deterministic Explainability & Counterfactual Threshold Analysis

Strict Governance & Scientific Guarantees:
- Replaceable search interface: surrounding pipeline depends on AbstractInverseDesignSearchEngine.
- Baseline mechanism: Deterministic candidate enumeration baseline (M9).
- Intelligent mechanism: Adaptive candidate selection driven by evaluation feedback (M10).
- Explainability layer: Deterministic constraint, objective, provenance, and counterfactual threshold reports (M11).
- NO optimizer algorithm selection: NSGA-II, MOEA/D, Bayesian/surrogate approaches remain unauthorized.
- NO scalar ranking or arbitrary weighted scores.
- NO UNKNOWN -> FEASIBLE or numeric penalty conversions.
- NO missing/invented objective dimensions (cost, LCA, carbon).
"""

import time
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Set
from pydantic import BaseModel, Field

from app.schemas.optimization import (
    OptimizationInputEnvelope,
    PackagingCandidate,
    ParetoCandidate,
    ParetoFront,
    CandidateScientificEvaluationRequest,
    OptimizationMetadata,
    EvidenceTier,
    ExplanationPayload,
)
from app.schemas.constraints import ConstraintStatus
from app.schemas.physics import ScientificTraceability
from backend.app.schemas.recommendation import CandidateEvaluationSummary
from backend.app.schemas.explainability import PipelineExplainabilitySummary
from scientific_engine.optimization.candidate_evaluator import CandidateScientificEvaluator, CandidateScientificEvaluationResult
from scientific_engine.optimization.objective_evaluator import ObjectiveEvaluator
from scientific_engine.optimization.pareto_front import ParetoFrontConstructor
from scientific_engine.optimization.explainability_engine import ExplainabilityEngine


class InverseDesignSearchResult(BaseModel):
    """
    Structured search execution result encapsulating Pareto front, candidate evaluation summaries,
    execution metrics, scientific traceability, and M11 explainability summary.
    """
    optimization_run_id: str = Field(..., description="Unique optimization run ID")
    algorithm_name: str = Field(..., description="Name of the search algorithm/mechanism used")
    pareto_front: ParetoFront = Field(..., description="Exact non-dominated Pareto front of FEASIBLE candidates")
    candidate_summaries: List[CandidateEvaluationSummary] = Field(
        default_factory=list,
        description="Detailed evaluation summaries for all considered candidates"
    )
    total_candidates_considered: int = Field(..., description="Total candidate designs generated/proposed in search space")
    total_candidates_evaluated: int = Field(..., description="Total candidates that underwent scientific evaluation")
    feasible_candidates_count: int = Field(..., description="Number of candidates satisfying all Phase 5 hard constraints")
    infeasible_candidates_count: int = Field(..., description="Number of candidates violating at least one hard constraint")
    unknown_candidates_count: int = Field(..., description="Number of candidates with indeterminate feasibility status")
    execution_time_ms: float = Field(..., description="Total search execution time in milliseconds")
    all_warnings: List[str] = Field(default_factory=list, description="Aggregated warnings encountered during search")
    traceability_log: List[ScientificTraceability] = Field(
        default_factory=list,
        description="Scientific equation and model traceability log"
    )
    pipeline_explainability: Optional[PipelineExplainabilitySummary] = Field(
        default=None,
        description="M11 pipeline-wide explainability & counterfactual summary"
    )


class AbstractInverseDesignSearchEngine(ABC):
    """
    Algorithm-neutral abstract interface for inverse-design search algorithms.
    
    Provides pluggable architecture so that candidate search mechanisms can be swapped
    without modifying surrounding scientific evaluation or recommendation pipelines.
    """

    @abstractmethod
    def search(self, optimization_input: OptimizationInputEnvelope) -> ParetoFront:
        """
        Execute search over optimization input envelope and return resulting ParetoFront.
        """
        pass

    @abstractmethod
    def search_with_summary(self, optimization_input: OptimizationInputEnvelope) -> InverseDesignSearchResult:
        """
        Execute search over optimization input envelope and return full InverseDesignSearchResult.
        """
        pass


class DeterministicEnumerationSearchEngine(AbstractInverseDesignSearchEngine):
    """
    M9 Reference Baseline: Deterministic exhaustive candidate enumeration baseline.
    
    This is an algorithm-neutral baseline search mechanism, NOT a final claimed AI optimizer.
    It systematically evaluates every discrete candidate design generated from canonical M5 material evidence,
    enforcing frozen Phase 4 recalculations, Phase 5 hard constraints, M6-B3 objectives, and M6-B4A/B Pareto logic.
    """

    def __init__(self, policy_version: str = "1.0"):
        self.policy_version = policy_version
        self.candidate_evaluator = CandidateScientificEvaluator()
        self.objective_evaluator = ObjectiveEvaluator()
        self.explainability_engine = ExplainabilityEngine()

    def search_with_summary(self, optimization_input: OptimizationInputEnvelope) -> InverseDesignSearchResult:
        """
        Systematically evaluate all eligible candidates in the optimization input envelope.
        """
        start_t = time.perf_counter()
        run_id = optimization_input.optimization_run_id
        base_env = optimization_input.packaging_requirement_envelope
        geometry = optimization_input.package_geometry
        candidates = optimization_input.eligible_candidate_materials

        total_considered = len(candidates)
        feasible_count = 0
        infeasible_count = 0
        unknown_count = 0

        candidate_summaries: List[CandidateEvaluationSummary] = []
        feasible_pareto_candidates: List[ParetoCandidate] = []
        all_warnings: List[str] = list(base_env.all_warnings)
        traceability_list: List[ScientificTraceability] = list(base_env.traceability_log)

        evaluation_records = []

        for cand in candidates:
            # 1. Candidate Scientific Evaluation (Phase 4 recalculation + Phase 5 hard constraints)
            eval_req = CandidateScientificEvaluationRequest(
                candidate=cand,
                base_requirement_envelope=base_env,
                package_geometry=geometry
            )
            eval_res = self.candidate_evaluator.evaluate_candidate(eval_req)
            if eval_res.traceability:
                traceability_list.append(eval_res.traceability)

            # 2. M6-B3 Objective Evaluation
            objs = self.objective_evaluator.evaluate_objectives(cand, eval_res)

            # 3. Categorize Feasibility & Collect Summaries
            status = eval_res.constraint_profile.overall_status

            if status == ConstraintStatus.FEASIBLE:
                feasible_count += 1
            elif status == ConstraintStatus.INFEASIBLE:
                infeasible_count += 1
            else:  # ConstraintStatus.UNKNOWN
                unknown_count += 1

            summary = CandidateEvaluationSummary(
                candidate_id=cand.candidate_id,
                material_id=cand.material_id,
                material_name=cand.material_name,
                total_thickness_um=cand.decision_variables.total_thickness_um or 50.0,
                constraint_status=status.value,
                all_hard_constraints_satisfied=eval_res.constraint_profile.all_hard_constraints_satisfied,
                evaluation_details=eval_res.constraint_profile
            )
            candidate_summaries.append(summary)
            evaluation_records.append((cand, eval_res, objs, summary))
            all_warnings.extend(eval_res.warnings)

            # 4. FEASIBLE Preservation for Pareto Front
            if status == ConstraintStatus.FEASIBLE:
                p_cand = ParetoCandidate(
                    pareto_candidate_id=cand.candidate_id,
                    candidate_design=cand,
                    objective_values=objs,
                    constraint_compliance_summary=eval_res.constraint_profile,
                    uncertainty_profile=eval_res.uncertainty_profile,
                    evidence_tier=EvidenceTier.TIER_3_COLD_START,
                    traceability=base_env.traceability_log[0] if base_env.traceability_log else eval_res.traceability,
                    explanation_payload=ExplanationPayload(
                        trade_off_summary=f"Feasible candidate design {cand.material_name} ({cand.decision_variables.total_thickness_um} µm) satisfies all hard constraints.",
                        limiting_barrier="none",
                        primary_strength=cand.material_name
                    )
                )
                feasible_pareto_candidates.append(p_cand)

        # 5. M6-B4A/B Non-Dominated Pareto Front Construction
        pareto_constructor = ParetoFrontConstructor(run_id=run_id, policy_version=self.policy_version)
        pareto_front = pareto_constructor.construct_front(feasible_pareto_candidates)

        # 6. M11 Explainability & Counterfactual Generation
        explainability_reports = []
        for cand, eval_res, objs, summary in evaluation_records:
            report = self.explainability_engine.generate_candidate_report(
                candidate=cand,
                eval_result=eval_res,
                objectives=objs,
                envelope=base_env,
                pareto_front=pareto_front
            )
            summary.explainability = report
            explainability_reports.append(report)

        pipeline_explainability = self.explainability_engine.generate_pipeline_summary(explainability_reports)

        exec_ms = (time.perf_counter() - start_t) * 1000.0

        pareto_front.solver_metadata = OptimizationMetadata(
            algorithm_name="DETERMINISTIC_EXHAUSTIVE_ENUMERATION_BASELINE",
            iterations_completed=total_considered,
            execution_time_ms=exec_ms,
            cache_hit=False
        )

        unique_warnings = list(dict.fromkeys(all_warnings))
        unique_traceability: List[ScientificTraceability] = []
        seen_models = set()
        for t in traceability_list:
            if t.model_name not in seen_models:
                seen_models.add(t.model_name)
                unique_traceability.append(t)

        return InverseDesignSearchResult(
            optimization_run_id=run_id,
            algorithm_name="DETERMINISTIC_EXHAUSTIVE_ENUMERATION_BASELINE",
            pareto_front=pareto_front,
            candidate_summaries=candidate_summaries,
            total_candidates_considered=total_considered,
            total_candidates_evaluated=total_considered,
            feasible_candidates_count=feasible_count,
            infeasible_candidates_count=infeasible_count,
            unknown_candidates_count=unknown_count,
            execution_time_ms=exec_ms,
            all_warnings=unique_warnings,
            traceability_log=unique_traceability,
            pipeline_explainability=pipeline_explainability
        )

    def search(self, optimization_input: OptimizationInputEnvelope) -> ParetoFront:
        """
        Interface method returning exact ParetoFront object.
        """
        res = self.search_with_summary(optimization_input)
        return res.pareto_front


class IntelligentInverseDesignSearchEngine(AbstractInverseDesignSearchEngine):
    """
    M10 Intelligent Adaptive Inverse-Design Search Engine with M11 Explainability.
    
    Implements an adaptive candidate selection strategy that uses evaluation feedback
    (feasible set progress and current non-dominated Pareto frontier boundaries) to dynamically
    guide candidate evaluation sequence across the authorized candidate search space.
    """

    def __init__(self, policy_version: str = "1.0", max_evaluations: Optional[int] = None):
        self.policy_version = policy_version
        self.max_evaluations = max_evaluations
        self.candidate_evaluator = CandidateScientificEvaluator()
        self.objective_evaluator = ObjectiveEvaluator()
        self.explainability_engine = ExplainabilityEngine()

    def _select_next_candidate(
        self,
        unevaluated: List[PackagingCandidate],
        current_feasible_pareto: List[ParetoCandidate],
        base_env: Any
    ) -> PackagingCandidate:
        """
        Adaptive candidate selection policy using search feedback.
        """
        if not unevaluated:
            raise ValueError("No unevaluated candidates remaining.")

        if not current_feasible_pareto:
            def initial_score(c: PackagingCandidate) -> float:
                wvtr_val = c.barrier_properties.wvtr.value if c.barrier_properties.wvtr else 1e6
                otr_val = c.barrier_properties.otr.value if c.barrier_properties.otr else 1e6
                return wvtr_val + otr_val

            return min(unevaluated, key=initial_score)

        current_thicknesses = [
            p.candidate_design.decision_variables.total_thickness_um
            for p in current_feasible_pareto
            if p.candidate_design.decision_variables.total_thickness_um
        ]

        def frontier_expansion_score(c: PackagingCandidate) -> float:
            c_thick = c.decision_variables.total_thickness_um or 50.0
            thick_dist = min([abs(c_thick - t) for t in current_thicknesses]) if current_thicknesses else 0.0

            c_wvtr = c.barrier_properties.wvtr.value if c.barrier_properties.wvtr else 0.0
            wvtr_dists = [
                abs(c_wvtr - (p.candidate_design.barrier_properties.wvtr.value if p.candidate_design.barrier_properties.wvtr else 0.0))
                for p in current_feasible_pareto
            ]
            avg_wvtr_dist = sum(wvtr_dists) / len(wvtr_dists) if wvtr_dists else 0.0

            return thick_dist + avg_wvtr_dist

        return max(unevaluated, key=frontier_expansion_score)

    def search_with_summary(self, optimization_input: OptimizationInputEnvelope) -> InverseDesignSearchResult:
        """
        Adaptively explore authorized search space and generate M11 explainability report.
        """
        start_t = time.perf_counter()
        run_id = optimization_input.optimization_run_id
        base_env = optimization_input.packaging_requirement_envelope
        geometry = optimization_input.package_geometry
        all_candidates = list(optimization_input.eligible_candidate_materials)

        total_considered = len(all_candidates)
        max_evals = self.max_evaluations
        if max_evals is None and optimization_input.solver_configuration and optimization_input.solver_configuration.max_iterations > 0:
            conf_max = optimization_input.solver_configuration.max_iterations
            max_evals = conf_max if conf_max < total_considered else total_considered
        else:
            max_evals = total_considered if max_evals is None else max_evals

        unevaluated_pool = list(all_candidates)
        evaluated_ids: Set[str] = set()

        feasible_count = 0
        infeasible_count = 0
        unknown_count = 0

        candidate_summaries: List[CandidateEvaluationSummary] = []
        feasible_pareto_candidates: List[ParetoCandidate] = []
        all_warnings: List[str] = list(base_env.all_warnings)
        traceability_list: List[ScientificTraceability] = list(base_env.traceability_log)

        pareto_constructor = ParetoFrontConstructor(run_id=run_id, policy_version=self.policy_version)

        evaluations_completed = 0
        evaluation_records = []

        while unevaluated_pool and evaluations_completed < max_evals:
            next_cand = self._select_next_candidate(unevaluated_pool, feasible_pareto_candidates, base_env)
            unevaluated_pool.remove(next_cand)

            if next_cand.candidate_id in evaluated_ids:
                continue
            evaluated_ids.add(next_cand.candidate_id)
            evaluations_completed += 1

            eval_req = CandidateScientificEvaluationRequest(
                candidate=next_cand,
                base_requirement_envelope=base_env,
                package_geometry=geometry
            )
            eval_res = self.candidate_evaluator.evaluate_candidate(eval_req)
            if eval_res.traceability:
                traceability_list.append(eval_res.traceability)

            objs = self.objective_evaluator.evaluate_objectives(next_cand, eval_res)
            status = eval_res.constraint_profile.overall_status

            if status == ConstraintStatus.FEASIBLE:
                feasible_count += 1
            elif status == ConstraintStatus.INFEASIBLE:
                infeasible_count += 1
            else:
                unknown_count += 1

            summary = CandidateEvaluationSummary(
                candidate_id=next_cand.candidate_id,
                material_id=next_cand.material_id,
                material_name=next_cand.material_name,
                total_thickness_um=next_cand.decision_variables.total_thickness_um or 50.0,
                constraint_status=status.value,
                all_hard_constraints_satisfied=eval_res.constraint_profile.all_hard_constraints_satisfied,
                evaluation_details=eval_res.constraint_profile
            )
            candidate_summaries.append(summary)
            evaluation_records.append((next_cand, eval_res, objs, summary))
            all_warnings.extend(eval_res.warnings)

            if status == ConstraintStatus.FEASIBLE:
                p_cand = ParetoCandidate(
                    pareto_candidate_id=next_cand.candidate_id,
                    candidate_design=next_cand,
                    objective_values=objs,
                    constraint_compliance_summary=eval_res.constraint_profile,
                    uncertainty_profile=eval_res.uncertainty_profile,
                    evidence_tier=EvidenceTier.TIER_3_COLD_START,
                    traceability=base_env.traceability_log[0] if base_env.traceability_log else eval_res.traceability,
                    explanation_payload=ExplanationPayload(
                        trade_off_summary=f"Feasible candidate design {next_cand.material_name} ({next_cand.decision_variables.total_thickness_um} µm) satisfies all hard constraints.",
                        limiting_barrier="none",
                        primary_strength=next_cand.material_name
                    )
                )
                feasible_pareto_candidates.append(p_cand)
                feasible_pareto_candidates = pareto_constructor.filter_non_dominated(feasible_pareto_candidates)

        pareto_front = pareto_constructor.construct_front(feasible_pareto_candidates)

        # M11 Explainability & Counterfactual Generation
        explainability_reports = []
        for cand, eval_res, objs, summary in evaluation_records:
            report = self.explainability_engine.generate_candidate_report(
                candidate=cand,
                eval_result=eval_res,
                objectives=objs,
                envelope=base_env,
                pareto_front=pareto_front
            )
            summary.explainability = report
            explainability_reports.append(report)

        pipeline_explainability = self.explainability_engine.generate_pipeline_summary(explainability_reports)

        exec_ms = (time.perf_counter() - start_t) * 1000.0

        pareto_front.solver_metadata = OptimizationMetadata(
            algorithm_name="ADAPTIVE_PARETO_FRONTIER_SEARCH_ENGINE",
            iterations_completed=evaluations_completed,
            execution_time_ms=exec_ms,
            cache_hit=False
        )

        unique_warnings = list(dict.fromkeys(all_warnings))
        unique_traceability: List[ScientificTraceability] = []
        seen_models = set()
        for t in traceability_list:
            if t.model_name not in seen_models:
                seen_models.add(t.model_name)
                unique_traceability.append(t)

        return InverseDesignSearchResult(
            optimization_run_id=run_id,
            algorithm_name="ADAPTIVE_PARETO_FRONTIER_SEARCH_ENGINE",
            pareto_front=pareto_front,
            candidate_summaries=candidate_summaries,
            total_candidates_considered=total_considered,
            total_candidates_evaluated=evaluations_completed,
            feasible_candidates_count=feasible_count,
            infeasible_candidates_count=infeasible_count,
            unknown_candidates_count=unknown_count,
            execution_time_ms=exec_ms,
            all_warnings=unique_warnings,
            traceability_log=unique_traceability,
            pipeline_explainability=pipeline_explainability
        )

    def search(self, optimization_input: OptimizationInputEnvelope) -> ParetoFront:
        """
        Interface method returning exact ParetoFront object.
        """
        res = self.search_with_summary(optimization_input)
        return res.pareto_front
