# M6-A LATTICE DISCRETIZATION DECISION ANALYSIS

## 1. Decision Status
**PROPOSED ARCHITECTURAL DECISION — AWAITING REVIEW**

## 2. Problem Statement
The M6-A optimization architecture mandates a Tier 1 Precomputed Lattice for candidate recommendations. While M6-A authorizes conceptual dimensions (`commodity`, `target_days`, `temp`, `RH`), it does not mathematically define the physical bin sizes, boundary intervals, and edge-case behavior required to project continuous runtime requests onto a finite discrete grid.

## 3. Existing Authorization
- **Precomputed Lattice (Tier 1)**: AUTHORIZED by M6-A.
- **Dimensions**: `commodity`, `target_shelf_life_days`, `storage_temperature_c`, `relative_humidity_percent` (AUTHORIZED).
- **Interpolation prohibition**: A MISS remains a MISS (AUTHORIZED).

## 4. Missing Contract Decisions
- Continuous-to-discrete interval mappings (UNRESOLVED).
- Physical bin widths/resolutions (UNRESOLVED).
- Domain boundaries (UNRESOLVED).
- Exact behavior at boundaries (UNRESOLVED).
- Out-of-domain behavior (UNRESOLVED).
- Canonical commodity identity handling of variety/product form (UNRESOLVED).

## 5. Design Principles
1. **Computational Scale**: The Cartesian product of bin dimensions must remain bounded.
2. **Scientific Equivalence Prohibition**: A computational lattice bin does NOT establish that all continuous physical states mapped to that bin are scientifically equivalent. The lattice is an indexing/precomputation mechanism. Scientific validity comes from the underlying scientific evaluation and evidence, not from the binning operation.
3. **Pessimistic Safety**: Out-of-domain edge cases must gracefully MISS rather than manufacture false physical safety (clamping/extrapolating).
4. **Original Input Preservation**: Runtime requests MUST retain the original continuous inputs separately from their lattice coordinates.

## 6. Candidate Policy A (Coarse Resolution)
- **Commodity**: Case-insensitive string normalization.
- **Temperature**: $5^\circ\text{C}$ resolution. Domain: $[-5^\circ\text{C}, 30^\circ\text{C}]$. Bins: -5, 0, 5, 10, 15, 20, 25, 30.
- **Relative Humidity**: $10\%$ resolution. Domain: $[40\%, 100\%]$. Bins: 40, 50, 60, 70, 80, 90, 100.
- **Target Shelf Life**: $7\text{-day}$ resolution. Domain: $[7, 91]$. Bins: 7, 14, 21, ..., 91. (13 bins).

## 7. Candidate Policy B (Proposed Architectural Convention)
- **Commodity**: Case-insensitive string normalization.
- **Temperature**: $2^\circ\text{C}$ resolution. Domain: $[-4^\circ\text{C}, 30^\circ\text{C}]$.
- **Relative Humidity**: $5\%$ resolution. Domain: $[50\%, 100\%]$.
- **Target Shelf Life**: $3\text{-day}$ resolution. Domain: $[3, 90]$.

## 8. Candidate Policy C (High Granularity)
- **Commodity**: Case-insensitive string normalization.
- **Temperature**: $1^\circ\text{C}$ resolution. Domain: $[-5^\circ\text{C}, 30^\circ\text{C}]$.
- **Relative Humidity**: $1\%$ resolution. Domain: $[50\%, 100\%]$.
- **Target Shelf Life**: $1\text{-day}$ resolution. Domain: $[1, 90]$.

## 9. Computational Scale Comparison
*Note: 50 commodities is an assumed scenario for scale analysis, not the production commodity registry.*
- **Policy A**: $50 \times 8 \times 7 \times 13 = 36,400$ theoretical coordinates.
- **Policy B**: $50 \times 18 \times 11 \times 30 = 297,000$ theoretical coordinates.
- **Policy C**: $50 \times 36 \times 51 \times 90 = 8,262,000$ theoretical coordinates (substantially larger theoretical coordinate space).

## 10. Scientific Validity Comparison
- **Policy A**: A $5^\circ\text{C}$ temperature bin is proposed to be too coarse for general use, as significant biological variances may occur within a 5-degree range.
- **Policy B**: Proposed engineering trade-off balancing discretization granularity and coordinate count.
- **Policy C**: Granular resolution reduces index aggregation, expanding the coordinate space.

*Note: No policy implies scientific equivalence within a bin.*

## 11. Boundary Comparison
All candidates must define boundary assignments. We propose as an ARCHITECTURAL CONVENTION for Policy B:
- **Intervals**: $[ \text{lower}, \text{upper} )$ 
- **Mapping**: Floor discretization to the explicit interval lower bound.
  - Example: $x \rightarrow \text{floor}((x - \text{min}) / \text{resolution}) \times \text{resolution} + \text{min}$
- **Edge**: The exact absolute maximum falls into an explicit out-of-domain state, or requires defining a closed upper interval for the highest valid bin. (Proposed: $[87, 90]$ is inclusive of 90 for shelf-life).

## 12. Out-of-Domain Comparison
- **Clamp to Nearest**: Rejected. Fails the no-false-science rule.
- **Explicit Reject/MISS**: Proposed convention. If an input is less than the minimum or greater than the maximum supported domain, it triggers a deterministic MISS. It does not silently fall back to Tier 2 unless Tier 2 is explicitly authorized downstream. The lookup itself purely returns a MISS.

## 13. Interpolation Implications
NO INTERPOLATION. Across all policies, a MISS must not silently become nearest-neighbor substitution, linear interpolation, multidimensional interpolation, or weighted averaging unless separately authorized in a future contract.

## 14. Proposed Policy
**Candidate Policy B is selected as the proposed architectural convention** awaiting formal approval. It is not currently an empirically validated scientific resolution.

## 15. Continuous Input Preservation
The architecture MUST preserve the original continuous request.
The lattice coordinate must NOT be represented as though it were the actual measured/runtime physical condition. The system must retain `original_storage_temperature_c` (e.g., 5.9) distinctly from `temperature_coordinate`.

## 16. Unresolved Decisions
- **Commodity Identity**: What exactly identifies the commodity dimension? M6-A uses `commodity`, but `PackagingRequest` also has `variety`, `product_form`, and `ripeness_stage`. Do these collapse into the lattice commodity string, or are they ignored? (UNRESOLVED — REQUIRES ARCHITECTURAL DECISION).
- **Sub-zero Physical States**: Are specific sub-zero physical states technically supported by Phase 4 models? (UNRESOLVED).
- **Numeric Values (Domains and Resolutions)**: The numeric values (e.g., 2°C resolution, [3, 90] shelf life) are PROPOSED CONVENTIONS only, lacking explicit scientific project source authority. (UNRESOLVED).

## 17. Final Decision Matrix

| Decision | Proposed Value | Authority | Status |
|----------|----------------|-----------|--------|
| Commodity Identity | Commodity only | None | UNRESOLVED |
| Commodity Normalization | Case-insensitive string | None | PROPOSED CONVENTION |
| Shelf-Life Domain | [3, 90] days | None | PROPOSED CONVENTION |
| Shelf-Life Resolution | 3 days | None | PROPOSED CONVENTION |
| Shelf-Life Boundary Rule | Interval [lower, upper) | None | PROPOSED CONVENTION |
| Temperature Domain | [-4°C, 30°C] | None | PROPOSED CONVENTION |
| Temperature Resolution | 2°C | None | PROPOSED CONVENTION |
| Temperature Boundary Rule | Interval [lower, upper) | None | PROPOSED CONVENTION |
| RH Domain | [50%, 100%] | None | PROPOSED CONVENTION |
| RH Resolution | 5% | None | PROPOSED CONVENTION |
| RH Boundary Rule | Interval [lower, upper) | None | PROPOSED CONVENTION |
| Discretization Function | Floor to grid interval | None | PROPOSED CONVENTION |
| Out-of-Domain Behavior | Deterministic MISS | M6-A | PROPOSED CONVENTION |
| Original-Input Preservation| Retain separately | None | PROPOSED CONVENTION |
| Interpolation Behavior | NO INTERPOLATION | M6-A | AUTHORIZED |
| Lattice Versioning | Invalidate on domain/bin change | None | PROPOSED CONVENTION |

## 18. M6-B5 Gating Conditions
Policy B is a proposed architectural convention awaiting formal approval. 

**M6-A POLICY B NOT READY — UNRESOLVED ARCHITECTURAL DECISIONS**
