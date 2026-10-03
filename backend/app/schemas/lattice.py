"""
M6-B5: Optimization Lattice Contract.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import hashlib
import json

from app.schemas.optimization import ParetoFront

class LatticeLookupStatus(str, Enum):
    HIT = "HIT"
    MISS = "MISS"

class LatticeCoordinate(BaseModel):
    """
    The discretized dimensions defining a precomputed optimization state,
    as authorized by the M6-A contract (commodity, target_days, temp, RH).
    """
    commodity: str = Field(..., description="Canonical commodity name.")
    target_shelf_life_days_bin: int = Field(..., description="Discretized shelf-life target.")
    storage_temperature_c_bin: float = Field(..., description="Discretized storage temperature.")
    relative_humidity_percent_bin: float = Field(..., description="Discretized relative humidity.")

    @property
    def canonical_key(self) -> str:
        """
        Deterministic serialization of the coordinate.
        Produces a unique, stable hash for lookup.
        """
        data = {
            "commodity": self.commodity.strip().lower(),
            "target_shelf_life_days_bin": self.target_shelf_life_days_bin,
            "storage_temperature_c_bin": round(self.storage_temperature_c_bin, 2),
            "relative_humidity_percent_bin": round(self.relative_humidity_percent_bin, 2)
        }
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

class LatticeMetadata(BaseModel):
    """
    Metadata for versioning the precomputed lattice.
    """
    lattice_version: str = Field(..., description="Version of the lattice discretization design.")
    physics_model_version: str = Field(..., description="Version of the Phase 4 physics engine.")
    evidence_database_version: str = Field(..., description="Version/timestamp of the M5 evidence database.")

class LatticePoint(BaseModel):
    """
    A single node in the precomputed lattice, permanently tying a discretized coordinate 
    to the formally evaluated Pareto front.
    """
    coordinate: LatticeCoordinate
    canonical_key: str
    pareto_front: ParetoFront
    metadata: LatticeMetadata
    
class LatticeLookupResult(BaseModel):
    """
    The result of querying the lattice. Explicitly preserves the distinction 
    between the original continuous request and the discretized coordinate.
    """
    status: LatticeLookupStatus
    original_commodity: str
    original_target_shelf_life_days: int
    original_storage_temperature_c: float
    original_relative_humidity_percent: float
    matched_coordinate: Optional[LatticeCoordinate] = None
    pareto_front: Optional[ParetoFront] = None
