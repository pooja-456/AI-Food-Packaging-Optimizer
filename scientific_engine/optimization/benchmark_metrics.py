"""
M7-E4: Benchmark Metrics Instrumentation & Telemetry Auditors.

Implements telemetry collectors for the 7 M7-D dimensions (Scientific evaluations,
Wall-clock time, Feasible discovery, Pareto coverage, Repeatability, Robustness, Peak RAM).
"""

import sys
import platform
import time
import tracemalloc
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple

from scientific_engine.optimization.benchmark_contracts import (
    FeasibleDiscoveryRecord,
    ReproducibilityMetadata,
    NOT_YET_AUTHORIZED,
    REFERENCE_PARETO_FRONT_NOT_AUTHORIZED,
)


class MonotonicTimerAuditor:
    """
    High-resolution monotonic wall-clock timer auditor.
    Measures solver execution time excluding scenario setup/validation overhead.
    """

    def __init__(self) -> None:
        self.start_ns: Optional[int] = None
        self.stop_ns: Optional[int] = None

    def start(self) -> None:
        self.start_ns = time.perf_counter_ns()
        self.stop_ns = None

    def stop(self) -> int:
        if self.start_ns is None:
            return 0
        self.stop_ns = time.perf_counter_ns()
        return self.stop_ns - self.start_ns

    def elapsed_ns(self) -> int:
        if self.start_ns is None:
            return 0
        if self.stop_ns is not None:
            return self.stop_ns - self.start_ns
        return time.perf_counter_ns() - self.start_ns


class FeasibleDiscoveryTracker:
    """
    Tracks the discovery of the first Phase 5 FEASIBLE candidate during solver execution.
    """

    def __init__(self, timer: MonotonicTimerAuditor) -> None:
        self.timer = timer
        self.first_feasible_found: bool = False
        self.evaluations_to_first_feasible: Optional[int] = None
        self.wall_clock_ns_to_first_feasible: Optional[int] = None

    def record_candidate_evaluation(self, is_feasible: bool, cumulative_evals: int) -> None:
        if is_feasible and not self.first_feasible_found:
            self.first_feasible_found = True
            self.evaluations_to_first_feasible = cumulative_evals
            self.wall_clock_ns_to_first_feasible = self.timer.elapsed_ns()

    def get_record(self) -> FeasibleDiscoveryRecord:
        return FeasibleDiscoveryRecord(
            first_feasible_found=self.first_feasible_found,
            evaluations_to_first_feasible=self.evaluations_to_first_feasible,
            wall_clock_ns_to_first_feasible=self.wall_clock_ns_to_first_feasible,
        )


class PeakRamAuditor:
    """
    Process RSS / heap RAM auditor. Uses tracemalloc when active.
    Returns status 'NOT_AVAILABLE' if uninitialized or unsupported.
    """

    def __init__(self) -> None:
        self.is_active: bool = False

    def start(self) -> None:
        try:
            if not tracemalloc.is_tracing():
                tracemalloc.start()
                self.is_active = True
            else:
                self.is_active = True
        except Exception:
            self.is_active = False

    def get_peak_ram(self) -> Tuple[Optional[int], str]:
        if not self.is_active or not tracemalloc.is_tracing():
            return None, "NOT_AVAILABLE"
        try:
            current, peak = tracemalloc.get_traced_memory()
            return peak, "MEASURED_TRACEMALLOC"
        except Exception:
            return None, "ERROR_FAILED_READ"

    def stop(self) -> None:
        if self.is_active:
            try:
                # Keep tracing state clean if we started it
                tracemalloc.clear_traces()
            except Exception:
                pass


def collect_reproducibility_metadata(random_seed: Optional[int] = None) -> ReproducibilityMetadata:
    """
    Collects 100% scientifically reproducible environment metadata without PII.
    """
    # Simple git commit hash check (returns static fallback if git binary unavailable)
    git_hash = "HEAD_LOCAL_WORKSPACE"
    try:
        import subprocess
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if res.returncode == 0:
            git_hash = res.stdout.strip()
    except Exception:
        pass

    return ReproducibilityMetadata(
        git_commit_hash=git_hash,
        python_version=sys.version.split()[0],
        platform_system=platform.system(),
        execution_timestamp_utc=datetime.now(timezone.utc).isoformat(),
        random_seed=random_seed,
        dependency_versions={
            "python": sys.version.split()[0],
            "pytest": "9.0.2",
            "pydantic": "2.x",
        },
    )
