import pytest
from app.schemas.physics import CalculationStatus
from scientific_engine.physics.microbial import MicrobialGrowthModel


def test_microbial_growth_with_complete_evidence() -> None:
    model = MicrobialGrowthModel()
    # N0 = 2.0 log CFU/g, Ncrit = 6.0 log CFU/g, mu = 0.8 /day, lag = 1.0 day
    # delta_log = 4.0. log10_rate = 0.8 / ln(10) ≈ 0.3474 log/day
    # t_microbial = 1.0 + (4.0 / 0.3474) ≈ 1.0 + 11.51 = 12.51 days
    req = model.calculate_microbial_limits(
        target_microorganism="Pseudomonas spp.",
        initial_count_log_cfu=2.0,
        critical_count_log_cfu=6.0,
        growth_rate_per_day=0.8,
        lag_time_days=1.0,
        temperature_c=4.0,
    )
    assert req.status == CalculationStatus.CALCULATED
    assert req.microbial_shelf_life_days is not None
    assert abs(req.microbial_shelf_life_days.value - 12.5) < 0.2
    assert "Baranyi" in req.traceability.equation_reference


def test_microbial_growth_with_ratkowsky_temperature_model() -> None:
    model = MicrobialGrowthModel()
    # Ratkowsky model: sqrt(mu) = 0.05 * (T - (-2.0))
    # At T = 8.0 °C: sqrt(mu) = 0.05 * 10 = 0.5 => mu = 0.25 /day
    req = model.calculate_microbial_limits(
        target_microorganism="Listeria monocytogenes",
        initial_count_log_cfu=1.0,
        critical_count_log_cfu=3.0,
        temperature_c=8.0,
        ratkowsky_b=0.05,
        ratkowsky_tmin_c=-2.0,
        lag_time_days=2.0,
    )
    assert req.status == CalculationStatus.CALCULATED
    assert req.growth_rate_per_day is not None
    assert abs(req.growth_rate_per_day.value - 0.25) < 0.001


def test_microbial_growth_missing_organism_returns_unknown() -> None:
    model = MicrobialGrowthModel()
    req = model.calculate_microbial_limits(
        target_microorganism=None,
    )
    assert req.status == CalculationStatus.UNKNOWN
    assert req.microbial_shelf_life_days is None
    assert any("UNKNOWN" in w for w in req.warnings)


def test_microbial_growth_with_co2_inhibition_factor() -> None:
    model = MicrobialGrowthModel()
    # With 0.5 inhibition factor, growth rate should be halved
    req = model.calculate_microbial_limits(
        target_microorganism="Aerobic Plate Count",
        initial_count_log_cfu=2.0,
        critical_count_log_cfu=6.0,
        growth_rate_per_day=1.0,
        co2_inhibition_factor=0.5,
    )
    assert req.status == CalculationStatus.CALCULATED
    assert req.growth_rate_per_day is not None
    assert abs(req.growth_rate_per_day.value - 0.5) < 0.001
