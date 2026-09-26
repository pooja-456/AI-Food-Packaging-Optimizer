"""
Moisture Sorption Isotherm Model Abstractions.

Provides sorption models (GAB, Oswin, Halsey, Linear) to relate food moisture
content (g H2O / 100g dry solids) with equilibrium water activity (aw).

Models are evidence-gated: they are ONLY executed when verified parameters and
applicability conditions exist.
"""

from abc import ABC, abstractmethod
import math
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.physics import CalculationStatus, ScientificResult
from scientific_engine.physics.applicability import validate_water_activity
from scientific_engine.physics.traceability import make_traceability


class MoistureSorptionModel(ABC):
    """Abstract base class for food moisture sorption isotherm models."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @abstractmethod
    def calculate_moisture_content(
        self,
        water_activity: float,
        temperature_c: Optional[float] = None,
    ) -> ScientificResult:
        """Calculate equilibrium dry-basis moisture content (g H2O / 100g dry solids) at a given aw."""
        pass


class GABModel(MoistureSorptionModel):
    """
    Guggenheim-Anderson-de Boer (GAB) Isotherm Model.

    Equation:
        m(aw) = (m0 * C * K * aw) / [(1 - K * aw) * (1 - K * aw + C * K * aw)]

    Parameters:
        m0 = Monolayer moisture content (g H2O / 100g dry solids)
        C = Guggenheim energy constant related to monolayer heat of sorption
        K = Factor correcting properties of multilayer molecules relative to bulk liquid

    Scientific Source:
        - van den Berg, C. (1984). Description of water activity of foods for engineering purposes
          by means of the GAB model of sorption. Engineering and Food, 1, 311-321.
        - Bizot, H. (1983). Using the G.A.B. model to construct sorption isotherms.
          In Physical Properties of Foods (pp. 43-54). Applied Science Publishers.

    Validity:
        aw in [0.05, 0.90], 0 < K <= 1, C > 0.
    """

    def __init__(
        self,
        m0: float,
        c: float,
        k: float,
        parameter_source: str = "literature",
        applicable_temperature_range: Tuple[float, float] = (0.0, 40.0),
    ) -> None:
        self.m0 = m0
        self.c = c
        self.k = k
        self.parameter_source = parameter_source
        self.temp_range = applicable_temperature_range

    @property
    def model_name(self) -> str:
        return "GABMoistureSorptionModel"

    def calculate_moisture_content(
        self,
        water_activity: float,
        temperature_c: Optional[float] = None,
    ) -> ScientificResult:
        warnings: List[str] = []
        warnings.extend(validate_water_activity(water_activity, model_name=self.model_name))

        if water_activity < 0.05 or water_activity > 0.90:
            warnings.append(
                f"[GAB] Water activity aw = {water_activity:.2f} is outside recommended GAB validity [0.05, 0.90]."
            )

        if not (0.0 < self.k <= 1.0) or self.c <= 0:
            return ScientificResult(
                status=CalculationStatus.UNKNOWN,
                traceability=make_traceability(
                    model_name=self.model_name,
                    equation_form="m(aw) = (m0 * C * K * aw) / [(1 - K * aw) * (1 - K * aw + C * K * aw)]",
                    failure_or_unknown_reason=f"Thermodynamically invalid GAB parameters: K={self.k}, C={self.c}.",
                    warnings=warnings,
                ),
            )

        denom1 = 1.0 - (self.k * water_activity)
        denom2 = 1.0 - (self.k * water_activity) + (self.c * self.k * water_activity)
        denominator = denom1 * denom2

        if denominator <= 0:
            return ScientificResult(
                status=CalculationStatus.UNKNOWN,
                traceability=make_traceability(
                    model_name=self.model_name,
                    equation_form="m(aw) = (m0 * C * K * aw) / [(1 - K * aw) * (1 - K * aw + C * K * aw)]",
                    failure_or_unknown_reason="Denominator evaluated to zero or negative.",
                    warnings=warnings,
                ),
            )

        m_calc = (self.m0 * self.c * self.k * water_activity) / denominator

        trace = make_traceability(
            model_name=self.model_name,
            equation_form="m(aw) = (m0 * C * K * aw) / [(1 - K * aw) * (1 - K * aw + C * K * aw)]",
            equation_reference="van den Berg (1984) Engineering and Food 1:311-321",
            scientific_sources=["Bizot, H. (1983) Physical Properties of Foods pp. 43-54"],
            inputs_used={"water_activity": water_activity, "temperature_c": temperature_c},
            parameters_used={"m0": self.m0, "C": self.c, "K": self.k},
            parameter_sources={"GAB_parameters": self.parameter_source},
            units_used={"m": "g H2O / 100g dry solids", "m0": "g H2O / 100g dry solids", "C": "dimensionless", "K": "dimensionless"},
            validity_range={"water_activity": (0.05, 0.90), "temperature_c": self.temp_range},
            assumptions=["Multilayer localized physical adsorption obeying GAB thermodynamics."],
            warnings=warnings,
        )

        return ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=round(m_calc, 3),
            unit="g H2O / 100g dry solids",
            traceability=trace,
        )


class OswinModel(MoistureSorptionModel):
    """
    Oswin Isotherm Model.

    Equation:
        m(aw) = a * [aw / (1 - aw)]^b

    Scientific Source:
        Oswin, C. R. (1946). The kinetics of package life. III. The isotherm.
        Journal of the Chemical Industry, 65(12), 419-421.
    """

    def __init__(self, a: float, b: float, parameter_source: str = "literature") -> None:
        self.a = a
        self.b = b
        self.parameter_source = parameter_source

    @property
    def model_name(self) -> str:
        return "OswinMoistureSorptionModel"

    def calculate_moisture_content(
        self,
        water_activity: float,
        temperature_c: Optional[float] = None,
    ) -> ScientificResult:
        warnings = validate_water_activity(water_activity, model_name=self.model_name)
        if water_activity >= 1.0 or water_activity <= 0.0:
            return ScientificResult(
                status=CalculationStatus.UNKNOWN,
                traceability=make_traceability(
                    model_name=self.model_name,
                    equation_form="m(aw) = a * [aw / (1 - aw)]^b",
                    failure_or_unknown_reason=f"Water activity aw={water_activity} at asymptote.",
                    warnings=warnings,
                ),
            )

        ratio = water_activity / (1.0 - water_activity)
        m_calc = self.a * math.pow(ratio, self.b)

        trace = make_traceability(
            model_name=self.model_name,
            equation_form="m(aw) = a * [aw / (1 - aw)]^b",
            equation_reference="Oswin, C. R. (1946) J. Soc. Chem. Ind. 65:419-421",
            inputs_used={"water_activity": water_activity},
            parameters_used={"a": self.a, "b": self.b},
            parameter_sources={"Oswin_params": self.parameter_source},
            units_used={"m": "g H2O / 100g dry solids"},
            assumptions=["Empirical sigmoidal sorption isotherm."],
            warnings=warnings,
        )
        return ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=round(m_calc, 3),
            unit="g H2O / 100g dry solids",
            traceability=trace,
        )


class HalseyModel(MoistureSorptionModel):
    """
    Halsey Isotherm Model.

    Equation:
        m(aw) = [-a / ln(aw)]^(1/b)

    Scientific Source:
        Halsey, G. (1948). Physical adsorption on non-uniform surfaces.
        Journal of Chemical Physics, 16(10), 931-937.
    """

    def __init__(self, a: float, b: float, parameter_source: str = "literature") -> None:
        self.a = a
        self.b = b
        self.parameter_source = parameter_source

    @property
    def model_name(self) -> str:
        return "HalseyMoistureSorptionModel"

    def calculate_moisture_content(
        self,
        water_activity: float,
        temperature_c: Optional[float] = None,
    ) -> ScientificResult:
        warnings = validate_water_activity(water_activity, model_name=self.model_name)
        if water_activity <= 0.0 or water_activity >= 1.0:
            return ScientificResult(
                status=CalculationStatus.UNKNOWN,
                traceability=make_traceability(
                    model_name=self.model_name,
                    equation_form="m(aw) = [-a / ln(aw)]^(1/b)",
                    failure_or_unknown_reason=f"Water activity aw={water_activity} outside logarithmic domain (0, 1).",
                    warnings=warnings,
                ),
            )

        val = -self.a / math.log(water_activity)
        if val <= 0:
            return ScientificResult(
                status=CalculationStatus.UNKNOWN,
                traceability=make_traceability(
                    model_name=self.model_name,
                    equation_form="m(aw) = [-a / ln(aw)]^(1/b)",
                    failure_or_unknown_reason="Negative term under fractional power.",
                    warnings=warnings,
                ),
            )

        m_calc = math.pow(val, 1.0 / self.b)
        trace = make_traceability(
            model_name=self.model_name,
            equation_form="m(aw) = [-a / ln(aw)]^(1/b)",
            equation_reference="Halsey, G. (1948) J. Chem. Phys. 16:931-937",
            inputs_used={"water_activity": water_activity},
            parameters_used={"a": self.a, "b": self.b},
            parameter_sources={"Halsey_params": self.parameter_source},
            units_used={"m": "g H2O / 100g dry solids"},
            assumptions=["Multilayer adsorption on non-uniform surface energy distribution."],
            warnings=warnings,
        )
        return ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=round(m_calc, 3),
            unit="g H2O / 100g dry solids",
            traceability=trace,
        )


class LinearLowAwModel(MoistureSorptionModel):
    """
    Linear Sorption Model for low-moisture dry foods in the Henry's law / low-aw regime.

    Equation:
        m(aw) = slope * aw + m0
    """

    def __init__(self, slope: float, m0: float = 0.0, parameter_source: str = "literature") -> None:
        self.slope = slope
        self.m0 = m0
        self.parameter_source = parameter_source

    @property
    def model_name(self) -> str:
        return "LinearLowAwSorptionModel"

    def calculate_moisture_content(
        self,
        water_activity: float,
        temperature_c: Optional[float] = None,
    ) -> ScientificResult:
        warnings = validate_water_activity(water_activity, model_name=self.model_name)
        if water_activity > 0.45:
            warnings.append(f"[LinearLowAw] Water activity aw={water_activity:.2f} exceeds linear regime (aw <= 0.45).")

        m_calc = self.slope * water_activity + self.m0
        trace = make_traceability(
            model_name=self.model_name,
            equation_form="m(aw) = slope * aw + m0",
            equation_reference="Labuza, T. P. (1984) Moisture Sorption: Practical Aspects of Isotherm Measurement",
            inputs_used={"water_activity": water_activity},
            parameters_used={"slope": self.slope, "m0": self.m0},
            parameter_sources={"Linear_params": self.parameter_source},
            units_used={"m": "g H2O / 100g dry solids"},
            assumptions=["Linearized moisture sorption in low water activity region."],
            warnings=warnings,
        )
        return ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=round(m_calc, 3),
            unit="g H2O / 100g dry solids",
            traceability=trace,
        )
