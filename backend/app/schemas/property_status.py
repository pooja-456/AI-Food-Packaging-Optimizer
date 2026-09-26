from enum import Enum
from typing import Optional
from pydantic import BaseModel


class PropertyStatusEnum(str, Enum):
    measured = "measured"
    literature = "literature"
    inferred = "inferred"
    unknown = "unknown"


class PropertyStatus(BaseModel):
    """
    Reusable representation for a single scientific property value.

    status reflects the origin of the value:
      - measured:   obtained by direct laboratory measurement
      - literature: taken from a published scientific source
      - inferred:   estimated by a model or rule
      - unknown:    no value is available
    """

    property: str
    value: Optional[float] = None
    unit: Optional[str] = None
    status: PropertyStatusEnum = PropertyStatusEnum.unknown
    source: Optional[str] = None
    confidence: Optional[float] = None
    uncertainty_range: Optional[tuple[float, float]] = None
    acquisition_method: Optional[str] = None
