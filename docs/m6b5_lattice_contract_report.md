# M6-B5: Optimization Lattice Contract & Design Report

**Project**: AI-Based Intelligent Food Packaging Material Recommendation System
**Milestone**: M6-B5
**Date**: 2026-09-29

## 1. Purpose
Define the schema, coordinate logic, and storage interface boundary for the Tier 1 Optimization Lattice without actually writing to persistence or precomputing instances. It explicitly designs the mapping between a continuous runtime food packaging request and an identical precomputed discrete optimization run.

## 2. Relationship to M6-A
This milestone fulfills the interface specification defined in M6-A ("Tier 1: Precomputed Lattice / Instant Cache Lookup"), constructing formal logical barriers between what constitutes a request and what is queried.

## 3. Lattice-Point Definition
A `LatticePoint` connects a `LatticeCoordinate` directly to a formally evaluated `ParetoFront`. It is a strict 1-to-1 mapping. No mathematical adjustments (like interpolations) occur within the point itself.

## 4. Authorized Dimensions
According to M6-A, the permitted dimensions bounding the lattice structure are strictly limited to:
- **commodity**: (String)
- **target_days**: (Integer shelf-life bin)
- **temp**: (Float bin in °C)
- **RH**: (Float bin for relative humidity %)

Cost bounds, user utility, or geometric boundaries were not formally authorized as lookup dimensions for Tier 1.

## 5. Discretization
The contract defines explicit variables (e.g. `storage_temperature_c_bin`) meant to safely store the bounded center of the grid location, while preserving continuous inputs (`original_storage_temperature_c`) on the lookup result. A request at $4.8^\circ\text{C}$ hitting a $5.0^\circ\text{C}$ node guarantees that both origin and lookup values are formally recorded in the response.

## 6. Canonical Key
The deterministic lookup key (`canonical_key`) serializes the precise coordinate fields (lowercasing strings, rounding floats to two decimals, and sorting keys) before applying a SHA-256 hash. This guarantees cross-language stability and complete independence from UUIDs or database sequence IDs.

## 7. Pareto-Front Representation
The existing `ParetoFront` schema is utilized identically. A `LatticePoint` literally houses the full unmodified `ParetoFront` produced by M6-B4B, containing the complete mathematical subset without attempting to filter it to a "Top 3".

## 8. Uncertainty
No logic for reducing interval uncertainty was introduced. All structures preserve exact intervals inside the attached Pareto candidates.

## 9. Feasibility
The precomputed grid does not upgrade `UNKNOWN` properties. A `LatticePoint` stores candidates evaluated by M6-B3/B4; thus, ineligible constraints remain securely rejected from the precomputed space.

## 10. Provenance
Every object retains full M5 evidence identifiers and Phase 4 model traceability within the `ParetoFront`.

## 11. Versioning
A `LatticeMetadata` schema was created linking:
- `lattice_version`
- `physics_model_version`
- `evidence_database_version`
to ensure runtime applications can distinguish outdated computations from refreshed data models.

## 12. HIT/MISS Semantics
A clear `LatticeLookupStatus` enumeration defines `HIT` and `MISS`. A `MISS` leaves the matched coordinate and Pareto front explicitly `None`. It does not invent or extrapolate a "closest" front. 

## 13. Storage Boundary
The system defines the standard Pydantic models needed to translate between runtime engines and whatever caching mechanism (e.g., PostgreSQL JSONB, Redis, file-store) will be developed in M6-B6/M6-C.

## 14. Runtime Boundary
The contract supports an input pipeline extracting fields from `PackagingRequest`, executing coordinate binning logic (which will be implemented later), hashing a `canonical_key`, and querying the data store.

## 15. Future Integration
The models seamlessly integrate with the Tier 2 "Warm-Start Optimization" pipeline, which can selectively query neighbors by manipulating coordinate bins if exact hits fail.

## 16. Explicit Non-Goals
I explicitly confirm that NO lattice population generation, caching systems, nearest-neighbor searches, interpolations, ML surrogates, database operations, or API layers were developed.

## 17. Tests
Tests implemented in `backend/tests/test_lattice_contract.py`:
- `test_lattice_coordinate_deterministic_key`: Stability across spaces.
- `test_different_coordinate_different_key`: Collision proof.
- `test_lattice_point_preserves_pareto_front`: Schema nesting safety.
- `test_lattice_lookup_result_preserves_original_values`: Preserves continuous vs discrete variables.
- `test_lattice_lookup_miss`: Graceful rejection structures.

## 18. Known Limitations
Continuous-to-discrete mappings (the actual binning algorithms determining *how* $4.8$ becomes $5.0$) are left to the implementation phase. The contracts only define the schema capacity to store them safely.
